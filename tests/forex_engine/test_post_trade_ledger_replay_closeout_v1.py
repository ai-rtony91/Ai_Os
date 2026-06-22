from __future__ import annotations

import copy
from pathlib import Path

from automation.forex_engine import final_live_operator_bridge_v1 as bridge
from automation.forex_engine import live_preflight_evidence_bundle_v1 as preflight
from automation.forex_engine import oanda_live_http_transport_v1 as transport
from automation.forex_engine import oanda_live_runtime_connector_v2 as connector
from automation.forex_engine import post_trade_ledger_replay_closeout_v1 as module
from automation.forex_engine import protected_live_execution_command_package_v1 as command
from automation.forex_engine import protected_runtime_credential_injection_v1 as injection
from automation.forex_engine import single_protected_live_micro_trade_execution_package_v1 as package


class FakeHttpClient:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def post(self, url: str, json: dict[str, object], headers: dict[str, object]) -> dict[str, object]:
        self.calls.append({"url": url, "json": dict(json), "headers": dict(headers)})
        return {"status_code": 200, "accepted": True}


class FakeSubmitter:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def place_live_micro_order(self, order_intent: dict[str, object]) -> dict[str, object]:
        self.calls.append(dict(order_intent))
        return {
            "submitted": True,
            "accepted": True,
            "instrument": order_intent["instrument"],
            "side": order_intent["side"],
            "units": order_intent["units"],
            "account_id": "ACCOUNT_SHOULD_NOT_LEAK",
        }

    def submit_live_micro_order(self, order_intent: dict[str, object]) -> dict[str, object]:
        return self.place_live_micro_order(order_intent)


def _order_intent(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "instrument": "EUR_USD",
        "side": "BUY",
        "units": 1000,
        "stop_loss": "1.0800",
        "take_profit": "1.0860",
        "risk_reward_ratio": 2.0,
        "risk_cap_confirmed": True,
        "stop_loss_confirmed": True,
        "take_profit_confirmed": True,
        "one_trade_only": True,
        "micro_size_only": True,
        "max_loss_gate_clear": True,
        "daily_stop_clear": True,
        "kill_switch_enabled": False,
    }
    payload.update(overrides)
    return payload


def _authority(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "authenticated_operator": True,
        "protected_action_authorized": True,
        "live_exception_requested": True,
        "understands_live_risk_ack": True,
        "operator_approved_live_runtime": True,
        "final_execute_live_order_command_ack": True,
        "final_human_execution_approval": True,
        "one_trade_only": True,
        "micro_size_only": True,
        "no_retry": True,
        "no_loop": True,
        "max_order_count": 1,
    }
    payload.update(overrides)
    return payload


def _runtime_inputs(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "runtime_auth_provider_injected": True,
        "http_client_injected": True,
        "fake_client_mode": True,
        "real_execution_forbidden_in_codex": True,
        "allow_live_network_once": False,
        "protected_live_execution_command": False,
        "fake_execution_selected": True,
        "dry_run_only": True,
    }
    payload.update(overrides)
    return payload


def _ready_arm_request() -> dict[str, object]:
    return {
        "instrument": "EUR_USD",
        "side": "BUY",
        "units": 1000,
        "stop_loss": "1.0800",
        "take_profit": "1.0860",
        "authenticated_operator": True,
        "protected_action_authorized": True,
        "live_exception_requested": True,
        "understands_live_risk_ack": True,
        "allow_live_network_once": True,
        "credentials_runtime_only": True,
        "credentials_persisted": False,
        "account_id_persisted": False,
        "max_loss_gate_clear": True,
        "daily_stop_clear": True,
        "kill_switch_enabled": False,
        "single_order_only": True,
        "micro_size_only": True,
        "requested_order_count": 1,
        "max_order_count": 1,
        "existing_live_order_count": 0,
    }


