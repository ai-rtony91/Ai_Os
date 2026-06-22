import time

from automation.forex_engine.broker_demo_decision_bridge_v4 import (
    BROKER_DEMO_DECISION_BLOCKED,
    BROKER_DEMO_DECISION_INVALID,
    BROKER_DEMO_DECISION_READY,
    BROKER_DEMO_DECISION_REVIEW_REQUIRED,
    evaluate_broker_demo_decision,
)


def _integration_ready():
    return {"integration_ready": True, "ready": True, "verdict": BROKER_DEMO_DECISION_READY}


def _connector_ready():
    return {"connector_ready": True, "ready": True, "verdict": BROKER_DEMO_DECISION_READY}


def _demo_data_ready():
    return {"demo_data_ready": True, "ready": True, "verdict": "BROKER_DEMO_DATA_READY"}


def _base_gates():
    return {"kill_switch_enabled": False, "max_loss_gate_clear": True, "daily_stop_clear": True}


def test_ready_path_returns_ready():
    result = evaluate_broker_demo_decision(
        _integration_ready(),
        _connector_ready(),
        _demo_data_ready(),
        _base_gates(),
    )
    assert result["decision"] == BROKER_DEMO_DECISION_READY
    assert result["ready"] is True
    assert result["blockers"] == tuple()
    assert result["next_safe_action"] == "prepare_protected_demo_review_packet"


def test_missing_integration_evidence_returns_invalid():
    result = evaluate_broker_demo_decision(
        None,
        _connector_ready(),
        _demo_data_ready(),
        _base_gates(),
    )
    assert result["decision"] == BROKER_DEMO_DECISION_INVALID
    assert result["ready"] is False
    assert "integration_evidence_missing" in result["blockers"]
    assert result["next_safe_action"] == "repair_missing_or_invalid_evidence"


def test_blocked_connector_returns_blocked():
    blocked_connector = {"connector_ready": False, "ready": False, "verdict": "BROKER_CONNECTOR_BLOCKED"}
    result = evaluate_broker_demo_decision(
        _integration_ready(),
        blocked_connector,
        _demo_data_ready(),
        _base_gates(),
    )
    assert result["decision"] == BROKER_DEMO_DECISION_BLOCKED
    assert result["ready"] is False
    assert "connector_not_ready" in result["blockers"]
    assert result["next_safe_action"] == "resolve_blockers_before_demo_review"


def test_blocked_demo_data_returns_blocked():
    blocked_demo = {"demo_data_ready": False, "ready": False, "verdict": "BROKER_DEMO_DATA_BLOCKED"}
    result = evaluate_broker_demo_decision(
        _integration_ready(),
        _connector_ready(),
        blocked_demo,
        _base_gates(),
    )
    assert result["decision"] == BROKER_DEMO_DECISION_BLOCKED
    assert result["ready"] is False
    assert "demo_data_not_ready" in result["blockers"]


def test_kill_switch_blocks():
    gates = _base_gates()
    gates["kill_switch_enabled"] = True
    result = evaluate_broker_demo_decision(
        _integration_ready(),
        _connector_ready(),
        _demo_data_ready(),
        gates,
    )
    assert result["decision"] == BROKER_DEMO_DECISION_BLOCKED
    assert "kill_switch_enabled" in result["blockers"]


def test_unsafe_live_network_order_block():
    gates = _base_gates()
    gates["order_execution"] = True
    result = evaluate_broker_demo_decision(
        {**_integration_ready(), "live_trading": True},
        {**_connector_ready()},
        {**_demo_data_ready(), "network_calls": True},
        gates,
    )
    assert result["decision"] == BROKER_DEMO_DECISION_BLOCKED
    assert "unsafe_flag_live_trading" in result["blockers"]
    assert "unsafe_flag_order_execution" in result["blockers"]
    assert "unsafe_flag_network_calls" in result["blockers"]


def test_next_safe_action_mapping():
    ready_result = evaluate_broker_demo_decision(
        _integration_ready(),
        _connector_ready(),
        _demo_data_ready(),
        _base_gates(),
    )
    blocked_result = evaluate_broker_demo_decision(
        _integration_ready(),
        {"connector_ready": False},
        _demo_data_ready(),
        _base_gates(),
    )
    assert ready_result["next_safe_action"] == "prepare_protected_demo_review_packet"
    assert blocked_result["next_safe_action"] == "resolve_blockers_before_demo_review"


def test_review_required_next_action_for_unknown_data():
    result = evaluate_broker_demo_decision(
        {"integration_ready": True, "ready": True},
        {"connector_ready": True, "ready": True},
        {"demo_data_ready": True, "ready": True, "verdict": "BROKER_DEMO_DATA_SANITIZED"},
        _base_gates(),
    )
    assert result["decision"] == BROKER_DEMO_DECISION_REVIEW_REQUIRED
    assert result["ready"] is False
    assert result["next_safe_action"] == "human_review_required"


def test_latency_budget_excludes_network_marker():
    result = evaluate_broker_demo_decision(
        _integration_ready(),
        _connector_ready(),
        _demo_data_ready(),
        _base_gates(),
    )
    assert result["latency_budget"]["network_latency_ms"] == "excluded_offline_default"
    assert result["latency_budget"]["integration_evidence_read_ms"] >= 0.0
    assert result["latency_budget"]["decision_mapping_ms"] >= 0.0

