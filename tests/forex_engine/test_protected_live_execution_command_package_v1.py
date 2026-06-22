from __future__ import annotations

from pathlib import Path

from automation.forex_engine import final_live_operator_bridge_v1 as bridge
from automation.forex_engine import live_preflight_evidence_bundle_v1 as preflight
from automation.forex_engine import oanda_live_http_transport_v1 as transport
from automation.forex_engine import oanda_live_runtime_connector_v2 as connector
from automation.forex_engine import protected_live_execution_command_package_v1 as command
from automation.forex_engine import protected_runtime_credential_injection_v1 as injection


def _authority(**overrides: object) -> dict:
    state = {
        "authenticated_operator": True,
        "protected_action_authorized": True,
        "live_exception_requested": True,
        "understands_live_risk_ack": True,
        "operator_approved_live_runtime": True,
        "final_execute_live_order_command_ack": True,
        "one_trade_only": True,
        "micro_size_only": True,
        "no_retry": True,
        "no_loop": True,
        "max_order_count": 1,
        "protected_live_execution_command": False,
        "execution_requested": False,
    }
    state.update(overrides)
    return state


def _preflight(**overrides: object) -> dict:
    state = {
        "live_preflight_ready": True,
        "final_bridge_ready": True,
        "runtime_injection_ready": True,
        "oanda_connector_ready": True,
        "oanda_transport_ready": True,
        "account_risk_ready": True,
        "instrument_ready": True,
        "quote_spread_ready": True,
        "order_intent_ready": True,
        "mobile_operator_ready": True,
        "max_loss_gate_clear": True,
        "daily_stop_clear": True,
        "kill_switch_enabled": False,
        "credential_persisted": False,
        "account_id_persisted": False,
        "broker_call_performed": False,
        "order_executed": False,
        "execution_allowed": False,
    }
    state.update(overrides)
    return state


def _order(**overrides: object) -> dict:
    state = {
        "instrument": "EUR_USD",
        "side": "BUY",
        "units": 10,
        "stop_loss": "1.0780",
        "take_profit": "1.0840",
        "risk_reward_ratio": 2.0,
        "risk_cap_confirmed": True,
        "stop_loss_confirmed": True,
        "take_profit_confirmed": True,
        "one_trade_only": True,
        "micro_size_only": True,
    }
    state.update(overrides)
    return state


def _ready_command() -> dict:
    return command.build_protected_live_execution_command(
        authority_state=_authority(),
        preflight_evidence=_preflight(),
        order_intent=_order(),
    )


def _account() -> dict:
    return {
        "account_currency": "USD",
        "balance": 10000.0,
        "equity": 10000.0,
        "margin_available": 9000.0,
        "open_risk": 0.0,
        "max_loss_gate_clear": True,
        "daily_stop_clear": True,
        "kill_switch_enabled": False,
        "portfolio_exposure_clear": True,
        "micro_risk_cap_amount": 5.0,
        "account_id_present": False,
        "account_id_persisted": False,
    }


def _instrument() -> dict:
    return {
        "instrument": "EUR_USD",
        "trade_enabled": True,
        "market_open": True,
        "instrument_supported": True,
        "min_units": 1,
        "max_units": 1000,
        "requested_units": 10,
    }


def _quote() -> dict:
    return {
        "bid": 1.0800,
        "ask": 1.0802,
        "spread": 0.0002,
        "max_spread": 0.0005,
        "quote_fresh": True,
        "quote_age_seconds": 2,
        "max_quote_age_seconds": 10,
        "market_data_source_verified": True,
        "broker_call_performed": False,
    }


def _operator() -> dict:
    return {
        "authenticated_operator": True,
        "protected_action_authorized": True,
        "live_exception_requested": True,
        "understands_live_risk_ack": True,
        "operator_approved_live_runtime": True,
        "credential_persisted": False,
        "account_id_persisted": False,
        "no_default_network": True,
        "no_retry": True,
        "no_loop": True,
        "one_order_only": True,
        "execution_requested": False,
        "order_executed": False,
        "broker_call_performed": False,
    }


