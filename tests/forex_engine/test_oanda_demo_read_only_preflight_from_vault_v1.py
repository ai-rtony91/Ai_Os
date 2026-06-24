from __future__ import annotations

import json
from pathlib import Path

import pytest

from automation.forex_engine.oanda_demo_read_only_preflight_from_vault_v1 import (
    ACCESS_TOKEN_CREDENTIAL_NAME,
    ACCOUNT_ID_CREDENTIAL_NAME,
    VAULT_PREFLIGHT_BLOCKED_LIVE_MODE,
    VAULT_PREFLIGHT_BLOCKED_MISSING_ACCOUNT_ID,
    VAULT_PREFLIGHT_BLOCKED_MISSING_TOKEN,
    VAULT_PREFLIGHT_BLOCKED_MISSING_VAULT_ADAPTER,
    VAULT_PREFLIGHT_BLOCKED_UNSAFE_ENDPOINT,
    VAULT_PREFLIGHT_DRY_RUN_READY,
    VAULT_PREFLIGHT_READ_ONLY_ATTEMPTED,
    default_oanda_demo_read_only_preflight_from_vault_context_v1,
    evaluate_oanda_demo_read_only_preflight_from_vault_v1,
    validate_oanda_demo_vault_preflight_endpoint_url_v1,
)
from scripts.forex_delivery import run_oanda_demo_read_only_preflight_from_vault_v1 as runner


TOKEN = "tok_runtime_secret_123"
ACCOUNT_ID = "101-001-12345678-001"


def test_dry_run_safe_by_default() -> None:
    vault_calls: list[dict] = []
    http_calls: list[dict] = []

    result = evaluate_oanda_demo_read_only_preflight_from_vault_v1(
        vault_load_callable=lambda payload: vault_calls.append(payload),
        http_get_callable=lambda payload: http_calls.append(payload),
    )

    assert result["status"] == VAULT_PREFLIGHT_DRY_RUN_READY
    assert vault_calls == []
    assert http_calls == []
    assert result["broker_network_call_performed"] is False
    assert result["order_placement_performed"] is False
    assert result["dotenv_read"] is False


def test_missing_vault_adapter_blocks() -> None:
    result = evaluate_oanda_demo_read_only_preflight_from_vault_v1(
        http_get_callable=_fake_http_get([]),
        execute_preflight=True,
    )

    assert result["status"] == VAULT_PREFLIGHT_BLOCKED_MISSING_VAULT_ADAPTER
    assert result["broker_network_call_performed"] is False


def test_missing_token_blocks() -> None:
    http_calls: list[dict] = []

    result = evaluate_oanda_demo_read_only_preflight_from_vault_v1(
        vault_load_callable=_fake_vault_loader(token="", account_id=ACCOUNT_ID),
        http_get_callable=_fake_http_get(http_calls),
        execute_preflight=True,
    )

    assert result["status"] == VAULT_PREFLIGHT_BLOCKED_MISSING_TOKEN
    assert http_calls == []


def test_missing_account_id_blocks() -> None:
    http_calls: list[dict] = []

    result = evaluate_oanda_demo_read_only_preflight_from_vault_v1(
        vault_load_callable=_fake_vault_loader(token=TOKEN, account_id=""),
        http_get_callable=_fake_http_get(http_calls),
        execute_preflight=True,
    )

    assert result["status"] == VAULT_PREFLIGHT_BLOCKED_MISSING_ACCOUNT_ID
    assert http_calls == []


def test_live_mode_blocks() -> None:
    context = default_oanda_demo_read_only_preflight_from_vault_context_v1()
    context.update(
        {
            "broker": "OANDA_LIVE",
            "environment": "LIVE",
            "demo_only": False,
            "live_mode": True,
            "live_credentials_allowed": True,
            "live_api_base_url": "https://api-fxtrade.oanda.com",
        }
    )

    result = evaluate_oanda_demo_read_only_preflight_from_vault_v1(
        preflight_context=context,
        vault_load_callable=_fake_vault_loader(),
        http_get_callable=_fake_http_get([]),
        execute_preflight=True,
    )

    assert result["status"] == VAULT_PREFLIGHT_BLOCKED_LIVE_MODE
    assert result["live_endpoint_used"] is False


@pytest.mark.parametrize(
    "url",
    [
        "https://api-fxpractice.oanda.com/v3/accounts/101/orders",
        "https://api-fxpractice.oanda.com/v3/accounts/101/trades",
        "https://api-fxpractice.oanda.com/v3/accounts/101/positions",
        "https://api-fxtrade.oanda.com/v3/accounts",
    ],
)
def test_unsafe_endpoint_blocks(url: str) -> None:
    result = evaluate_oanda_demo_read_only_preflight_from_vault_v1(
        endpoint_plan_override=[url],
    )

    assert result["status"] == VAULT_PREFLIGHT_BLOCKED_UNSAFE_ENDPOINT


