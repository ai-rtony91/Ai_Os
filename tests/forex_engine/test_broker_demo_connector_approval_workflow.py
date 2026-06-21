from __future__ import annotations

from automation.forex_engine.broker_demo_connector_approval_workflow import (
    APPROVAL_WORKFLOW_BLOCKED,
    APPROVAL_WORKFLOW_EXPIRED,
    APPROVAL_WORKFLOW_INCOMPLETE,
    APPROVAL_WORKFLOW_REJECTED,
    APPROVAL_WORKFLOW_REVIEW_READY,
    APPROVAL_WORKFLOW_REVOKED,
    evaluate_broker_demo_connector_approval_workflow,
)


def _base_state():
    return {
        "protected_connector_gate_status": "PROTECTED_CONNECTOR_GATE_REVIEW_READY",
        "broker_demo_runtime_review_status": "BROKER_DEMO_RUNTIME_REVIEW_READY",
        "runtime_connector_status": "RUNTIME_CONNECTOR_REVIEW_READY",
        "connector_contract_status": "CONNECTOR_CONTRACT_REVIEW_READY",
        "approval_request_present": True,
        "approval_trace": {"id": "trace-1"},
        "approval_evidence_bundle": ["evidence-1"],
        "approval_window_active": True,
        "approval_timestamp": "2026-06-21T10:00:00Z",
        "approval_freshness": 120,
        "approval_scope": "demo-connector",
        "approval_reviewer": "risk-ops",
        "approval_expiration": "2026-06-21T11:00:00Z",
        "approval_revocation_path": {"approved": False},
        "approval_audit_record": {"step": "preflight"},
        "replay_prevention": {"enabled": True},
        "kill_switch_proof": {"enabled": True},
        "rollback_proof": {"enabled": True},
        "reconciliation_proof": {"enabled": True},
        "final_disarm_proof": {"enabled": True},
        "one_shot_controls": {"enabled": True},
        "broker_connection_detected": False,
        "network_access_detected": False,
        "credential_access_detected": False,
        "account_identifier_access_detected": False,
        "order_execution_detected": False,
        "live_trading_authorization_detected": False,
        "execution_authority_detected": False,
        "capital_allocation_detected": False,
    }


def test_empty_state_blocks():
    out = evaluate_broker_demo_connector_approval_workflow({})
    assert out["approval_workflow_status"] == APPROVAL_WORKFLOW_INCOMPLETE
    assert out["approval_workflow_review_ready"] is False
    assert out["approval_workflow_blocked"] is False
    assert out["approval_workflow_completed"] is False
    assert len(out["approval_workflow_blockers"]) >= 4


def test_complete_state_review_ready():
    result = evaluate_broker_demo_connector_approval_workflow(_base_state())
    assert result["approval_workflow_status"] == APPROVAL_WORKFLOW_REVIEW_READY
    assert result["approval_workflow_review_ready"] is True
    assert result["approval_workflow_blocked"] is False
    assert result["approval_workflow_completed"] is True


def test_missing_protected_connector_gate_blocks():
    state = _base_state()
    state["protected_connector_gate_status"] = None
    result = evaluate_broker_demo_connector_approval_workflow(state)
    assert result["approval_workflow_status"] == APPROVAL_WORKFLOW_INCOMPLETE
    assert "missing_protected_connector_gate" in result["approval_workflow_blockers"]


def test_missing_broker_demo_runtime_review_blocks():
    state = _base_state()
    state["broker_demo_runtime_review_status"] = None
    result = evaluate_broker_demo_connector_approval_workflow(state)
    assert "missing_broker_demo_runtime_review" in result["approval_workflow_blockers"]


def test_missing_runtime_connector_blocks():
    state = _base_state()
    state["runtime_connector_status"] = None
    result = evaluate_broker_demo_connector_approval_workflow(state)
    assert "missing_runtime_connector" in result["approval_workflow_blockers"]


def test_missing_connector_contract_blocks():
    state = _base_state()
    state["connector_contract_status"] = None
    result = evaluate_broker_demo_connector_approval_workflow(state)
    assert "missing_connector_contract" in result["approval_workflow_blockers"]


def test_missing_approval_request_blocks():
    state = _base_state()
    state["approval_request_present"] = False
    result = evaluate_broker_demo_connector_approval_workflow(state)
    assert result["approval_workflow_status"] == APPROVAL_WORKFLOW_REJECTED
    assert result["approval_workflow_blocked"] is False
    assert "missing_approval_request" in result["approval_workflow_blockers"]


def test_missing_approval_trace_blocks():
    state = _base_state()
    del state["approval_trace"]
    result = evaluate_broker_demo_connector_approval_workflow(state)
    assert "missing_approval_trace" in result["approval_workflow_blockers"]


def test_missing_approval_evidence_bundle_blocks():
    state = _base_state()
    del state["approval_evidence_bundle"]
    result = evaluate_broker_demo_connector_approval_workflow(state)
    assert "missing_approval_evidence_bundle" in result["approval_workflow_blockers"]


