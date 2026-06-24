from __future__ import annotations

import json

from automation.forex_engine.oanda_demo_vault_backed_one_order_transport_v1 import (
    ACCESS_TOKEN_CREDENTIAL_NAME,
    ACCOUNT_ID_CREDENTIAL_NAME,
    BLOCKED_BY_LIVE_ENDPOINT,
    BLOCKED_BY_MISSING_STOP_LOSS,
    BLOCKED_BY_MISSING_VAULT_CREDENTIALS,
    BLOCKED_BY_PROFIT_CLAIM,
    VAULT_BACKED_DEMO_ONE_ORDER_ATTEMPTED,
    VAULT_BACKED_DEMO_ONE_ORDER_READY_FOR_OWNER_RUN,
    evaluate_oanda_demo_vault_backed_one_order_transport_v1,
)
from scripts.forex_delivery.run_oanda_demo_vault_backed_one_order_transport_v1 import (
    main,
)


def test_ready_state_does_not_load_vault_or_call_transport() -> None:
    vault_calls: list[dict] = []
    transport_calls: list[dict] = []

    decision = evaluate_oanda_demo_vault_backed_one_order_transport_v1(
        _valid_context(),
        vault_load_callable=lambda payload: vault_calls.append(payload),
        http_post_callable=lambda payload: transport_calls.append(payload),
        execute_transport=False,
    )

    assert decision["status"] == VAULT_BACKED_DEMO_ONE_ORDER_READY_FOR_OWNER_RUN
    assert decision["credential_read_performed"] is False
    assert decision["account_id_read_performed"] is False
    assert decision["broker_network_call_performed"] is False
    assert vault_calls == []
    assert transport_calls == []


def test_execute_uses_injected_vault_and_fake_transport_once_with_redaction() -> None:
    access_secret = "".join(["runtime", "-access", "-redact"])
    account_secret = "".join(["runtime", "-account", "-redact"])
    vault_calls: list[str] = []
    transport_calls: list[dict] = []

    def fake_vault(payload: dict) -> dict:
        credential_name = payload["credential_name"]
        vault_calls.append(credential_name)
        secret = access_secret
        if credential_name == ACCOUNT_ID_CREDENTIAL_NAME:
            secret = account_secret
        return {
            "credential_name": credential_name,
            "load_status": "loaded_from_test_adapter",
            "secret_value": secret,
        }

    def fake_transport(payload: dict) -> dict:
        transport_calls.append(payload)
        return {"status_code": 400, "status": "http_error", "body": {"ok": False}}

    decision = evaluate_oanda_demo_vault_backed_one_order_transport_v1(
        _valid_context(),
        vault_load_callable=fake_vault,
        http_post_callable=fake_transport,
        execute_transport=True,
    )
    serialized = json.dumps(decision, sort_keys=True)

    assert decision["status"] == VAULT_BACKED_DEMO_ONE_ORDER_ATTEMPTED
    assert vault_calls == [ACCESS_TOKEN_CREDENTIAL_NAME, ACCOUNT_ID_CREDENTIAL_NAME]
    assert len(transport_calls) == 1
    assert decision["broker_network_call_performed"] is True
    assert decision["order_attempt_count"] == 1
    assert decision["order_placement_performed"] is False
    assert access_secret not in serialized
    assert account_secret not in serialized


def test_missing_vault_credentials_blocks_before_transport() -> None:
    transport_calls: list[dict] = []

    def fake_vault(payload: dict) -> dict:
        return {
            "credential_name": payload["credential_name"],
            "load_status": "credential_not_found",
            "secret_value": "",
        }

    decision = evaluate_oanda_demo_vault_backed_one_order_transport_v1(
        _valid_context(),
        vault_load_callable=fake_vault,
        http_post_callable=lambda payload: transport_calls.append(payload),
        execute_transport=True,
    )

    assert decision["status"] == BLOCKED_BY_MISSING_VAULT_CREDENTIALS
    assert decision["credential_read_performed"] is True
    assert decision["broker_network_call_performed"] is False
    assert transport_calls == []


def test_missing_stop_loss_blocks_before_vault() -> None:
    vault_calls: list[dict] = []
    context = _valid_context()
    context["stop_loss"] = ""

    decision = evaluate_oanda_demo_vault_backed_one_order_transport_v1(
        context,
        vault_load_callable=lambda payload: vault_calls.append(payload),
        execute_transport=True,
    )

    assert decision["status"] == BLOCKED_BY_MISSING_STOP_LOSS
    assert decision["credential_read_performed"] is False
    assert vault_calls == []


