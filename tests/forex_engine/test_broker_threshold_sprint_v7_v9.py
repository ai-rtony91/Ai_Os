from __future__ import annotations

from automation.forex_engine.broker_demo_rehearsal_runner_v6 import (
    BROKER_DEMO_REHEARSAL_READY,
)
from automation.forex_engine.broker_threshold_sprint_v7_v9 import (
    DEMO_MICRO_TRADE_PACKET_BLOCKED,
    DEMO_MICRO_TRADE_PACKET_INVALID,
    DEMO_MICRO_TRADE_PACKET_READY,
    DEMO_MICRO_TRADE_PACKET_REVIEW_REQUIRED,
    PROTECTED_DEMO_PREFLIGHT_BLOCKED,
    PROTECTED_DEMO_PREFLIGHT_INVALID,
    PROTECTED_DEMO_PREFLIGHT_READY,
    PROTECTED_DEMO_PREFLIGHT_REVIEW_REQUIRED,
    PROTECTED_DEMO_READONLY_CONTROLLER_BLOCKED,
    PROTECTED_DEMO_READONLY_CONTROLLER_INVALID,
    PROTECTED_DEMO_READONLY_CONTROLLER_READY,
    PROTECTED_DEMO_READONLY_CONTROLLER_REVIEW_REQUIRED,
    evaluate_protected_demo_connection_preflight,
    build_protected_demo_readonly_attempt_controller,
    build_demo_micro_trade_approval_packet,
)


def _ready_rehearsal_result() -> dict:
    return {
        "rehearsal_schema": "AIOS_BROKER_DEMO_REHEARSAL_RUNNER_V6A.v1",
        "rehearsal_status": BROKER_DEMO_REHEARSAL_READY,
        "ready": True,
    }


def _ready_connection_request() -> dict:
    return {
        "operator_approved": True,
        "demo_only": True,
        "simulation_or_preflight_only": True,
        "network_requested": False,
        "credentials_supplied_runtime_only": True,
        "credentials_persisted": False,
        "account_id_persisted": False,
        "endpoint_classification": "PRACTICE_DEMO",
        "order_execution_requested": False,
        "read_only_requested": True,
    }


def _ready_runtime_auth() -> dict:
    return {
        "explicit_operator_runtime_approval": True,
        "allow_demo_network_once": True,
        "read_only_scope_only": True,
        "no_order_scope_ack": True,
        "credentials_runtime_only_ack": True,
        "no_secret_persistence_ack": True,
    }


def _ready_trade_candidate() -> dict:
    return {
        "instrument": "EUR_USD",
        "side": "BUY",
        "units": 100,
        "risk_cap": 10,
        "stop_loss_placeholder": 1.0900,
        "take_profit_placeholder": 1.0950,
        "max_loss_gate_clear": True,
        "daily_stop_clear": True,
        "kill_switch_enabled": False,
        "simulation_only": True,
        "broker_demo_only": True,
    }


def _ready_approval() -> dict:
    return {
        "human_approved_demo_micro_trade": True,
        "single_trade_only": True,
        "micro_size_ack": True,
        "no_live_trade_ack": True,
        "demo_only_ack": True,
    }


def test_preflight_ready_path():
    result = evaluate_protected_demo_connection_preflight(
        _ready_rehearsal_result(),
        connection_request=_ready_connection_request(),
    )

    assert result["preflight_status"] == PROTECTED_DEMO_PREFLIGHT_READY
    assert result["ready"] is True
    assert result["next_safe_action"] == "prepare_protected_readonly_attempt_controller"


def test_preflight_missing_rehearsal_is_invalid():
    result = evaluate_protected_demo_connection_preflight(None, connection_request=_ready_connection_request())

    assert result["preflight_status"] == PROTECTED_DEMO_PREFLIGHT_INVALID
    assert result["ready"] is False


def test_preflight_missing_operator_approval_is_review_required():
    request = _ready_connection_request()
    request["operator_approved"] = False

    result = evaluate_protected_demo_connection_preflight(
        _ready_rehearsal_result(),
        connection_request=request,
    )

    assert result["preflight_status"] == PROTECTED_DEMO_PREFLIGHT_REVIEW_REQUIRED
    assert result["next_safe_action"] == "obtain_operator_preflight_approval"


def test_preflight_live_endpoint_blocked():
    request = _ready_connection_request()
    request["endpoint_classification"] = "LIVE"

    result = evaluate_protected_demo_connection_preflight(
        _ready_rehearsal_result(),
        connection_request=request,
    )

    assert result["preflight_status"] == PROTECTED_DEMO_PREFLIGHT_BLOCKED
    assert "endpoint_not_practice_demo" in result["blockers"]


