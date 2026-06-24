from __future__ import annotations

import json

from automation.forex_engine.oanda_demo_read_only_filled_trade_pl_capture_v1 import (
    ACCESS_TOKEN_CREDENTIAL_NAME,
    ACCOUNT_ID_CREDENTIAL_NAME,
    BLOCKED_BY_READ_ONLY_PL_CAPTURE_FAILURE,
    FILLED_TRADE_PL_OPEN_UNREALIZED,
    FILLED_TRADE_PL_POSITIVE,
    PRACTICE_API_BASE_URL,
    READ_ONLY_FILLED_TRADE_PL_CAPTURE_READY,
    evaluate_oanda_demo_read_only_filled_trade_pl_capture_v1,
    validate_oanda_demo_read_only_filled_trade_pl_capture_endpoint_url_v1,
)
from scripts.forex_delivery.run_oanda_demo_read_only_filled_trade_pl_capture_v1 import (
    main,
)


RUNTIME_TOKEN = "owner-runtime-token-value"
RUNTIME_ACCOUNT_ID = "owner-runtime-account-id"


def test_default_capture_is_ready_without_vault_or_network() -> None:
    decision = evaluate_oanda_demo_read_only_filled_trade_pl_capture_v1()

    assert decision["status"] == READ_ONLY_FILLED_TRADE_PL_CAPTURE_READY
    assert decision["broker_network_call_performed"] is False
    assert decision["credential_read_performed"] is False
    assert decision["order_placement_performed"] is False
    assert decision["order_close_performed"] is False
    assert decision["live_endpoint_used"] is False


def test_endpoint_validator_allows_only_practice_get_allowlist() -> None:
    allowed = [
        f"{PRACTICE_API_BASE_URL}/v3/accounts",
        f"{PRACTICE_API_BASE_URL}/v3/accounts/{RUNTIME_ACCOUNT_ID}",
        f"{PRACTICE_API_BASE_URL}/v3/accounts/{RUNTIME_ACCOUNT_ID}/summary",
        f"{PRACTICE_API_BASE_URL}/v3/accounts/{RUNTIME_ACCOUNT_ID}/openTrades",
        f"{PRACTICE_API_BASE_URL}/v3/accounts/{RUNTIME_ACCOUNT_ID}/openPositions",
        (
            f"{PRACTICE_API_BASE_URL}/v3/accounts/"
            f"{RUNTIME_ACCOUNT_ID}/transactions?from=319&to=322"
        ),
    ]

    for url in allowed:
        assert (
            validate_oanda_demo_read_only_filled_trade_pl_capture_endpoint_url_v1(url)
            == []
        )

    assert "method_must_be_get" in (
        validate_oanda_demo_read_only_filled_trade_pl_capture_endpoint_url_v1(
            allowed[0],
            method="POST",
        )
    )
    assert "url_must_use_oanda_practice_base" in (
        validate_oanda_demo_read_only_filled_trade_pl_capture_endpoint_url_v1(
            "https://api-fxtrade.oanda.com/v3/accounts",
        )
    )
    assert "orders_endpoint_forbidden" in (
        validate_oanda_demo_read_only_filled_trade_pl_capture_endpoint_url_v1(
            f"{PRACTICE_API_BASE_URL}/v3/accounts/{RUNTIME_ACCOUNT_ID}/orders",
        )
    )


