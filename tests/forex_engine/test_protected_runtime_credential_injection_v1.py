from __future__ import annotations

from pathlib import Path

import pytest

from automation.forex_engine import protected_runtime_credential_injection_v1 as injection


class FakeHttpClient:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def post(self, url: str, json: dict, headers: dict) -> dict:
        self.calls.append({"url": url, "json": dict(json), "headers": dict(headers)})
        return {"status_code": 201, "json": {"status": "ACCEPTED"}}


def _ready_request(**overrides: object) -> dict:
    request = {
        "authenticated_operator": True,
        "protected_action_authorized": True,
        "live_exception_requested": True,
        "understands_live_risk_ack": True,
        "operator_approved_live_runtime": True,
        "credentials_runtime_only": True,
        "credentials_persisted": False,
        "account_id_persisted": False,
        "allow_live_network_once": True,
        "one_trade_only": True,
        "micro_size_only": True,
        "no_retry": True,
        "no_loop": True,
        "max_order_count": 1,
        "runtime_auth_provider_injected": True,
        "http_client_injected": True,
        "final_bridge_ready": True,
        "oanda_transport_ready": True,
        "oanda_connector_ready": True,
        "max_loss_gate_clear": True,
        "daily_stop_clear": True,
        "kill_switch_enabled": False,
    }
    request.update(overrides)
    return request


def _order_intent() -> dict:
    return {
        "instrument": "EUR_USD",
        "side": "BUY",
        "units": 10,
        "stop_loss": "1.0800",
        "take_profit": "1.0860",
    }


def test_missing_injection_request_returns_invalid_or_blocked() -> None:
    result = injection.validate_runtime_injection_request(None)

    assert result["status"] in {
        injection.PROTECTED_RUNTIME_INJECTION_INVALID,
        injection.PROTECTED_RUNTIME_INJECTION_BLOCKED,
    }
    assert "injection_request_missing" in result["blockers"]


def test_missing_authenticated_operator_blocks() -> None:
    result = injection.validate_runtime_injection_request(_ready_request(authenticated_operator=False))

    assert result["status"] != injection.PROTECTED_RUNTIME_INJECTION_READY
    assert "authenticated_operator_required" in result["blockers"]


def test_missing_protected_action_authorization_blocks() -> None:
    result = injection.validate_runtime_injection_request(_ready_request(protected_action_authorized=False))

    assert result["status"] != injection.PROTECTED_RUNTIME_INJECTION_READY
    assert "protected_action_authorization_required" in result["blockers"]


def test_missing_live_exception_request_blocks() -> None:
    result = injection.validate_runtime_injection_request(_ready_request(live_exception_requested=False))

    assert result["status"] != injection.PROTECTED_RUNTIME_INJECTION_READY
    assert "live_exception_request_required" in result["blockers"]


def test_credentials_runtime_only_false_blocks() -> None:
    result = injection.validate_runtime_injection_request(_ready_request(credentials_runtime_only=False))

    assert result["status"] == injection.PROTECTED_RUNTIME_INJECTION_BLOCKED
    assert "credentials_runtime_only_required" in result["blockers"]


def test_credentials_persisted_true_blocks() -> None:
    result = injection.validate_runtime_injection_request(_ready_request(credentials_persisted=True))

    assert result["status"] == injection.PROTECTED_RUNTIME_INJECTION_BLOCKED
    assert "credentials_persisted_blocked" in result["blockers"]


def test_account_id_persisted_true_blocks() -> None:
    result = injection.validate_runtime_injection_request(_ready_request(account_id_persisted=True))

    assert result["status"] == injection.PROTECTED_RUNTIME_INJECTION_BLOCKED
    assert "account_id_persisted_blocked" in result["blockers"]


def test_allow_live_network_once_false_blocks() -> None:
    result = injection.validate_runtime_injection_request(_ready_request(allow_live_network_once=False))

    assert result["status"] == injection.PROTECTED_RUNTIME_INJECTION_BLOCKED
    assert "allow_live_network_once_required" in result["blockers"]


def test_max_order_count_not_equal_to_one_blocks() -> None:
    result = injection.validate_runtime_injection_request(_ready_request(max_order_count=2))

    assert result["status"] == injection.PROTECTED_RUNTIME_INJECTION_BLOCKED
    assert "max_order_count_must_equal_one" in result["blockers"]


def test_ready_request_returns_ready() -> None:
    result = injection.build_runtime_injection_contract(_ready_request())

    assert result["status"] == injection.PROTECTED_RUNTIME_INJECTION_READY
    assert result["ready"] is True


def test_build_runtime_auth_provider_rejects_blank_access_token() -> None:
    with pytest.raises(ValueError, match="access_token_required"):
        injection.build_runtime_auth_provider("", "ACCOUNT_SHOULD_NOT_LEAK")