def _preflight_bundle() -> dict:
    return preflight.build_live_preflight_evidence_bundle(
        final_bridge_state={
            "bridge_status": bridge.FINAL_LIVE_OPERATOR_BRIDGE_READY,
            "ready": True,
            "final_bridge_ready": True,
        },
        runtime_injection_state={
            "status": injection.PROTECTED_RUNTIME_INJECTION_READY,
            "ready": True,
            "runtime_injection_ready": True,
        },
        oanda_connector_state=connector.build_oanda_live_connector_config(
            {
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
        ),
        oanda_transport_state=transport.build_oanda_live_http_transport_config(
            {
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
        ),
        account_risk_envelope=_account(),
        instrument_envelope=_instrument(),
        quote_spread_envelope=_quote(),
        order_intent_envelope=_order(),
        mobile_operator_state={"mobile_operator_ready": True},
        operator_state=_operator(),
    )


def test_missing_authority_returns_invalid_or_blocked() -> None:
    result = command.validate_live_command_authority(None)

    assert result["status"] in {
        command.PROTECTED_LIVE_COMMAND_INVALID,
        command.PROTECTED_LIVE_COMMAND_BLOCKED,
    }
    assert "authority_state_missing" in result["blockers"]


def test_missing_authenticated_operator_blocks() -> None:
    result = command.validate_live_command_authority(_authority(authenticated_operator=False))

    assert result["status"] == command.PROTECTED_LIVE_COMMAND_BLOCKED
    assert "authenticated_operator_required" in result["blockers"]


def test_missing_protected_action_authorization_blocks() -> None:
    result = command.validate_live_command_authority(_authority(protected_action_authorized=False))

    assert result["status"] == command.PROTECTED_LIVE_COMMAND_BLOCKED
    assert "protected_action_authorization_required" in result["blockers"]


def test_missing_live_exception_request_blocks() -> None:
    result = command.validate_live_command_authority(_authority(live_exception_requested=False))

    assert result["status"] == command.PROTECTED_LIVE_COMMAND_BLOCKED
    assert "live_exception_request_required" in result["blockers"]


def test_missing_final_live_command_acknowledgement_blocks() -> None:
    result = command.validate_live_command_authority(_authority(final_execute_live_order_command_ack=False))

    assert result["status"] == command.PROTECTED_LIVE_COMMAND_BLOCKED
    assert "final_live_command_ack_required" in result["blockers"]


def test_max_order_count_not_equal_to_one_blocks() -> None:
    result = command.validate_live_command_authority(_authority(max_order_count=2))

    assert result["status"] == command.PROTECTED_LIVE_COMMAND_BLOCKED
    assert "max_order_count_must_equal_one" in result["blockers"]


def test_preflight_not_ready_blocks() -> None:
    result = command.validate_live_command_preflight(_preflight(live_preflight_ready=False))

    assert result["status"] == command.PROTECTED_LIVE_COMMAND_BLOCKED
    assert "live_preflight_not_ready" in result["blockers"]


def test_kill_switch_enabled_blocks() -> None:
    result = command.validate_live_command_preflight(_preflight(kill_switch_enabled=True))

    assert result["status"] == command.PROTECTED_LIVE_COMMAND_BLOCKED
    assert "kill_switch_enabled" in result["blockers"]


def test_daily_stop_blocked_blocks() -> None:
    result = command.validate_live_command_preflight(_preflight(daily_stop_clear=False))

    assert result["status"] == command.PROTECTED_LIVE_COMMAND_BLOCKED
    assert "daily_stop_not_clear" in result["blockers"]


def test_max_loss_blocked_blocks() -> None:
    result = command.validate_live_command_preflight(_preflight(max_loss_gate_clear=False))

    assert result["status"] == command.PROTECTED_LIVE_COMMAND_BLOCKED
    assert "max_loss_gate_not_clear" in result["blockers"]


def test_credential_persisted_true_blocks() -> None:
    result = command.validate_live_command_preflight(_preflight(credential_persisted=True))

    assert result["status"] == command.PROTECTED_LIVE_COMMAND_BLOCKED
    assert "credential_persisted_blocked" in result["blockers"]


def test_account_id_persisted_true_blocks() -> None:
    result = command.validate_live_command_preflight(_preflight(account_id_persisted=True))

    assert result["status"] == command.PROTECTED_LIVE_COMMAND_BLOCKED
    assert "account_id_persisted_blocked" in result["blockers"]


def test_order_intent_missing_stop_loss_blocks() -> None:
    result = command.validate_live_command_order_intent(_order(stop_loss=None))

    assert result["status"] == command.PROTECTED_LIVE_COMMAND_BLOCKED
    assert "stop_loss_missing" in result["blockers"]


def test_order_intent_missing_take_profit_blocks() -> None:
    result = command.validate_live_command_order_intent(_order(take_profit=""))

    assert result["status"] == command.PROTECTED_LIVE_COMMAND_BLOCKED
    assert "take_profit_missing" in result["blockers"]


def test_order_intent_invalid_side_blocks() -> None:
    result = command.validate_live_command_order_intent(_order(side="HOLD"))

    assert result["status"] == command.PROTECTED_LIVE_COMMAND_BLOCKED
    assert "side_invalid" in result["blockers"]


def test_order_intent_units_above_1000_blocks() -> None:
    result = command.validate_live_command_order_intent(_order(units=1001))

    assert result["status"] == command.PROTECTED_LIVE_COMMAND_BLOCKED
    assert "units_above_micro_max" in result["blockers"]


def test_complete_fake_local_evidence_creates_ready_command() -> None:
    result = _ready_command()

    assert result["command_status"] == command.PROTECTED_LIVE_COMMAND_READY
    assert result["ready"] is True
    assert result["execution_requested"] is False
    assert result["execution_allowed"] is False
    assert result["order_executed"] is False
    assert result["broker_call_performed"] is False


def test_sealing_ready_command_creates_sealed_status() -> None:
    result = command.seal_protected_live_execution_command(_ready_command())

    assert result["command_status"] == command.PROTECTED_LIVE_COMMAND_SEALED
    assert result["sealed"] == command.PROTECTED_LIVE_COMMAND_SEALED
    assert result["ready"] is True


def test_sealed_command_keeps_execution_disabled() -> None:
    result = command.seal_protected_live_execution_command(_ready_command())

    assert result["execution_requested"] is False
    assert result["execution_allowed"] is False
    assert result["order_executed"] is False
    assert result["broker_call_performed"] is False
    assert result["sanitized_command"]["execution_requested"] is False
    assert result["sanitized_command"]["execution_allowed"] is False


def test_executor_request_preview_is_preview_only_and_performs_no_execution() -> None:
    sealed = command.seal_protected_live_execution_command(_ready_command())
    result = command.build_live_runtime_executor_request_preview(sealed)

    assert result["preview_only"] is True
    assert result["execute_requested"] is False
    assert result["order_executed"] is False
    assert result["broker_call_performed"] is False
    assert result["runtime_execution_request"]["broker_call_performed"] is False
    assert result["runtime_execution_request"]["order_executed"] is False


def test_sanitized_output_never_includes_sensitive_values() -> None:
    result = command.build_protected_live_execution_command(
        authority_state={**_authority(), "token": "TOKEN_SHOULD_NOT_LEAK"},
        preflight_evidence={
            **_preflight(),
            "authorization": "AUTH_SHOULD_NOT_LEAK",
            "account_id": "ACCOUNT_SHOULD_NOT_LEAK",
            "broker_order_id": "BROKER_ORDER_SHOULD_NOT_LEAK",
            "raw_request": {"value": "RAW_REQUEST_SHOULD_NOT_LEAK"},
            "raw_response": {"value": "RAW_RESPONSE_SHOULD_NOT_LEAK"},
            "raw_payload": {"value": "RAW_PAYLOAD_SHOULD_NOT_LEAK"},
        },
        order_intent={**_order(), "credentials": {"value": "CREDENTIAL_SHOULD_NOT_LEAK"}},
    )
    rendered = repr(result)

    for value in (
        "TOKEN_SHOULD_NOT_LEAK",
        "AUTH_SHOULD_NOT_LEAK",
        "ACCOUNT_SHOULD_NOT_LEAK",
        "BROKER_ORDER_SHOULD_NOT_LEAK",
        "RAW_REQUEST_SHOULD_NOT_LEAK",
        "RAW_RESPONSE_SHOULD_NOT_LEAK",
        "RAW_PAYLOAD_SHOULD_NOT_LEAK",
        "CREDENTIAL_SHOULD_NOT_LEAK",
    ):
        assert value not in rendered
    assert result["credential_persisted"] is False
    assert result["account_id_persisted"] is False
    assert result["raw_broker_payload_persisted"] is False


def test_mobile_summary_includes_required_truth_fields() -> None:
    summary = _ready_command()["mobile_summary"]

    for key in (
        "command_status",
        "sealed_status",
        "instrument",
        "side",
        "units",
        "stop_loss",
        "take_profit",
        "max_loss_gate",
        "daily_stop_gate",
        "kill_switch",
        "execution_allowed",
        "next_safe_action",
    ):
        assert key in summary
    assert summary["instrument"] == "EUR_USD"
    assert summary["execution_allowed"] is False


def test_integration_with_live_preflight_evidence_bundle_fake_ready_output_succeeds() -> None:
    result = command.build_protected_live_execution_command(
        authority_state=_authority(),
        preflight_evidence=_preflight_bundle(),
        order_intent=_order(),
    )

    assert result["command_status"] == command.PROTECTED_LIVE_COMMAND_READY
    assert result["preflight_summary"]["live_preflight_ready"] is True
    assert result["integration_summary"]["executor_request_status"] == "LIVE_RUNTIME_REQUEST_READY"


def test_source_scan_proves_no_forbidden_execution_triggers() -> None:
    source = Path("automation/forex_engine/protected_live_execution_command_package_v1.py").read_text(
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
        "execute_single_live_micro_trade",
        "execute_requested=true",
        "execute_requested = true",
    )

    for snippet in forbidden_snippets:
        assert snippet not in source