def test_practice_get_endpoints_are_allowed() -> None:
    urls = [
        "https://api-fxpractice.oanda.com/v3/accounts",
        f"https://api-fxpractice.oanda.com/v3/accounts/{ACCOUNT_ID}",
        f"https://api-fxpractice.oanda.com/v3/accounts/{ACCOUNT_ID}/summary",
        f"https://api-fxpractice.oanda.com/v3/accounts/{ACCOUNT_ID}/instruments",
    ]

    for url in urls:
        assert validate_oanda_demo_vault_preflight_endpoint_url_v1(url) == []


def test_redaction_removes_token() -> None:
    result = _successful_execute_result()
    serialized = json.dumps(result, sort_keys=True)

    assert result["status"] == VAULT_PREFLIGHT_READ_ONLY_ATTEMPTED
    assert TOKEN not in serialized


def test_redaction_removes_account_id() -> None:
    result = _successful_execute_result()
    serialized = json.dumps(result, sort_keys=True)

    assert result["status"] == VAULT_PREFLIGHT_READ_ONLY_ATTEMPTED
    assert ACCOUNT_ID not in serialized


def test_script_print_template_reads_no_credential(capsys: pytest.CaptureFixture[str]) -> None:
    def fail_loader(payload: dict) -> dict:
        raise AssertionError("vault loader must not be called")

    exit_code = runner.main(["--print-template"], vault_load_callable=fail_loader)
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["credential_read_performed"] is False
    assert payload["account_id_read_performed"] is False
    assert payload["broker_network_call_performed"] is False