def _runtime_snapshot() -> dict[str, object]:
    return {
        "balance": 10000.0,
        "equity": 10000.0,
        "realized_pl": 0.0,
        "open_risk": 0.0,
        "active_trades": 0,
        "evidence_freshness": "fixture_current",
    }


def _account_risk_envelope(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "account_currency": "USD",
        "balance": 10000.0,
        "equity": 10000.0,
        "margin_available": 1000.0,
        "open_risk": 0.0,
        "max_loss_gate_clear": True,
        "daily_stop_clear": True,
        "kill_switch_enabled": False,
        "portfolio_exposure_clear": True,
        "micro_risk_cap_amount": 10.0,
        "account_id_present": False,
        "account_id_persisted": False,
    }
    payload.update(overrides)
    return payload


def _instrument_envelope(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "instrument": "EUR_USD",
        "requested_units": 1000,
        "min_units": 1,
        "max_units": 1000,
        "trade_enabled": True,
        "market_open": True,
        "instrument_supported": True,
    }
    payload.update(overrides)
    return payload


def _quote_envelope(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "bid": 1.0810,
        "ask": 1.0815,
        "spread": 0.0005,
        "max_spread": 0.0010,
        "quote_fresh": True,
        "quote_age_seconds": 2,
        "max_quote_age_seconds": 10,
        "market_data_source_verified": True,
        "broker_call_performed": False,
    }
    payload.update(overrides)
    return payload


def _operator_state(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "authenticated_operator": True,
        "protected_action_authorized": True,
        "protected_action_authorization_required": True,
        "live_exception_requested": True,
        "live_exception_request_required": True,
        "understands_live_risk_ack": True,
        "live_risk_ack_required": True,
        "operator_approved_live_runtime": True,
        "operator_live_runtime_approval_required": True,
        "no_default_network": True,
        "no_retry": True,
        "no_loop": True,
        "one_order_only": True,
        "credential_persisted": False,
        "account_id_persisted": False,
        "execution_requested": False,
        "order_executed": False,
        "broker_call_performed": False,
        "mobile_operator_ready": True,
    }
    payload.update(overrides)
    return payload


def _runtime_auth_provider() -> dict[str, str]:
    return injection.build_runtime_auth_provider("TOKEN_SHOULD_NOT_LEAK", "ACCOUNT_SHOULD_NOT_LEAK")


def _transport_config() -> dict[str, object]:
    return {
        "operator_approved_live_runtime": True,
        "live_endpoint_confirmed": True,
        "allow_live_network_once": True,
        "credentials_runtime_only": True,
        "credentials_persisted": False,
        "account_id_persisted": False,
        "single_order_only": True,
        "micro_size_only": True,
        "no_retry": True,
        "no_loop": True,
        "max_order_count": 1,
        "http_client_injected": True,
        "runtime_auth_provider_injected": True,
    }


def _connector_config() -> dict[str, object]:
    return {
        "operator_approved_live_runtime": True,
        "live_endpoint_confirmed": True,
        "credentials_runtime_only": True,
        "credentials_persisted": False,
        "account_id_persisted": False,
        "single_order_only": True,
        "micro_size_only": True,
        "no_retry": True,
        "no_loop": True,
        "max_order_count": 1,
        "transport_injected": True,
    }