def test_preflight_persisted_credentials_blocked():
    request = _ready_connection_request()
    request["credentials_persisted"] = True

    result = evaluate_protected_demo_connection_preflight(
        _ready_rehearsal_result(),
        connection_request=request,
    )

    assert result["preflight_status"] == PROTECTED_DEMO_PREFLIGHT_BLOCKED
    assert "credentials_persisted_blocked" in result["blockers"]


def test_preflight_order_execution_request_blocked():
    request = _ready_connection_request()
    request["order_execution_requested"] = True

    result = evaluate_protected_demo_connection_preflight(
        _ready_rehearsal_result(),
        connection_request=request,
    )

    assert result["preflight_status"] == PROTECTED_DEMO_PREFLIGHT_BLOCKED
    assert "order_execution_requested_blocked" in result["blockers"]


def test_controller_ready_path():
    preflight = evaluate_protected_demo_connection_preflight(
        _ready_rehearsal_result(),
        connection_request=_ready_connection_request(),
    )
    controller = build_protected_demo_readonly_attempt_controller(preflight, _ready_runtime_auth())

    assert controller["controller_status"] == PROTECTED_DEMO_READONLY_CONTROLLER_READY
    assert controller["ready"] is True
    assert controller["next_safe_action"] == "execute_explicit_readonly_demo_connection_in_separate_authorized_runtime"


def test_controller_missing_runtime_authorization_review_required():
    preflight = evaluate_protected_demo_connection_preflight(
        _ready_rehearsal_result(),
        connection_request=_ready_connection_request(),
    )
    controller = build_protected_demo_readonly_attempt_controller(preflight)

    assert controller["controller_status"] == PROTECTED_DEMO_READONLY_CONTROLLER_REVIEW_REQUIRED
    assert controller["next_safe_action"] == "obtain_runtime_authorization"


def test_controller_network_auth_missing_blocked():
    preflight = evaluate_protected_demo_connection_preflight(
        _ready_rehearsal_result(),
        connection_request=_ready_connection_request(),
    )
    auth = _ready_runtime_auth()
    auth["allow_demo_network_once"] = False
    controller = build_protected_demo_readonly_attempt_controller(preflight, auth)

    assert controller["controller_status"] == PROTECTED_DEMO_READONLY_CONTROLLER_BLOCKED
    assert "demo_network_once_not_authorized" in controller["blockers"]


def test_controller_order_scope_blocked():
    preflight = evaluate_protected_demo_connection_preflight(
        _ready_rehearsal_result(),
        connection_request=_ready_connection_request(),
    )
    auth = _ready_runtime_auth()
    auth["no_order_scope_ack"] = False
    controller = build_protected_demo_readonly_attempt_controller(preflight, auth)

    assert controller["controller_status"] == PROTECTED_DEMO_READONLY_CONTROLLER_BLOCKED
    assert "no_order_scope_not_acknowledged" in controller["blockers"]


def test_micro_trade_ready_packet():
    preflight = evaluate_protected_demo_connection_preflight(
        _ready_rehearsal_result(),
        connection_request=_ready_connection_request(),
    )
    controller = build_protected_demo_readonly_attempt_controller(preflight, _ready_runtime_auth())
    packet = build_demo_micro_trade_approval_packet(
        controller,
        trade_candidate=_ready_trade_candidate(),
        approval=_ready_approval(),
    )

    assert packet["packet_status"] == DEMO_MICRO_TRADE_PACKET_READY
    assert packet["ready"] is True
    assert packet["next_safe_action"] == "await_explicit_operator_command_for_demo_micro_trade_execution"


def test_micro_trade_missing_approval_review_required():
    preflight = evaluate_protected_demo_connection_preflight(
        _ready_rehearsal_result(),
        connection_request=_ready_connection_request(),
    )
    controller = build_protected_demo_readonly_attempt_controller(preflight, _ready_runtime_auth())
    packet = build_demo_micro_trade_approval_packet(
        controller,
        trade_candidate=_ready_trade_candidate(),
    )

    assert packet["packet_status"] == DEMO_MICRO_TRADE_PACKET_REVIEW_REQUIRED
    assert packet["next_safe_action"] == "obtain_demo_micro_trade_human_approval"