def test_inactive_approval_window_includes_incomplete():
    state = _base_state()
    state["approval_window_active"] = False
    result = evaluate_broker_demo_connector_approval_workflow(state)
    assert result["approval_workflow_status"] == APPROVAL_WORKFLOW_INCOMPLETE
    assert "approval_window_inactive" in result["approval_workflow_blockers"]


def test_missing_approval_timestamp_blocks():
    state = _base_state()
    state["approval_timestamp"] = None
    result = evaluate_broker_demo_connector_approval_workflow(state)
    assert "missing_approval_timestamp" in result["approval_workflow_blockers"]


def test_missing_approval_freshness_blocks():
    state = _base_state()
    state["approval_freshness"] = None
    result = evaluate_broker_demo_connector_approval_workflow(state)
    assert "missing_approval_freshness" in result["approval_workflow_blockers"]


def test_missing_approval_scope_blocks():
    state = _base_state()
    state["approval_scope"] = None
    result = evaluate_broker_demo_connector_approval_workflow(state)
    assert "missing_approval_scope" in result["approval_workflow_blockers"]


def test_missing_approval_reviewer_blocks():
    state = _base_state()
    state["approval_reviewer"] = None
    result = evaluate_broker_demo_connector_approval_workflow(state)
    assert "missing_approval_reviewer" in result["approval_workflow_blockers"]


def test_missing_approval_expiration_blocks():
    state = _base_state()
    state["approval_expiration"] = None
    result = evaluate_broker_demo_connector_approval_workflow(state)
    assert "missing_approval_expiration" in result["approval_workflow_blockers"]


def test_missing_approval_revocation_path_blocks():
    state = _base_state()
    state["approval_revocation_path"] = None
    result = evaluate_broker_demo_connector_approval_workflow(state)
    assert "missing_approval_revocation_path" in result["approval_workflow_blockers"]


def test_missing_approval_audit_record_blocks():
    state = _base_state()
    state["approval_audit_record"] = None
    result = evaluate_broker_demo_connector_approval_workflow(state)
    assert "missing_approval_audit_record" in result["approval_workflow_blockers"]


def test_missing_replay_prevention_blocks():
    state = _base_state()
    state["replay_prevention"] = None
    result = evaluate_broker_demo_connector_approval_workflow(state)
    assert "missing_replay_prevention" in result["approval_workflow_blockers"]


def test_missing_kill_switch_proof_blocks():
    state = _base_state()
    state["kill_switch_proof"] = None
    result = evaluate_broker_demo_connector_approval_workflow(state)
    assert "missing_kill_switch_proof" in result["approval_workflow_blockers"]


def test_missing_rollback_proof_blocks():
    state = _base_state()
    state["rollback_proof"] = None
    result = evaluate_broker_demo_connector_approval_workflow(state)
    assert "missing_rollback_proof" in result["approval_workflow_blockers"]


def test_missing_reconciliation_proof_blocks():
    state = _base_state()
    state["reconciliation_proof"] = None
    result = evaluate_broker_demo_connector_approval_workflow(state)
    assert "missing_reconciliation_proof" in result["approval_workflow_blockers"]


def test_missing_final_disarm_proof_blocks():
    state = _base_state()
    state["final_disarm_proof"] = None
    result = evaluate_broker_demo_connector_approval_workflow(state)
    assert "missing_final_disarm_proof" in result["approval_workflow_blockers"]


def test_missing_one_shot_controls_blocks():
    state = _base_state()
    state["one_shot_controls"] = None
    result = evaluate_broker_demo_connector_approval_workflow(state)
    assert "missing_one_shot_controls" in result["approval_workflow_blockers"]


def test_approval_expired_returns_expired():
    state = _base_state()
    state["approval_expired"] = True
    result = evaluate_broker_demo_connector_approval_workflow(state)
    assert result["approval_workflow_status"] == APPROVAL_WORKFLOW_EXPIRED


def test_approval_revoked_returns_revoked():
    state = _base_state()
    state["approval_revoked"] = True
    result = evaluate_broker_demo_connector_approval_workflow(state)
    assert result["approval_workflow_status"] == APPROVAL_WORKFLOW_REVOKED


def test_broker_connection_detected_blocks():
    state = _base_state()
    state["broker_connection_detected"] = True
    result = evaluate_broker_demo_connector_approval_workflow(state)
    assert result["approval_workflow_status"] == APPROVAL_WORKFLOW_BLOCKED
    assert "broker_connection_detected" in result["approval_workflow_blockers"]


def test_network_access_detected_blocks():
    state = _base_state()
    state["network_access_detected"] = True
    result = evaluate_broker_demo_connector_approval_workflow(state)
    assert result["approval_workflow_status"] == APPROVAL_WORKFLOW_BLOCKED
    assert "network_access_detected" in result["approval_workflow_blockers"]