def _build_ready_spine(realized_pnl: float | None = 0.5) -> dict[str, object]:
    order = _order_intent()
    runtime_auth_provider = _runtime_auth_provider()
    fake_http_client = FakeHttpClient()

    runtime_injection_state = injection.build_runtime_injection_contract(
        {
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
            "runtime_auth_provider_injected": True,
            "http_client_injected": True,
            "final_bridge_ready": True,
            "oanda_transport_ready": True,
            "oanda_connector_ready": True,
            "max_order_count": 1,
        }
    )
    runtime_injection_state["sanitized_summary"]["understands_live_risk_ack"] = True

    transport_state = transport.build_oanda_live_http_transport_readiness(
        transport.build_oanda_live_http_transport_config(_transport_config()),
        http_client=fake_http_client,
        runtime_auth_provider=runtime_auth_provider,
    )
    connector_state = connector.build_oanda_live_connector_readiness_packet(
        connector.build_oanda_live_connector_config(_connector_config())
    )
    connector_state["oanda_connector_ready"] = True
    final_bridge_state = bridge.build_final_live_operator_bridge_state(_ready_arm_request(), _runtime_snapshot())
    preflight_bundle_state = preflight.build_live_preflight_evidence_bundle(
        final_bridge_state=final_bridge_state,
        runtime_injection_state=runtime_injection_state,
        oanda_connector_state=connector_state,
        oanda_transport_state=transport_state,
        account_risk_envelope=_account_risk_envelope(),
        instrument_envelope=_instrument_envelope(),
        quote_spread_envelope=_quote_envelope(),
        order_intent_envelope=order,
        mobile_operator_state={"mobile_operator_ready": True},
        operator_state=_operator_state(),
    )
    sealed_command = command.seal_protected_live_execution_command(
        command.build_protected_live_execution_command(_authority(), preflight_bundle_state, order)
    )
    execution_package_state = package.build_single_live_micro_trade_execution_package(
        authority_state=_authority(),
        command_package=sealed_command,
        runtime_inputs=_runtime_inputs(),
        order_intent=order,
    )
    execution_result = package.execute_single_live_micro_trade_fake_only(
        copy.deepcopy(execution_package_state),
        fake_client=FakeSubmitter(),
    )
    operator_review_state: dict[str, object] = {"operator_review_required": True, "review_status": "POST_TRADE_REVIEW_REQUIRED"}
    if realized_pnl is not None:
        operator_review_state["realized_pnl"] = realized_pnl

    return {
        "execution_package_state": execution_package_state,
        "execution_result": execution_result,
        "command_package_state": sealed_command,
        "preflight_bundle_state": preflight_bundle_state,
        "runtime_injection_state": runtime_injection_state,
        "transport_state": transport_state,
        "connector_state": connector_state,
        "final_bridge_state": final_bridge_state,
        "operator_review_state": operator_review_state,
    }


def test_missing_post_trade_result_input_returns_invalid_or_blocked() -> None:
    result = module.validate_post_trade_result_input(None)

    assert result["status"] in {module.POST_TRADE_LEDGER_INVALID, module.POST_TRADE_LEDGER_BLOCKED}
    assert "post_trade_result_input_missing" in result["blockers"]


def test_missing_execution_package_readiness_blocks() -> None:
    payload = _build_ready_spine()
    payload["execution_package_state"]["ready"] = False

    result = module.validate_post_trade_result_input(payload)

    assert result["status"] == module.POST_TRADE_LEDGER_BLOCKED
    assert "single_live_micro_trade_package_not_ready" in result["blockers"]


def test_missing_fake_execution_result_blocks() -> None:
    payload = _build_ready_spine()
    payload["execution_result"] = {}

    result = module.validate_post_trade_result_input(payload)

    assert result["status"] == module.POST_TRADE_LEDGER_BLOCKED
    assert "execution_result_missing" in result["blockers"]


def test_real_order_executed_true_requires_real_review_path_not_fake_ready_path() -> None:
    payload = _build_ready_spine()
    payload["execution_result"]["real_order_executed"] = True
    payload["execution_result"]["real_broker_call_performed"] = True

    result = module.validate_post_trade_result_input(payload)

    assert result["status"] == module.POST_TRADE_LEDGER_BLOCKED
    assert result["trade_mode"] == module.POST_TRADE_RESULT_REAL_REVIEW_REQUIRED
    assert "real_review_path_required" in result["blockers"]


def test_credential_persisted_true_blocks() -> None:
    payload = _build_ready_spine()
    payload["runtime_injection_state"]["sanitized_summary"]["credentials_persisted"] = True

    result = module.validate_post_trade_result_input(payload)

    assert result["status"] == module.POST_TRADE_LEDGER_BLOCKED
    assert "credentials_persisted_blocked" in result["blockers"]