def test_script_missing_confirmations_blocks(capsys: pytest.CaptureFixture[str]) -> None:
    vault_calls: list[dict] = []

    exit_code = runner.main(
        ["--execute-read-only-preflight-from-vault"],
        vault_load_callable=lambda payload: vault_calls.append(payload),
        http_get_callable=_fake_http_get([]),
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 1
    assert payload["script_status"] == "BLOCKED_MISSING_REQUIRED_CONFIRMATIONS"
    assert vault_calls == []
    assert payload["broker_network_call_performed"] is False


def test_script_execute_path_uses_injected_fakes_only(
    capsys: pytest.CaptureFixture[str],
) -> None:
    vault_calls: list[dict] = []
    http_calls: list[dict] = []

    exit_code = runner.main(
        ["--execute-read-only-preflight-from-vault", *_confirmation_flags()],
        vault_load_callable=_fake_vault_loader(calls=vault_calls),
        http_get_callable=_fake_http_get(http_calls),
    )
    payload = json.loads(capsys.readouterr().out)
    serialized = json.dumps(payload, sort_keys=True)

    assert exit_code == 0
    assert [call["credential_name"] for call in vault_calls] == [
        ACCESS_TOKEN_CREDENTIAL_NAME,
        ACCOUNT_ID_CREDENTIAL_NAME,
    ]
    assert len(http_calls) == 4
    assert payload["script_status"] == VAULT_PREFLIGHT_READ_ONLY_ATTEMPTED
    assert TOKEN not in serialized
    assert ACCOUNT_ID not in serialized


def test_no_order_execution_fields_can_become_true() -> None:
    result = _successful_execute_result()

    assert result["order_placement_performed"] is False
    assert result["orders_endpoint_called"] is False
    assert result["execution_authority"]["demo_order_allowed"] is False
    assert result["execution_authority"]["live_order_allowed"] is False
    assert result["execution_authority"]["order_mutation_allowed"] is False
    assert result["execution_authority"]["position_mutation_allowed"] is False


def test_no_broker_write_authority_can_become_true() -> None:
    result = _successful_execute_result()

    assert result["execution_authority"]["broker_write_allowed"] is False
    assert result["broker_write_allowed"] is False


def test_no_scheduler_daemon_webhook_authority_can_become_true() -> None:
    result = _successful_execute_result()

    assert result["execution_authority"]["scheduler_allowed"] is False
    assert result["execution_authority"]["daemon_allowed"] is False
    assert result["execution_authority"]["webhook_allowed"] is False


def test_no_dotenv_read_is_represented() -> None:
    result = _successful_execute_result()

    assert result["dotenv_read"] is False
    assert result["safety_proof"]["dotenv_read"] is False


def test_status_classification_is_deterministic() -> None:
    observed = {
        evaluate_oanda_demo_read_only_preflight_from_vault_v1()["status"],
        evaluate_oanda_demo_read_only_preflight_from_vault_v1(
            execute_preflight=True
        )["status"],
        evaluate_oanda_demo_read_only_preflight_from_vault_v1(
            vault_load_callable=_fake_vault_loader(token="", account_id=ACCOUNT_ID),
            http_get_callable=_fake_http_get([]),
            execute_preflight=True,
        )["status"],
        evaluate_oanda_demo_read_only_preflight_from_vault_v1(
            vault_load_callable=_fake_vault_loader(token=TOKEN, account_id=""),
            http_get_callable=_fake_http_get([]),
            execute_preflight=True,
        )["status"],
        evaluate_oanda_demo_read_only_preflight_from_vault_v1(
            endpoint_plan_override=[
                "https://api-fxpractice.oanda.com/v3/accounts/101/orders"
            ],
        )["status"],
        _successful_execute_result()["status"],
    }

    assert observed == {
        VAULT_PREFLIGHT_DRY_RUN_READY,
        VAULT_PREFLIGHT_BLOCKED_MISSING_VAULT_ADAPTER,
        VAULT_PREFLIGHT_BLOCKED_MISSING_TOKEN,
        VAULT_PREFLIGHT_BLOCKED_MISSING_ACCOUNT_ID,
        VAULT_PREFLIGHT_BLOCKED_UNSAFE_ENDPOINT,
        VAULT_PREFLIGHT_READ_ONLY_ATTEMPTED,
    }


def test_campaign_anchor_report_exists() -> None:
    assert Path(
        "Reports/forex_delivery/AIOS_FOREX_120_PERCENT_PROFITABILITY_CAMPAIGN_ANCHOR_V1.md"
    ).exists()


def test_campaign_target_is_represented_as_2_20x_starting_equity() -> None:
    text = _campaign_report_text()

    assert "starting campaign equity multiplied by 2.20" in text
    assert "2.20x starting campaign equity" in text


def test_campaign_target_is_represented_as_120_percent_net_return() -> None:
    text = _campaign_report_text()

    assert "+120% net campaign return target" in text


def test_campaign_target_is_not_represented_as_guaranteed() -> None:
    text = _campaign_report_text().lower()

    assert "does not guarantee" in text
    assert "no claim that the 120% target is guaranteed" in text


def test_campaign_target_is_not_represented_as_one_trade_requirement() -> None:
    text = _campaign_report_text().lower()

    assert "multiple sequential trades, not one trade" in text
    assert "not a one-trade requirement" in text


def _successful_execute_result() -> dict:
    return evaluate_oanda_demo_read_only_preflight_from_vault_v1(
        vault_load_callable=_fake_vault_loader(),
        http_get_callable=_fake_http_get([]),
        execute_preflight=True,
    )


def _fake_vault_loader(
    *,
    token: str = TOKEN,
    account_id: str = ACCOUNT_ID,
    calls: list[dict] | None = None,
):
    def load(payload: dict) -> dict:
        if calls is not None:
            calls.append(payload)
        credential_name = payload["credential_name"]
        if credential_name == ACCESS_TOKEN_CREDENTIAL_NAME:
            return {"credential_name": credential_name, "secret_value": token}
        if credential_name == ACCOUNT_ID_CREDENTIAL_NAME:
            return {"credential_name": credential_name, "secret_value": account_id}
        return {"credential_name": credential_name, "secret_value": ""}

    return load


def _fake_http_get(calls: list[dict]):
    def get(payload: dict) -> dict:
        calls.append(payload)
        url = payload["url"]
        if url.endswith("/v3/accounts"):
            body = {"accounts": [{"id": ACCOUNT_ID, "environment": "demo"}]}
        elif url.endswith("/summary"):
            body = {"account": {"id": ACCOUNT_ID, "environment": "demo"}}
        elif url.endswith("/instruments"):
            body = {"instruments": [{"name": "EUR_USD"}]}
        else:
            body = {"account": {"id": ACCOUNT_ID, "environment": "demo"}}
        return {"status_code": 200, "status": "success", "body": body}

    return get


def _confirmation_flags() -> list[str]:
    return [
        "--i-confirm-demo-only",
        "--i-confirm-read-only-preflight",
        "--i-confirm-windows-vault-only",
        "--i-confirm-no-env-file",
        "--i-confirm-no-repo-persistence",
        "--i-confirm-no-live-credentials",
        "--i-confirm-token-visible-account",
        "--i-confirm-no-order-endpoint",
        "--i-confirm-no-trade-mutation",
        "--i-confirm-no-second-order-attempt",
    ]


def _campaign_report_text() -> str:
    return Path(
        "Reports/forex_delivery/AIOS_FOREX_120_PERCENT_PROFITABILITY_CAMPAIGN_ANCHOR_V1.md"
    ).read_text(encoding="utf-8")