def test_credential_access_detected_blocks():
    state = _base_state()
    state["credential_access_detected"] = True
    result = evaluate_broker_demo_connector_approval_workflow(state)
    assert result["approval_workflow_status"] == APPROVAL_WORKFLOW_BLOCKED
    assert "credential_access_detected" in result["approval_workflow_blockers"]


def test_account_identifier_access_detected_blocks():
    state = _base_state()
    state["account_identifier_access_detected"] = True
    result = evaluate_broker_demo_connector_approval_workflow(state)
    assert result["approval_workflow_status"] == APPROVAL_WORKFLOW_BLOCKED
    assert "account_identifier_access_detected" in result["approval_workflow_blockers"]


def test_order_execution_detected_blocks():
    state = _base_state()
    state["order_execution_detected"] = True
    result = evaluate_broker_demo_connector_approval_workflow(state)
    assert result["approval_workflow_status"] == APPROVAL_WORKFLOW_BLOCKED
    assert "order_execution_detected" in result["approval_workflow_blockers"]


def test_live_trading_authorization_detected_blocks():
    state = _base_state()
    state["live_trading_authorization_detected"] = True
    result = evaluate_broker_demo_connector_approval_workflow(state)
    assert result["approval_workflow_status"] == APPROVAL_WORKFLOW_BLOCKED
    assert "live_trading_authorization_detected" in result["approval_workflow_blockers"]


def test_execution_authority_detected_blocks():
    state = _base_state()
    state["execution_authority_detected"] = True
    result = evaluate_broker_demo_connector_approval_workflow(state)
    assert result["approval_workflow_status"] == APPROVAL_WORKFLOW_BLOCKED
    assert "execution_authority_detected" in result["approval_workflow_blockers"]


def test_capital_allocation_detected_blocks():
    state = _base_state()
    state["capital_allocation_detected"] = True
    result = evaluate_broker_demo_connector_approval_workflow(state)
    assert result["approval_workflow_status"] == APPROVAL_WORKFLOW_BLOCKED
    assert "capital_allocation_detected" in result["approval_workflow_blockers"]


def test_alias_aware_inputs_work():
    state = _base_state()
    state["approvalRequestPresent"] = True
    state["approvalTrace"] = {"id": "alias"}
    state["approvalScope"] = "alias-scope"
    state["approvalReviewer"] = "alias-reviewer"
    state.pop("approval_request_present")
    state.pop("approval_trace")
    state.pop("approval_scope")
    state.pop("approval_reviewer")

    result = evaluate_broker_demo_connector_approval_workflow(state)
    assert result["approval_workflow_status"] == APPROVAL_WORKFLOW_REVIEW_READY
    assert result["approval_workflow_summary"]["approval_scope"] == "alias-scope"
    assert result["approval_workflow_summary"]["approval_reviewer"] == "alias-reviewer"


def test_contract_hard_false_permissions_enforced():
    contract = evaluate_broker_demo_connector_approval_workflow(_base_state())["approval_workflow_contract"]
    assert contract["contract_version"] == "BROKER_DEMO_CONNECTOR_APPROVAL_WORKFLOW_V1"
    assert contract["broker_connection_allowed"] is False
    assert contract["network_access_allowed"] is False
    assert contract["credential_access_allowed"] is False
    assert contract["account_identifier_access_allowed"] is False
    assert contract["order_execution_allowed"] is False
    assert contract["live_trading_authorized"] is False
    assert contract["execution_authority_granted"] is False


def test_safety_never_authorizes_broker_network_order_live_execution():
    safety = evaluate_broker_demo_connector_approval_workflow(_base_state())["safety"]
    assert safety["broker_connection_active"] is False
    assert safety["network_access"] is False
    assert safety["order_execution_enabled"] is False
    assert safety["live_trading_authorized"] is False
    assert safety["execution_authority_granted"] is False


def test_next_safe_action_deterministic():
    out = evaluate_broker_demo_connector_approval_workflow(_base_state())
    assert out["approval_workflow_next_safe_action"] == "route_to_broker_demo_connector_implementation"


def test_required_next_packets_deterministic():
    state = _base_state()
    state["approval_window_active"] = False
    out1 = evaluate_broker_demo_connector_approval_workflow(state)
    out2 = evaluate_broker_demo_connector_approval_workflow(state)
    assert out1["approval_workflow_required_next_packets"] == out2["approval_workflow_required_next_packets"]


def test_blockers_deterministic_and_deduplicated():
    state = _base_state()
    state["approval_trace"] = None
    out1 = evaluate_broker_demo_connector_approval_workflow(state)
    out2 = evaluate_broker_demo_connector_approval_workflow(state)
    assert out1["approval_workflow_blockers"] == out2["approval_workflow_blockers"]
    assert len(out1["approval_workflow_blockers"]) == len(set(out1["approval_workflow_blockers"]))


def test_approval_workflow_only_true():
    out = evaluate_broker_demo_connector_approval_workflow(_base_state())
    assert out["safety"]["approval_workflow_only"] is True