def test_account_id_persisted_true_blocks() -> None:
    payload = _build_ready_spine()
    payload["runtime_injection_state"]["sanitized_summary"]["account_id_persisted"] = True

    result = module.validate_post_trade_result_input(payload)

    assert result["status"] == module.POST_TRADE_LEDGER_BLOCKED
    assert "account_id_persisted_blocked" in result["blockers"]


def test_raw_broker_payload_persisted_true_blocks() -> None:
    payload = _build_ready_spine()
    payload["execution_result"]["raw_broker_payload_persisted"] = True

    result = module.validate_post_trade_result_input(payload)

    assert result["status"] == module.POST_TRADE_LEDGER_BLOCKED
    assert "raw_broker_payload_persisted_blocked" in result["blockers"]


def test_ledger_entry_builds_from_complete_fake_result() -> None:
    payload = _build_ready_spine()

    result = module.build_post_trade_ledger_entry(payload)

    assert result["ledger_status"] == module.POST_TRADE_LEDGER_READY
    assert result["trade_mode"] == module.POST_TRADE_RESULT_FAKE_ONLY
    assert result["fake_order_executed"] is True
    assert result["real_order_executed"] is False
    assert result["credential_persisted"] is False
    assert result["account_id_persisted"] is False
    assert result["raw_broker_payload_persisted"] is False


def test_replay_reconstruction_builds_observed_inputs_decision_path_risk_controls_execution_controls_and_result_path() -> None:
    payload = _build_ready_spine()

    result = module.build_post_trade_replay_reconstruction(payload)

    assert result["replay_status"] == module.POST_TRADE_REPLAY_READY
    assert result["ready"] is True
    assert result["fake_vs_real_classification"] == module.POST_TRADE_RESULT_FAKE_ONLY
    assert "execution_package_state" in result["observed_inputs"]
    assert "decision_path" in result
    assert "risk_controls" in result
    assert "execution_controls" in result
    assert "result_path" in result


def test_closeout_summary_requires_operator_review_when_pnl_unknown() -> None:
    payload = _build_ready_spine(realized_pnl=None)

    result = module.build_post_trade_closeout_summary(payload)

    assert result["closeout_status"] == module.POST_TRADE_CLOSEOUT_BLOCKED
    assert result["pnl_known"] is False
    assert result["operator_review_required"] is True
    assert "realized_pnl" in result["unresolved_fields"]


def test_closeout_summary_accepts_realized_pnl_when_supplied_as_non_sensitive_numeric_evidence() -> None:
    payload = _build_ready_spine(realized_pnl=1.25)

    result = module.build_post_trade_closeout_summary(payload)

    assert result["closeout_status"] == module.POST_TRADE_CLOSEOUT_READY
    assert result["pnl_known"] is True
    assert result["realized_pnl"] == 1.25


def test_completion_packet_is_ready_for_fake_post_trade_path() -> None:
    payload = _build_ready_spine(realized_pnl=1.25)

    result = module.build_post_trade_completion_packet(payload)

    assert result["status"] == module.POST_TRADE_CLOSEOUT_READY
    assert result["ready"] is True
    assert result["ledger_entry"]["ledger_status"] == module.POST_TRADE_LEDGER_READY
    assert result["replay_reconstruction"]["replay_status"] == module.POST_TRADE_REPLAY_READY
    assert result["closeout_summary"]["closeout_status"] == module.POST_TRADE_CLOSEOUT_READY


def test_completion_packet_marks_build_lane_completion_true() -> None:
    payload = _build_ready_spine(realized_pnl=1.25)

    result = module.build_post_trade_completion_packet(payload)

    assert result["build_lane_completion"] is True


def test_completion_packet_keeps_real_trade_completion_false_in_codex_tests() -> None:
    payload = _build_ready_spine(realized_pnl=1.25)

    result = module.build_post_trade_completion_packet(payload)

    assert result["real_trade_completion"] is False


