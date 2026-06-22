from __future__ import annotations

from pathlib import Path

from automation.forex_engine import protected_live_execution_command_package_v1 as command
from automation.forex_engine import single_protected_live_micro_trade_execution_package_v1 as package


class FakeSubmitter:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def place_live_micro_order(self, intent: dict) -> dict:
        self.calls.append(dict(intent))
        return {
            "submitted": True,
            "accepted": True,
            "instrument": intent["instrument"],
            "side": intent["side"],
            "units": intent["units"],
            "token": "TOKEN_SHOULD_NOT_LEAK",
            "authorization": "AUTH_SHOULD_NOT_LEAK",
            "account_id": "ACCOUNT_SHOULD_NOT_LEAK",
            "broker_order_id": "ORDER_SHOULD_NOT_LEAK",
            "raw_request": {"value": "RAW_REQUEST_SHOULD_NOT_LEAK"},
            "raw_response": {"value": "RAW_RESPONSE_SHOULD_NOT_LEAK"},
            "raw_payload": {"value": "RAW_PAYLOAD_SHOULD_NOT_LEAK"},
        }


def _authority(**overrides: object) -> dict:
    state = {
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
    state.update(overrides)
    return state


def _command_preflight(**overrides: object) -> dict:
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
        "max_loss_gate_clear": True,
        "daily_stop_clear": True,
        "kill_switch_enabled": False,
    }
    state.update(overrides)
    return state


def _sealed_command(**preflight_overrides: object) -> dict:
    ready = command.build_protected_live_execution_command(
        authority_state={
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
        },
        preflight_evidence=_command_preflight(**preflight_overrides),
        order_intent=_order(),
    )
    return command.seal_protected_live_execution_command(ready)


def _unsealed_command() -> dict:
    return command.build_protected_live_execution_command(
        authority_state={
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
        },
        preflight_evidence=_command_preflight(),
        order_intent=_order(),
    )


def _runtime(**overrides: object) -> dict:
    state = {
        "runtime_auth_provider_injected": True,
        "http_client_injected": True,
        "fake_client_mode": True,
        "fake_execution_selected": True,
        "allow_live_network_once": False,
        "protected_live_execution_command": False,
        "real_execution_forbidden_in_codex": True,
        "dry_run_only": False,
    }
    state.update(overrides)
    return state


def _ready_package(**overrides: object) -> dict:
    payload = {
        "authority_state": _authority(),
        "command_package": _sealed_command(),
        "runtime_inputs": _runtime(),
        "order_intent": _order(),
    }
    payload.update(overrides)
    return package.build_single_live_micro_trade_execution_package(**payload)


def test_missing_authority_returns_invalid_or_blocked() -> None:
    result = package.validate_single_live_micro_trade_authority(None)

    assert result["status"] in {
        package.SINGLE_LIVE_MICRO_TRADE_INVALID,
        package.SINGLE_LIVE_MICRO_TRADE_BLOCKED,
    }
    assert "authority_state_missing" in result["blockers"]


def test_missing_final_human_execution_approval_blocks() -> None:
    result = package.validate_single_live_micro_trade_authority(
        _authority(final_human_execution_approval=False)
    )

    assert result["status"] == package.SINGLE_LIVE_MICRO_TRADE_BLOCKED
    assert "final_human_execution_approval_required" in result["blockers"]


def test_missing_protected_action_authorization_blocks() -> None:
    result = package.validate_single_live_micro_trade_authority(
        _authority(protected_action_authorized=False)
    )

    assert result["status"] == package.SINGLE_LIVE_MICRO_TRADE_BLOCKED
    assert "protected_action_authorization_required" in result["blockers"]


def test_missing_sealed_command_blocks() -> None:
    result = package.validate_single_live_micro_trade_command(_unsealed_command())

    assert result["status"] == package.SINGLE_LIVE_MICRO_TRADE_BLOCKED
    assert "protected_command_not_sealed" in result["blockers"]


def test_missing_preflight_readiness_blocks() -> None:
    sealed = _sealed_command(live_preflight_ready=False)

    result = package.validate_single_live_micro_trade_command(sealed)

    assert result["status"] == package.SINGLE_LIVE_MICRO_TRADE_BLOCKED
    assert "live_preflight_not_ready" in result["blockers"]