def test_execute_capture_classifies_open_unrealized_and_redacts_runtime_values() -> None:
    calls: list[dict] = []

    def fake_vault(payload: dict) -> dict:
        if payload["credential_name"] == ACCESS_TOKEN_CREDENTIAL_NAME:
            return {"secret_value": RUNTIME_TOKEN}
        if payload["credential_name"] == ACCOUNT_ID_CREDENTIAL_NAME:
            return {"secret_value": RUNTIME_ACCOUNT_ID}
        return {"secret_value": ""}

    def fake_http_get(payload: dict) -> dict:
        calls.append(payload)
        endpoint_name = payload["endpoint_name"]
        if endpoint_name == "account_summary":
            body = {
                "account": {
                    "id": RUNTIME_ACCOUNT_ID,
                    "balance": "1000.00",
                    "NAV": "1000.01",
                    "unrealizedPL": "0.01",
                }
            }
        elif endpoint_name == "open_trades":
            body = {
                "trades": [
                    {
                        "id": "777",
                        "instrument": "EUR_USD",
                        "currentUnits": "1",
                        "unrealizedPL": "0.01",
                    }
                ]
            }
        elif endpoint_name == "open_positions":
            body = {
                "positions": [
                    {
                        "instrument": "EUR_USD",
                        "long": {"units": "1"},
                        "short": {"units": "0"},
                        "unrealizedPL": "0.01",
                    }
                ]
            }
        elif endpoint_name == "transactions_window":
            body = {
                "transactions": [
                    {"id": "319", "type": "MARKET_ORDER"},
                    {"id": "320", "type": "ORDER_FILL"},
                ]
            }
        else:
            body = {"account": {"id": RUNTIME_ACCOUNT_ID}}
        return {"status_code": 200, "json": body}

    decision = evaluate_oanda_demo_read_only_filled_trade_pl_capture_v1(
        vault_load_callable=fake_vault,
        http_get_callable=fake_http_get,
        execute_capture=True,
    )

    assert decision["pl_capture_classification"] == FILLED_TRADE_PL_OPEN_UNREALIZED
    assert decision["broker_network_call_performed"] is True
    assert decision["order_placement_performed"] is False
    assert len(calls) == 6
    assert {call["method"] for call in calls} == {"GET"}
    assert all(call["url"].startswith(PRACTICE_API_BASE_URL) for call in calls)
    serialized = json.dumps(decision, sort_keys=True)
    assert RUNTIME_TOKEN not in serialized
    assert RUNTIME_ACCOUNT_ID not in serialized


def test_execute_capture_classifies_positive_realized_pl() -> None:
    def fake_vault(payload: dict) -> dict:
        values = {
            ACCESS_TOKEN_CREDENTIAL_NAME: RUNTIME_TOKEN,
            ACCOUNT_ID_CREDENTIAL_NAME: RUNTIME_ACCOUNT_ID,
        }
        return {"secret_value": values.get(payload["credential_name"], "")}

    def fake_http_get(payload: dict) -> dict:
        if payload["endpoint_name"] == "transactions_window":
            body = {
                "transactions": [
                    {
                        "id": "320",
                        "type": "ORDER_FILL",
                        "pl": "0.02",
                    }
                ]
            }
        else:
            body = {"account": {"id": RUNTIME_ACCOUNT_ID}}
        return {"status_code": 200, "json": body}

    decision = evaluate_oanda_demo_read_only_filled_trade_pl_capture_v1(
        vault_load_callable=fake_vault,
        http_get_callable=fake_http_get,
        execute_capture=True,
    )

    assert decision["pl_capture_classification"] == FILLED_TRADE_PL_POSITIVE
    assert decision["profit_claimed"] is False


def test_script_template_prints_sanitized_json(capsys) -> None:
    exit_code = main(["--print-template"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    assert payload["broker_network_call_performed"] is False
    assert payload["credential_read_performed"] is False
    assert payload["runtime_input_rule"]["command_line_token_argument_supported"] is False
    assert payload["runtime_input_rule"]["command_line_account_id_argument_supported"] is False


def test_script_execute_without_confirmations_blocks_before_vault(capsys) -> None:
    def fail_if_called(payload: dict) -> dict:
        raise AssertionError("vault or network must not be called")

    exit_code = main(
        ["--execute-read-only-filled-trade-pl-capture-from-vault"],
        vault_load_callable=fail_if_called,
        http_get_callable=fail_if_called,
    )

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 1
    assert payload["script_status"] == "BLOCKED_MISSING_REQUIRED_CONFIRMATIONS"
    assert payload["broker_network_call_performed"] is False
    assert payload["credential_read_performed"] is False
    assert payload["decision"]["pl_capture_classification"] is None