def test_micro_trade_kill_switch_blocks():
    preflight = evaluate_protected_demo_connection_preflight(
        _ready_rehearsal_result(),
        connection_request=_ready_connection_request(),
    )
    controller = build_protected_demo_readonly_attempt_controller(preflight, _ready_runtime_auth())
    trade = _ready_trade_candidate()
    trade["kill_switch_enabled"] = True
    packet = build_demo_micro_trade_approval_packet(
        controller,
        trade_candidate=trade,
        approval=_ready_approval(),
    )

    assert packet["packet_status"] == DEMO_MICRO_TRADE_PACKET_BLOCKED
    assert "kill_switch_enabled" in packet["blockers"]


def test_micro_trade_max_loss_or_daily_stop_blocked():
    preflight = evaluate_protected_demo_connection_preflight(
        _ready_rehearsal_result(),
        connection_request=_ready_connection_request(),
    )
    controller = build_protected_demo_readonly_attempt_controller(preflight, _ready_runtime_auth())

    trade = _ready_trade_candidate()
    trade["max_loss_gate_clear"] = False
    packet = build_demo_micro_trade_approval_packet(
        controller,
        trade_candidate=trade,
        approval=_ready_approval(),
    )
    assert packet["packet_status"] == DEMO_MICRO_TRADE_PACKET_BLOCKED

    trade["max_loss_gate_clear"] = True
    trade["daily_stop_clear"] = False
    packet = build_demo_micro_trade_approval_packet(
        controller,
        trade_candidate=trade,
        approval=_ready_approval(),
    )
    assert packet["packet_status"] == DEMO_MICRO_TRADE_PACKET_BLOCKED


def test_micro_trade_non_demo_ack_failure_blocks():
    preflight = evaluate_protected_demo_connection_preflight(
        _ready_rehearsal_result(),
        connection_request=_ready_connection_request(),
    )
    controller = build_protected_demo_readonly_attempt_controller(preflight, _ready_runtime_auth())
    approval = _ready_approval()
    approval["demo_only_ack"] = False
    packet = build_demo_micro_trade_approval_packet(
        controller,
        trade_candidate=_ready_trade_candidate(),
        approval=approval,
    )

    assert packet["packet_status"] == DEMO_MICRO_TRADE_PACKET_BLOCKED
    assert "demo_only_ack_required" in packet["blockers"]


def test_micro_trade_packet_does_not_report_execution_or_network():
    preflight = evaluate_protected_demo_connection_preflight(
        _ready_rehearsal_result(),
        connection_request=_ready_connection_request(),
    )
    controller = build_protected_demo_readonly_attempt_controller(preflight, _ready_runtime_auth())
    packet = build_demo_micro_trade_approval_packet(
        controller,
        trade_candidate=_ready_trade_candidate(),
        approval=_ready_approval(),
    )

    assert packet["safety_summary"]["order_execution"] is False
    assert packet["safety_summary"]["network_calls"] is False
    assert packet["packet_status"] in {
        DEMO_MICRO_TRADE_PACKET_READY,
        DEMO_MICRO_TRADE_PACKET_BLOCKED,
    }


def test_cross_chain_ready_preflight_controller_micro_trade_chain():
    preflight = evaluate_protected_demo_connection_preflight(
        _ready_rehearsal_result(),
        connection_request=_ready_connection_request(),
    )
    assert preflight["preflight_status"] == PROTECTED_DEMO_PREFLIGHT_READY

    controller = build_protected_demo_readonly_attempt_controller(preflight, _ready_runtime_auth())
    assert controller["controller_status"] == PROTECTED_DEMO_READONLY_CONTROLLER_READY

    packet = build_demo_micro_trade_approval_packet(
        controller,
        trade_candidate=_ready_trade_candidate(),
        approval=_ready_approval(),
    )
    assert packet["packet_status"] == DEMO_MICRO_TRADE_PACKET_READY
    assert preflight["latency_budget"]["network_latency_ms"] == "excluded_offline_default"
    assert controller["latency_budget"]["network_latency_ms"] == "excluded_offline_default"
    assert packet["latency_budget"]["network_latency_ms"] == "excluded_offline_default"


def test_invalid_input_classification_includes_ban():
    preflight = evaluate_protected_demo_connection_preflight(
        {},
        connection_request={"operator_approved": True},
    )
    assert preflight["preflight_status"] == PROTECTED_DEMO_PREFLIGHT_INVALID

    controller = build_protected_demo_readonly_attempt_controller(preflight, _ready_runtime_auth())
    assert controller["controller_status"] == PROTECTED_DEMO_READONLY_CONTROLLER_INVALID

    packet = build_demo_micro_trade_approval_packet(controller)
    assert packet["packet_status"] == DEMO_MICRO_TRADE_PACKET_INVALID