def test_mobile_summary_includes_required_fields() -> None:
    payload = _build_ready_spine(realized_pnl=1.25)

    summary = module.build_post_trade_mobile_summary(payload)

    for key in (
        "mode",
        "post_trade_status",
        "trade_mode",
        "instrument",
        "side",
        "units",
        "stop_loss",
        "take_profit",
        "fake_order_executed",
        "real_order_executed",
        "fake_broker_call_performed",
        "real_broker_call_performed",
        "realized_pnl",
        "pnl_known",
        "operator_review_required",
        "replay_ready",
        "ledger_ready",
        "closeout_ready",
        "next_safe_action",
    ):
        assert key in summary
    assert summary["trade_mode"] == module.POST_TRADE_RESULT_FAKE_ONLY
    assert summary["pnl_known"] is True
    assert summary["realized_pnl"] == 1.25


def test_sanitized_output_never_includes_sensitive_values() -> None:
    sanitized = module.sanitize_post_trade_evidence(
        {
            "credential": "CREDENTIAL_SHOULD_NOT_LEAK",
            "token": "TOKEN_SHOULD_NOT_LEAK",
            "authorization": "AUTH_SHOULD_NOT_LEAK",
            "account_id": "ACCOUNT_SHOULD_NOT_LEAK",
            "broker_order_id": "BROKER_ORDER_SHOULD_NOT_LEAK",
            "raw_request": {"value": "RAW_REQUEST_SHOULD_NOT_LEAK"},
            "raw_response": {"value": "RAW_RESPONSE_SHOULD_NOT_LEAK"},
            "raw_payload": {"value": "RAW_PAYLOAD_SHOULD_NOT_LEAK"},
            "nested": {
                "access_token": "ACCESS_TOKEN_SHOULD_NOT_LEAK",
                "refresh_token": "REFRESH_TOKEN_SHOULD_NOT_LEAK",
                "authorization": "NESTED_AUTH_SHOULD_NOT_LEAK",
            },
        }
    )
    rendered = repr(sanitized)

    for value in (
        "CREDENTIAL_SHOULD_NOT_LEAK",
        "TOKEN_SHOULD_NOT_LEAK",
        "AUTH_SHOULD_NOT_LEAK",
        "ACCOUNT_SHOULD_NOT_LEAK",
        "BROKER_ORDER_SHOULD_NOT_LEAK",
        "RAW_REQUEST_SHOULD_NOT_LEAK",
        "RAW_RESPONSE_SHOULD_NOT_LEAK",
        "RAW_PAYLOAD_SHOULD_NOT_LEAK",
        "ACCESS_TOKEN_SHOULD_NOT_LEAK",
        "REFRESH_TOKEN_SHOULD_NOT_LEAK",
        "NESTED_AUTH_SHOULD_NOT_LEAK",
    ):
        assert value not in rendered


def test_integration_with_single_protected_live_micro_trade_fake_result_succeeds() -> None:
    payload = _build_ready_spine(realized_pnl=1.25)

    validation = module.validate_post_trade_result_input(payload)
    completion = module.build_post_trade_completion_packet(payload)

    assert validation["status"] == module.POST_TRADE_LEDGER_READY
    assert validation["trade_mode"] == module.POST_TRADE_RESULT_FAKE_ONLY
    assert validation["execution_summary"]["single_live_micro_trade_package_ready"] is True
    assert validation["result_summary"]["fake_order_executed"] is True
    assert completion["ready"] is True
    assert completion["build_lane_completion"] is True
    assert completion["real_trade_completion"] is False


def test_source_scan_proves_no_forbidden_execution_triggers() -> None:
    source = Path("automation/forex_engine/post_trade_ledger_replay_closeout_v1.py").read_text(
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
        "live_runtime_executor_v1.execute_single_live_micro_trade",
    )

    for snippet in forbidden_snippets:
        assert snippet not in source