def test_runtime_inputs_missing_auth_provider_block() -> None:
    result = package.validate_single_live_micro_trade_runtime_inputs(
        _runtime(runtime_auth_provider_injected=False)
    )

    assert result["status"] == package.SINGLE_LIVE_MICRO_TRADE_BLOCKED
    assert "runtime_auth_provider_injected_required" in result["blockers"]


def test_runtime_inputs_missing_http_client_block() -> None:
    result = package.validate_single_live_micro_trade_runtime_inputs(
        _runtime(http_client_injected=False)
    )

    assert result["status"] == package.SINGLE_LIVE_MICRO_TRADE_BLOCKED
    assert "http_client_injected_required" in result["blockers"]


def test_real_execution_flags_are_forbidden_in_codex() -> None:
    result = package.validate_single_live_micro_trade_runtime_inputs(
        _runtime(allow_live_network_once=True, protected_live_execution_command=True)
    )

    assert result["status"] == package.SINGLE_LIVE_MICRO_TRADE_BLOCKED
    assert "allow_live_network_once_forbidden_inside_codex" in result["blockers"]
    assert "protected_live_execution_command_forbidden_inside_codex" in result["blockers"]


def test_order_intent_missing_stop_loss_blocks() -> None:
    result = _ready_package(order_intent=_order(stop_loss=None))

    assert result["status"] == package.SINGLE_LIVE_MICRO_TRADE_BLOCKED
    assert "stop_loss_missing" in result["blockers"]


def test_order_intent_missing_take_profit_blocks() -> None:
    result = _ready_package(order_intent=_order(take_profit=""))

    assert result["status"] == package.SINGLE_LIVE_MICRO_TRADE_BLOCKED
    assert "take_profit_missing" in result["blockers"]


def test_order_intent_invalid_side_blocks() -> None:
    result = _ready_package(order_intent=_order(side="HOLD"))

    assert result["status"] == package.SINGLE_LIVE_MICRO_TRADE_BLOCKED
    assert "side_invalid" in result["blockers"]


def test_order_intent_units_above_1000_blocks() -> None:
    result = _ready_package(order_intent=_order(units=1001))

    assert result["status"] == package.SINGLE_LIVE_MICRO_TRADE_BLOCKED
    assert "units_above_micro_max" in result["blockers"]


def test_complete_fake_local_evidence_creates_ready_package() -> None:
    result = _ready_package()

    assert result["status"] == package.SINGLE_LIVE_MICRO_TRADE_READY
    assert result["ready"] is True
    assert result["fake_execution_available"] is True
    assert result["real_execution_forbidden_in_codex"] is True
    assert result["real_order_executed"] is False
    assert result["real_broker_call_performed"] is False


def test_fake_only_execution_returns_fake_submitted() -> None:
    ready = _ready_package()
    fake = FakeSubmitter()

    result = package.execute_single_live_micro_trade_fake_only(ready, fake_client=fake)

    assert result["status"] == package.SINGLE_LIVE_MICRO_TRADE_FAKE_SUBMITTED
    assert result["fake_broker_call_performed"] is True
    assert result["fake_order_executed"] is True
    assert result["real_broker_call_performed"] is False
    assert result["real_order_executed"] is False
    assert len(fake.calls) == 1


def test_fake_only_execution_blocks_second_order() -> None:
    ready = _ready_package()
    fake = FakeSubmitter()

    first = package.execute_single_live_micro_trade_fake_only(ready, fake_client=fake)
    second = package.execute_single_live_micro_trade_fake_only(ready, fake_client=fake)

    assert first["status"] == package.SINGLE_LIVE_MICRO_TRADE_FAKE_SUBMITTED
    assert second["status"] == package.SINGLE_LIVE_MICRO_TRADE_BLOCKED
    assert "second_order_blocked" in second["blockers"]
    assert len(fake.calls) == 1


def test_fake_result_evidence_distinguishes_fake_order_from_real_order() -> None:
    fake_output = package.execute_single_live_micro_trade_fake_only(_ready_package(), fake_client=FakeSubmitter())

    evidence = package.build_single_live_micro_trade_result_evidence(fake_output)

    assert evidence["status"] == package.SINGLE_LIVE_MICRO_TRADE_RESULT_READY
    assert evidence["fake_order_executed"] is True
    assert evidence["real_order_executed"] is False
    assert evidence["real_broker_call_performed"] is False