def test_live_endpoint_and_profit_claim_block_before_vault() -> None:
    live_context = _valid_context()
    live_context["live_api_base_url"] = "https://api-fxtrade.oanda.com"
    profit_context = _valid_context()
    profit_context["profit_claim_made"] = True

    assert (
        evaluate_oanda_demo_vault_backed_one_order_transport_v1(
            live_context,
            execute_transport=True,
        )["status"]
        == BLOCKED_BY_LIVE_ENDPOINT
    )
    assert (
        evaluate_oanda_demo_vault_backed_one_order_transport_v1(
            profit_context,
            execute_transport=True,
        )["status"]
        == BLOCKED_BY_PROFIT_CLAIM
    )


def test_script_print_template_does_not_load_vault_or_transport(capsys) -> None:
    exit_code = main(["--print-template"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["script_status"] == "VAULT_BACKED_DEMO_ONE_ORDER_TEMPLATE_ONLY"
    assert payload["broker_network_call_performed"] is False
    assert payload["credential_read_performed"] is False
    assert ACCESS_TOKEN_CREDENTIAL_NAME in payload["approved_vault_labels"]
    assert ACCOUNT_ID_CREDENTIAL_NAME in payload["approved_vault_labels"]


def test_script_execute_uses_injected_dependencies_only(capsys) -> None:
    access_secret = "".join(["script", "-access", "-redact"])
    account_secret = "".join(["script", "-account", "-redact"])

    def fake_vault(payload: dict) -> dict:
        secret = account_secret
        if payload["credential_name"] == ACCESS_TOKEN_CREDENTIAL_NAME:
            secret = access_secret
        return {
            "credential_name": payload["credential_name"],
            "load_status": "loaded_from_test_adapter",
            "secret_value": secret,
        }

    def fake_transport(payload: dict) -> dict:
        return {"status_code": 400, "status": "http_error", "body": {"ok": False}}

    exit_code = main(
        [
            "--execute-vault-backed-demo-one-order",
            "--instrument",
            "EUR_USD",
            "--direction",
            "BUY",
            "--units",
            "1",
            "--stop-loss",
            "1.07000",
            "--take-profit",
            "1.07100",
            "--risk-amount",
            "1.00",
            "--client-order-id",
            "AIOS-DEMO-ONE-ORDER-OWNER-RUNTIME-001",
            "--order-type",
            "MARKET",
            "--i-confirm-demo-only",
            "--i-confirm-vault-backed-runtime-only",
            "--i-confirm-one-order-only",
            "--i-confirm-owner-manual-runtime-only",
            "--i-confirm-stop-loss",
            "--i-confirm-take-profit",
            "--i-confirm-no-live-endpoint",
            "--i-confirm-no-autonomous-order",
            "--i-confirm-no-second-order",
            "--i-confirm-post-trade-evidence",
            "--i-confirm-kill-switch-ready",
            "--i-understand-loss-possible",
            "--i-understand-no-profit-guarantee",
        ],
        vault_load_callable=fake_vault,
        http_post_callable=fake_transport,
    )
    output = capsys.readouterr().out
    payload = json.loads(output)

    assert exit_code == 0
    assert payload["script_status"] == VAULT_BACKED_DEMO_ONE_ORDER_ATTEMPTED
    assert payload["broker_network_call_performed"] is True
    assert payload["order_attempt_count"] == 1
    assert access_secret not in output
    assert account_secret not in output


def _valid_context() -> dict:
    return {
        "instrument": "EUR_USD",
        "direction": "BUY",
        "units": 1,
        "stop_loss": "1.07000",
        "take_profit": "1.07100",
        "risk_amount": 1.0,
        "client_order_id": "AIOS-DEMO-ONE-ORDER-OWNER-RUNTIME-001",
        "order_type": "MARKET",
        "demo_only_confirmed": True,
        "vault_backed_runtime_only_confirmed": True,
        "one_order_only_confirmed": True,
        "owner_manual_runtime_only_confirmed": True,
        "stop_loss_confirmed": True,
        "take_profit_confirmed": True,
        "no_live_endpoint_confirmed": True,
        "no_autonomous_order_confirmed": True,
        "no_second_order_confirmed": True,
        "post_trade_evidence_confirmed": True,
        "kill_switch_ready_confirmed": True,
        "loss_possible_understood": True,
        "no_profit_guarantee_understood": True,
    }