def test_build_runtime_auth_provider_rejects_blank_account_id() -> None:
    with pytest.raises(ValueError, match="account_id_required"):
        injection.build_runtime_auth_provider("TOKEN_SHOULD_NOT_LEAK", "")


def test_runtime_auth_provider_returns_values_only_when_invoked() -> None:
    provider = injection.build_runtime_auth_provider("TOKEN_SHOULD_NOT_LEAK", "ACCOUNT_SHOULD_NOT_LEAK")

    assert callable(provider)
    runtime_auth = provider()
    assert runtime_auth["access_token"] == "TOKEN_SHOULD_NOT_LEAK"
    assert runtime_auth["account_id"] == "ACCOUNT_SHOULD_NOT_LEAK"


def test_sanitized_summary_does_not_include_token_value_or_account_id_value() -> None:
    provider = injection.build_runtime_auth_provider("TOKEN_SHOULD_NOT_LEAK", "ACCOUNT_SHOULD_NOT_LEAK")

    summary = injection.build_sanitized_runtime_injection_summary(
        _ready_request(),
        runtime_auth_provider_present=callable(provider),
        http_client_present=True,
    )
    rendered = repr(summary)

    assert "TOKEN_SHOULD_NOT_LEAK" not in rendered
    assert "ACCOUNT_SHOULD_NOT_LEAK" not in rendered
    assert summary["runtime_auth_provider_present"] is True
    assert summary["credential_values_returned"] is False
    assert summary["account_identifier_values_returned"] is False


def test_dry_run_local_harness_does_not_call_fake_http_client_post() -> None:
    http_client = FakeHttpClient()
    provider = injection.build_runtime_auth_provider("TOKEN_SHOULD_NOT_LEAK", "ACCOUNT_SHOULD_NOT_LEAK")

    result = injection.build_protected_local_execution_harness(
        _ready_request(),
        http_client,
        provider,
        _order_intent(),
        dry_run_only=True,
    )

    assert result["status"] == injection.PROTECTED_LOCAL_HARNESS_READY
    assert result["ready"] is True
    assert result["broker_call_performed"] is False
    assert result["order_executed"] is False
    assert http_client.calls == []


def test_non_dry_run_harness_blocks_without_protected_live_execution_command_true() -> None:
    http_client = FakeHttpClient()
    provider = injection.build_runtime_auth_provider("TOKEN_SHOULD_NOT_LEAK", "ACCOUNT_SHOULD_NOT_LEAK")

    result = injection.build_protected_local_execution_harness(
        _ready_request(),
        http_client,
        provider,
        _order_intent(),
        dry_run_only=False,
    )

    assert result["status"] == injection.PROTECTED_LOCAL_HARNESS_REVIEW_REQUIRED
    assert "protected_live_execution_command_required" in result["blockers"]
    assert http_client.calls == []


def test_fake_armed_harness_assembles_readiness_without_leaking_values() -> None:
    http_client = FakeHttpClient()
    provider = injection.build_runtime_auth_provider("TOKEN_SHOULD_NOT_LEAK", "ACCOUNT_SHOULD_NOT_LEAK")
    request = _ready_request(protected_live_execution_command=True)

    result = injection.build_protected_local_execution_harness(
        request,
        http_client,
        provider,
        _order_intent(),
        dry_run_only=False,
    )
    rendered = repr(result)

    assert result["status"] == injection.PROTECTED_LOCAL_HARNESS_READY
    assert result["sanitized_summary"]["observed_final_bridge_status"] == "FINAL_LIVE_OPERATOR_BRIDGE_READY"
    assert result["sanitized_summary"]["observed_transport_ready"] is True
    assert result["sanitized_summary"]["observed_connector_ready"] is True
    assert result["broker_call_performed"] is False
    assert http_client.calls == []
    assert "TOKEN_SHOULD_NOT_LEAK" not in rendered
    assert "ACCOUNT_SHOULD_NOT_LEAK" not in rendered


def test_source_scan_proves_no_secret_loading_or_real_network_triggers() -> None:
    source = Path("automation/forex_engine/protected_runtime_credential_injection_v1.py").read_text(
        encoding="utf-8"
    ).lower()
    forbidden_snippets = (
        "import os",
        "from os",
        "os.environ",
        "getenv(",
        "dotenv",
        "import requests",
        "from requests",
        "open(",
        "scheduler",
        "daemon",
        "webhook",
        "retry loop",
        "urlopen(",
        "urllib.request",
        "socket.",
        "api-fxtrade",
    )

    for snippet in forbidden_snippets:
        assert snippet not in source