def test_fake_result_keeps_real_order_and_broker_call_false() -> None:
    fake_output = package.execute_single_live_micro_trade_fake_only(_ready_package(), fake_client=FakeSubmitter())
    fake_output["real_order_executed"] = True
    fake_output["real_broker_call_performed"] = True

    evidence = package.build_single_live_micro_trade_result_evidence(fake_output)

    assert evidence["real_order_executed"] is False
    assert evidence["real_broker_call_performed"] is False
    assert evidence["order_executed"] is False


def test_sanitized_output_never_includes_sensitive_values() -> None:
    fake_output = package.execute_single_live_micro_trade_fake_only(_ready_package(), fake_client=FakeSubmitter())
    sanitized = package.sanitize_single_live_micro_trade_result(
        {
            "credential": "CREDENTIAL_SHOULD_NOT_LEAK",
            "token": "TOKEN_SHOULD_NOT_LEAK",
            "authorization": "AUTH_SHOULD_NOT_LEAK",
            "account_id": "ACCOUNT_SHOULD_NOT_LEAK",
            "broker_order_id": "ORDER_SHOULD_NOT_LEAK",
            "raw_request": {"value": "RAW_REQUEST_SHOULD_NOT_LEAK"},
            "raw_response": {"value": "RAW_RESPONSE_SHOULD_NOT_LEAK"},
            "raw_payload": {"value": "RAW_PAYLOAD_SHOULD_NOT_LEAK"},
            "safe": fake_output,
        }
    )
    rendered = repr(sanitized)

    for value in (
        "CREDENTIAL_SHOULD_NOT_LEAK",
        "TOKEN_SHOULD_NOT_LEAK",
        "AUTH_SHOULD_NOT_LEAK",
        "ACCOUNT_SHOULD_NOT_LEAK",
        "ORDER_SHOULD_NOT_LEAK",
        "RAW_REQUEST_SHOULD_NOT_LEAK",
        "RAW_RESPONSE_SHOULD_NOT_LEAK",
        "RAW_PAYLOAD_SHOULD_NOT_LEAK",
    ):
        assert value not in rendered
    assert sanitized["credential_persisted"] is False
    assert sanitized["account_id_persisted"] is False
    assert sanitized["raw_broker_payload_persisted"] is False


def test_mobile_summary_includes_required_truth_fields() -> None:
    summary = _ready_package()["mobile_summary"]

    for key in (
        "status",
        "instrument",
        "side",
        "units",
        "stop_loss",
        "take_profit",
        "max_loss_gate",
        "daily_stop_gate",
        "kill_switch",
        "fake_execution_status",
        "real_execution_blocked_status",
        "next_safe_action",
    ):
        assert key in summary
    assert summary["instrument"] == "EUR_USD"
    assert summary["real_execution_blocked_status"] == (
        package.SINGLE_LIVE_MICRO_TRADE_REAL_EXECUTION_FORBIDDEN_IN_CODEX
    )


def test_integration_with_protected_live_command_package_fake_ready_output_succeeds() -> None:
    sealed = _sealed_command()

    result = package.build_single_live_micro_trade_execution_package(
        authority_state=_authority(),
        command_package=sealed,
        runtime_inputs=_runtime(),
        order_intent=_order(),
    )

    assert result["status"] == package.SINGLE_LIVE_MICRO_TRADE_READY
    assert result["sanitized_command_summary"]["protected_command_ready"] is True
    assert result["sanitized_command_summary"]["protected_command_sealed"] is True
    assert result["integration_summary"]["executor_request_status"] == "LIVE_RUNTIME_REQUEST_READY"


def test_source_scan_proves_no_forbidden_execution_triggers() -> None:
    source = Path(
        "automation/forex_engine/single_protected_live_micro_trade_execution_package_v1.py"
    ).read_text(encoding="utf-8").lower()
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
        "execute_requested=true",
        "execute_requested = true",
    )

    for snippet in forbidden_snippets:
        assert snippet not in source
