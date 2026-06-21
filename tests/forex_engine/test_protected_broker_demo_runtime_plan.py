from __future__ import annotations

from automation.forex_engine.protected_broker_demo_runtime_plan import (
    APPROVAL_WORKFLOW_REVIEW_READY,
    CONNECTOR_CONTRACT_REVIEW_READY,
    LIVE_REVIEW_CERTIFICATE_REVIEW_READY,
    ONE_SHOT_EXCEPTION_REVIEW_READY,
    PROTECTED_CONNECTOR_GATE_REVIEW_READY,
    PROTECTED_RUNTIME_PLAN_BLOCKED,
    PROTECTED_RUNTIME_PLAN_EXPIRED,
    PROTECTED_RUNTIME_PLAN_INCOMPLETE,
    PROTECTED_RUNTIME_PLAN_REJECTED,
    PROTECTED_RUNTIME_PLAN_REVIEW_READY,
    PROTECTED_RUNTIME_PLAN_REVOKED,
    BROKER_DEMO_RUNTIME_REVIEW_READY,
    RUNTIME_CONNECTOR_REVIEW_READY,
    REVIEW_CHAIN_REVIEW_READY,
    APPROVAL_WORKFLOW_REJECTED,
    evaluate_protected_broker_demo_runtime_plan,
    PROTECTED_CONNECTOR_GATE_REJECTED,
)

from automation.forex_engine.protected_broker_demo_runtime_plan import (
    BROKER_DEMO_RUNTIME_REVIEW_REJECTED,
    RUNTIME_CONNECTOR_REJECTED,
    CONNECTOR_CONTRACT_REJECTED,
    REVIEW_CHAIN_REJECTED,
    LIVE_REVIEW_CERTIFICATE_REJECTED,
    ONE_SHOT_EXCEPTION_REJECTED,
)


def _ready_state():
    return {
        "approval_workflow_status": APPROVAL_WORKFLOW_REVIEW_READY,
        "protected_connector_gate_status": PROTECTED_CONNECTOR_GATE_REVIEW_READY,
        "broker_demo_runtime_review_status": BROKER_DEMO_RUNTIME_REVIEW_READY,
        "runtime_connector_status": RUNTIME_CONNECTOR_REVIEW_READY,
        "connector_contract_status": CONNECTOR_CONTRACT_REVIEW_READY,
        "review_chain_status": REVIEW_CHAIN_REVIEW_READY,
        "certificate_status": LIVE_REVIEW_CERTIFICATE_REVIEW_READY,
        "one_shot_status": ONE_SHOT_EXCEPTION_REVIEW_READY,
        "runtime_plan_request_present": True,
        "runtime_plan_trace": "trace-id",
        "runtime_plan_evidence_bundle": ["proof"],
        "runtime_plan_scope": "demo",
        "runtime_plan_owner": "ops",
        "runtime_plan_expiration": "2026-06-22",
        "runtime_plan_freshness": True,
        "runtime_plan_revocation_path": "revocations/active",
        "runtime_plan_audit_record": "audit.log",
        "runtime_plan_connector_scope": "forex-demo",
        "runtime_plan_handoff_boundary": "handoff-v1",
        "approval_trace": {"present": True},
        "approval_evidence_bundle": {"present": True},
        "approval_window_active": True,
        "replay_prevention": {"present": True},
        "replay_proof": {"present": True},
        "reconciliation_proof": {"present": True},
        "kill_switch_proof": {"present": True},
        "rollback_proof": {"present": True},
        "freshness_proof": {"present": True},
        "final_disarm_proof": {"present": True},
        "one_shot_controls": {
            "operator_review_required": True,
            "manual_arming_required": True,
            "no_retry_loop": True,
            "no_autonomous_reentry": True,
        },
        "post_trade_journal_path": "/tmp/journal",
        "operator_review_required": True,
        "manual_arming_required": True,
        "timeout_required": True,
        "no_retry_loop": True,
        "no_autonomous_reentry": True,
    }


def _assert_blocked(result, expected):
    assert result["runtime_plan_status"] == PROTECTED_RUNTIME_PLAN_BLOCKED
    assert result["runtime_plan_blocked"] is True
    assert expected in result["runtime_plan_blockers"]


def _assert_incomplete(result, expected_blocker):
    assert result["runtime_plan_status"] == PROTECTED_RUNTIME_PLAN_INCOMPLETE
    assert result["runtime_plan_blocked"] is False
    assert expected_blocker in result["runtime_plan_blockers"]


def _assert_rejected(result, expected_blocker):
    assert result["runtime_plan_status"] == PROTECTED_RUNTIME_PLAN_REJECTED
    assert expected_blocker in result["runtime_plan_blockers"]


def _assert_ready(result):
    assert result["runtime_plan_status"] == PROTECTED_RUNTIME_PLAN_REVIEW_READY
    assert result["runtime_plan_review_ready"] is True
    assert result["runtime_plan_blocked"] is False
    assert result["runtime_plan_blockers"] == []


def test_empty_state_blocks():
    result = evaluate_protected_broker_demo_runtime_plan({})
    assert result["runtime_plan_status"] == PROTECTED_RUNTIME_PLAN_INCOMPLETE
    assert result["runtime_plan_review_ready"] is False
    assert "missing_approval_workflow" in result["runtime_plan_blockers"]


def test_complete_proof_state_returns_review_ready():
    result = evaluate_protected_broker_demo_runtime_plan(_ready_state())
    _assert_ready(result)
    assert result["runtime_plan_contract"]["contract_version"] == "PROTECTED_BROKER_DEMO_RUNTIME_PLAN_V1"
    assert result["runtime_plan_contract"]["broker_connection_allowed"] is False
    assert result["runtime_plan_contract"]["network_access_allowed"] is False
    assert result["runtime_plan_contract"]["order_execution_allowed"] is False
    assert result["runtime_plan_contract"]["live_trading_authorized"] is False
    assert result["runtime_plan_contract"]["execution_authority_granted"] is False


def test_missing_approval_workflow_blocks():
    state = _ready_state()
    state.pop("approval_workflow_status")
    result = evaluate_protected_broker_demo_runtime_plan(state)
    _assert_incomplete(result, "missing_approval_workflow")


def test_approval_workflow_incomplete_blocks():
    state = _ready_state()
    state["approval_workflow_status"] = "APPROVAL_WORKFLOW_INCOMPLETE"
    result = evaluate_protected_broker_demo_runtime_plan(state)
    _assert_incomplete(result, "approval_workflow_not_ready")


def test_approval_workflow_rejected_returns_rejected():
    state = _ready_state()
    state["approval_workflow_status"] = "APPROVAL_WORKFLOW_REJECTED"
    result = evaluate_protected_broker_demo_runtime_plan(state)
    _assert_rejected(result, "rejected_approval_workflow")


def test_missing_protected_connector_gate_blocks():
    state = _ready_state()
    state.pop("protected_connector_gate_status")
    result = evaluate_protected_broker_demo_runtime_plan(state)
    _assert_incomplete(result, "missing_protected_connector_gate")


def test_protected_connector_gate_incomplete_blocks():
    state = _ready_state()
    state["protected_connector_gate_status"] = "PROTECTED_CONNECTOR_GATE_INCOMPLETE"
    result = evaluate_protected_broker_demo_runtime_plan(state)
    _assert_incomplete(result, "protected_connector_gate_not_ready")


def test_protected_connector_gate_rejected_returns_rejected():
    state = _ready_state()
    state["protected_connector_gate_status"] = "PROTECTED_CONNECTOR_GATE_REJECTED"
    result = evaluate_protected_broker_demo_runtime_plan(state)
    _assert_rejected(result, "rejected_protected_connector_gate")


def test_missing_broker_demo_runtime_review_blocks():
    state = _ready_state()
    state.pop("broker_demo_runtime_review_status")
    result = evaluate_protected_broker_demo_runtime_plan(state)
    _assert_incomplete(result, "missing_broker_demo_runtime_review")


def test_broker_demo_runtime_review_incomplete_blocks():
    state = _ready_state()
    state["broker_demo_runtime_review_status"] = "BROKER_DEMO_RUNTIME_REVIEW_INCOMPLETE"
    result = evaluate_protected_broker_demo_runtime_plan(state)
    _assert_incomplete(result, "broker_demo_runtime_review_not_ready")


def test_broker_demo_runtime_review_rejected_returns_rejected():
    state = _ready_state()
    state["broker_demo_runtime_review_status"] = BROKER_DEMO_RUNTIME_REVIEW_REJECTED
    result = evaluate_protected_broker_demo_runtime_plan(state)
    _assert_rejected(result, "rejected_broker_demo_runtime_review")


def test_missing_runtime_connector_blocks():
    state = _ready_state()
    state.pop("runtime_connector_status")
    result = evaluate_protected_broker_demo_runtime_plan(state)
    _assert_incomplete(result, "missing_runtime_connector")


def test_runtime_connector_incomplete_blocks():
    state = _ready_state()
    state["runtime_connector_status"] = "RUNTIME_CONNECTOR_INCOMPLETE"
    result = evaluate_protected_broker_demo_runtime_plan(state)
    _assert_incomplete(result, "runtime_connector_not_ready")


def test_runtime_connector_rejected_returns_rejected():
    state = _ready_state()
    state["runtime_connector_status"] = RUNTIME_CONNECTOR_REJECTED
    result = evaluate_protected_broker_demo_runtime_plan(state)
    _assert_rejected(result, "rejected_runtime_connector")


def test_missing_connector_contract_blocks():
    state = _ready_state()
    state.pop("connector_contract_status")
    result = evaluate_protected_broker_demo_runtime_plan(state)
    _assert_incomplete(result, "missing_connector_contract")


def test_connector_contract_incomplete_blocks():
    state = _ready_state()
    state["connector_contract_status"] = "CONNECTOR_CONTRACT_INCOMPLETE"
    result = evaluate_protected_broker_demo_runtime_plan(state)
    _assert_incomplete(result, "connector_contract_not_ready")


def test_connector_contract_rejected_returns_rejected():
    state = _ready_state()
    state["connector_contract_status"] = CONNECTOR_CONTRACT_REJECTED
    result = evaluate_protected_broker_demo_runtime_plan(state)
    _assert_rejected(result, "rejected_connector_contract")


def test_missing_review_chain_blocks():
    state = _ready_state()
    state.pop("review_chain_status")
    result = evaluate_protected_broker_demo_runtime_plan(state)
    _assert_incomplete(result, "missing_review_chain")


def test_review_chain_incomplete_blocks():
    state = _ready_state()
    state["review_chain_status"] = "REVIEW_CHAIN_INCOMPLETE"
    result = evaluate_protected_broker_demo_runtime_plan(state)
    _assert_incomplete(result, "review_chain_not_ready")


def test_review_chain_rejected_returns_rejected():
    state = _ready_state()
    state["review_chain_status"] = REVIEW_CHAIN_REJECTED
    result = evaluate_protected_broker_demo_runtime_plan(state)
    _assert_rejected(result, "rejected_review_chain")


def test_missing_certificate_blocks():
    state = _ready_state()
    state.pop("certificate_status")
    result = evaluate_protected_broker_demo_runtime_plan(state)
    _assert_incomplete(result, "missing_certificate")


def test_certificate_incomplete_blocks():
    state = _ready_state()
    state["certificate_status"] = "LIVE_REVIEW_CERTIFICATE_INCOMPLETE"
    result = evaluate_protected_broker_demo_runtime_plan(state)
    _assert_incomplete(result, "certificate_not_ready")


def test_certificate_rejected_returns_rejected():
    state = _ready_state()
    state["certificate_status"] = LIVE_REVIEW_CERTIFICATE_REJECTED
    result = evaluate_protected_broker_demo_runtime_plan(state)
    _assert_rejected(result, "rejected_certificate")


def test_missing_one_shot_package_blocks():
    state = _ready_state()
    state.pop("one_shot_status")
    result = evaluate_protected_broker_demo_runtime_plan(state)
    _assert_incomplete(result, "missing_one_shot_package")


def test_one_shot_package_incomplete_blocks():
    state = _ready_state()
    state["one_shot_status"] = "ONE_SHOT_EXCEPTION_INCOMPLETE"
    result = evaluate_protected_broker_demo_runtime_plan(state)
    _assert_incomplete(result, "one_shot_package_not_ready")


def test_one_shot_package_rejected_returns_rejected():
    state = _ready_state()
    state["one_shot_status"] = ONE_SHOT_EXCEPTION_REJECTED
    result = evaluate_protected_broker_demo_runtime_plan(state)
    _assert_rejected(result, "rejected_one_shot_package")


def test_missing_runtime_plan_request_blocks():
    state = _ready_state()
    state["runtime_plan_request_present"] = False
    result = evaluate_protected_broker_demo_runtime_plan(state)
    _assert_incomplete(result, "missing_runtime_plan_request")


def test_missing_runtime_plan_trace_blocks():
    state = _ready_state()
    state.pop("runtime_plan_trace")
    result = evaluate_protected_broker_demo_runtime_plan(state)
    _assert_incomplete(result, "missing_runtime_plan_trace")


def test_missing_runtime_plan_evidence_bundle_blocks():
    state = _ready_state()
    state.pop("runtime_plan_evidence_bundle")
    result = evaluate_protected_broker_demo_runtime_plan(state)
    _assert_incomplete(result, "missing_runtime_plan_evidence_bundle")


def test_missing_runtime_plan_scope_blocks():
    state = _ready_state()
    state.pop("runtime_plan_scope")
    result = evaluate_protected_broker_demo_runtime_plan(state)
    _assert_incomplete(result, "missing_runtime_plan_scope")


def test_missing_runtime_plan_owner_blocks():
    state = _ready_state()
    state.pop("runtime_plan_owner")
    result = evaluate_protected_broker_demo_runtime_plan(state)
    _assert_incomplete(result, "missing_runtime_plan_owner")


def test_missing_runtime_plan_expiration_blocks():
    state = _ready_state()
    state.pop("runtime_plan_expiration")
    result = evaluate_protected_broker_demo_runtime_plan(state)
    _assert_incomplete(result, "missing_runtime_plan_expiration")


def test_missing_runtime_plan_freshness_blocks():
    state = _ready_state()
    state.pop("runtime_plan_freshness")
    result = evaluate_protected_broker_demo_runtime_plan(state)
    _assert_incomplete(result, "missing_runtime_plan_freshness")


def test_missing_runtime_plan_revocation_path_blocks():
    state = _ready_state()
    state.pop("runtime_plan_revocation_path")
    result = evaluate_protected_broker_demo_runtime_plan(state)
    _assert_incomplete(result, "missing_runtime_plan_revocation_path")


def test_missing_runtime_plan_audit_record_blocks():
    state = _ready_state()
    state.pop("runtime_plan_audit_record")
    result = evaluate_protected_broker_demo_runtime_plan(state)
    _assert_incomplete(result, "missing_runtime_plan_audit_record")


def test_missing_runtime_plan_connector_scope_blocks():
    state = _ready_state()
    state.pop("runtime_plan_connector_scope")
    result = evaluate_protected_broker_demo_runtime_plan(state)
    _assert_incomplete(result, "missing_runtime_plan_connector_scope")


def test_missing_runtime_plan_handoff_boundary_blocks():
    state = _ready_state()
    state.pop("runtime_plan_handoff_boundary")
    result = evaluate_protected_broker_demo_runtime_plan(state)
    _assert_incomplete(result, "missing_runtime_plan_handoff_boundary")


def test_missing_approval_trace_blocks():
    state = _ready_state()
    state.pop("approval_trace")
    result = evaluate_protected_broker_demo_runtime_plan(state)
    _assert_incomplete(result, "missing_approval_trace")


def test_missing_approval_evidence_bundle_blocks():
    state = _ready_state()
    state.pop("approval_evidence_bundle")
    result = evaluate_protected_broker_demo_runtime_plan(state)
    _assert_incomplete(result, "missing_approval_evidence_bundle")


def test_inactive_approval_window_expires():
    state = _ready_state()
    state["approval_window_active"] = False
    result = evaluate_protected_broker_demo_runtime_plan(state)
    assert result["runtime_plan_status"] == PROTECTED_RUNTIME_PLAN_EXPIRED


def test_missing_replay_prevention_blocks():
    state = _ready_state()
    state.pop("replay_prevention")
    result = evaluate_protected_broker_demo_runtime_plan(state)
    _assert_incomplete(result, "missing_replay_prevention")


def test_missing_replay_proof_blocks():
    state = _ready_state()
    state.pop("replay_proof")
    result = evaluate_protected_broker_demo_runtime_plan(state)
    _assert_incomplete(result, "missing_replay_proof")


def test_missing_reconciliation_proof_blocks():
    state = _ready_state()
    state.pop("reconciliation_proof")
    result = evaluate_protected_broker_demo_runtime_plan(state)
    _assert_incomplete(result, "missing_reconciliation_proof")


def test_missing_kill_switch_proof_blocks():
    state = _ready_state()
    state.pop("kill_switch_proof")
    result = evaluate_protected_broker_demo_runtime_plan(state)
    _assert_incomplete(result, "missing_kill_switch_proof")


def test_missing_rollback_proof_blocks():
    state = _ready_state()
    state.pop("rollback_proof")
    result = evaluate_protected_broker_demo_runtime_plan(state)
    _assert_incomplete(result, "missing_rollback_proof")


def test_missing_freshness_proof_blocks():
    state = _ready_state()
    state.pop("freshness_proof")
    result = evaluate_protected_broker_demo_runtime_plan(state)
    _assert_incomplete(result, "missing_freshness_proof")


def test_missing_final_disarm_proof_blocks():
    state = _ready_state()
    state.pop("final_disarm_proof")
    result = evaluate_protected_broker_demo_runtime_plan(state)
    _assert_incomplete(result, "missing_final_disarm_proof")


def test_missing_one_shot_controls_blocks():
    state = _ready_state()
    state.pop("one_shot_controls")
    result = evaluate_protected_broker_demo_runtime_plan(state)
    _assert_incomplete(result, "missing_one_shot_controls")


def test_missing_post_trade_journal_path_blocks():
    state = _ready_state()
    state.pop("post_trade_journal_path")
    result = evaluate_protected_broker_demo_runtime_plan(state)
    _assert_incomplete(result, "missing_post_trade_journal_path")


def test_missing_operator_review_blocks():
    state = _ready_state()
    state["operator_review_required"] = False
    result = evaluate_protected_broker_demo_runtime_plan(state)
    _assert_incomplete(result, "missing_operator_review_requirement")


def test_missing_manual_arming_blocks():
    state = _ready_state()
    state["manual_arming_required"] = False
    result = evaluate_protected_broker_demo_runtime_plan(state)
    _assert_incomplete(result, "missing_manual_arming_requirement")


def test_missing_timeout_requirement_blocks():
    state = _ready_state()
    state["timeout_required"] = False
    result = evaluate_protected_broker_demo_runtime_plan(state)
    _assert_incomplete(result, "missing_timeout_requirement")


def test_retry_loop_detected_blocks():
    state = _ready_state()
    state["no_retry_loop"] = False
    result = evaluate_protected_broker_demo_runtime_plan(state)
    _assert_blocked(result, "retry_loop_detected")


def test_autonomous_reentry_detected_blocks():
    state = _ready_state()
    state["no_autonomous_reentry"] = False
    result = evaluate_protected_broker_demo_runtime_plan(state)
    _assert_blocked(result, "autonomous_reentry_detected")


def test_broker_connection_detected_blocks():
    state = _ready_state()
    state["broker_connection_detected"] = True
    result = evaluate_protected_broker_demo_runtime_plan(state)
    _assert_blocked(result, "broker_connection_detected")


def test_network_access_detected_blocks():
    state = _ready_state()
    state["network_access_detected"] = True
    result = evaluate_protected_broker_demo_runtime_plan(state)
    _assert_blocked(result, "network_access_detected")


def test_credential_access_detected_blocks():
    state = _ready_state()
    state["credential_access_detected"] = True
    result = evaluate_protected_broker_demo_runtime_plan(state)
    _assert_blocked(result, "credential_access_detected")


def test_account_identifier_detected_blocks():
    state = _ready_state()
    state["account_identifier_access_detected"] = True
    result = evaluate_protected_broker_demo_runtime_plan(state)
    _assert_blocked(result, "account_identifier_access_detected")


def test_order_execution_detected_blocks():
    state = _ready_state()
    state["order_execution_detected"] = True
    result = evaluate_protected_broker_demo_runtime_plan(state)
    _assert_blocked(result, "order_execution_detected")


def test_live_trading_authorization_detected_blocks():
    state = _ready_state()
    state["live_trading_authorization_detected"] = True
    result = evaluate_protected_broker_demo_runtime_plan(state)
    _assert_blocked(result, "live_trading_authorization_detected")


def test_execution_authority_detected_blocks():
    state = _ready_state()
    state["execution_authority_detected"] = True
    result = evaluate_protected_broker_demo_runtime_plan(state)
    _assert_blocked(result, "execution_authority_detected")


def test_capital_allocation_detected_blocks():
    state = _ready_state()
    state["capital_allocation_detected"] = True
    result = evaluate_protected_broker_demo_runtime_plan(state)
    _assert_blocked(result, "capital_allocation_detected")


def test_runtime_plan_revoked_returns_revoked():
    state = _ready_state()
    state["runtime_plan_revoked"] = True
    result = evaluate_protected_broker_demo_runtime_plan(state)
    assert result["runtime_plan_status"] == PROTECTED_RUNTIME_PLAN_REVOKED


def test_runtime_plan_expired_returns_expired():
    state = _ready_state()
    state["runtime_plan_freshness"] = False
    result = evaluate_protected_broker_demo_runtime_plan(state)
    assert result["runtime_plan_status"] == PROTECTED_RUNTIME_PLAN_EXPIRED


def test_alias_aware_upstream_statuses_work():
    state = _ready_state()
    state["approval_status"] = APPROVAL_WORKFLOW_REVIEW_READY
    state["connector_gate_status"] = PROTECTED_CONNECTOR_GATE_REVIEW_READY
    state["broker_demo_review_status"] = BROKER_DEMO_RUNTIME_REVIEW_READY
    state["broker_demo_runtime_connector_status"] = RUNTIME_CONNECTOR_REVIEW_READY
    state["live_review_connector_contract_status"] = CONNECTOR_CONTRACT_REVIEW_READY
    state["chain_status"] = REVIEW_CHAIN_REVIEW_READY
    state["live_review_certificate_status"] = LIVE_REVIEW_CERTIFICATE_REVIEW_READY
    state["exception_package_status"] = ONE_SHOT_EXCEPTION_REVIEW_READY
    state.pop("approval_workflow_status")
    state.pop("protected_connector_gate_status")
    state.pop("broker_demo_runtime_review_status")
    state.pop("runtime_connector_status")
    state.pop("connector_contract_status")
    state.pop("review_chain_status")
    state.pop("certificate_status")
    state.pop("one_shot_status")
    result = evaluate_protected_broker_demo_runtime_plan(state)
    _assert_ready(result)


def test_alias_aware_runtime_plan_inputs_work():
    state = _ready_state()
    state["plan_request_present"] = True
    state["plan_trace"] = "x"
    state["plan_evidence_bundle"] = ["z"]
    state["plan_scope"] = "scope"
    state["plan_owner"] = "ops"
    state["plan_expiration"] = "2026-06-22"
    state["plan_freshness"] = True
    state["plan_revocation_path"] = "path"
    state["plan_audit_record"] = "audit"
    state["plan_connector_scope"] = "scope"
    state["plan_handoff_boundary"] = "boundary"
    for key in [
        "runtime_plan_request_present",
        "runtime_plan_trace",
        "runtime_plan_evidence_bundle",
        "runtime_plan_scope",
        "runtime_plan_owner",
        "runtime_plan_expiration",
        "runtime_plan_freshness",
        "runtime_plan_revocation_path",
        "runtime_plan_audit_record",
        "runtime_plan_connector_scope",
        "runtime_plan_handoff_boundary",
    ]:
        state.pop(key)
    result = evaluate_protected_broker_demo_runtime_plan(state)
    _assert_ready(result)


def test_alias_aware_proof_and_controls_inputs_work():
    state = _ready_state()
    state["approval"] = {"present": True}
    state["approval_evidence"] = {"present": True}
    state["approval_active"] = True
    state["anti_replay"] = {"present": True}
    state["replayability_proof"] = {"present": True}
    state["reconciliation"] = {"present": True}
    state["kill_switch"] = {"present": True}
    state["rollback"] = {"present": True}
    state["evidence_fresh"] = {"present": True}
    state["final_disarm"] = {"present": True}
    state["controls"] = {
        "operator_review_required": True,
        "manual_arming_required": True,
        "no_retry_loop": True,
        "no_autonomous_reentry": True,
    }
    state["journal_path"] = "/tmp/journal"
    for key in [
        "approval_trace",
        "approval_evidence_bundle",
        "approval_window_active",
        "replay_prevention",
        "replay_proof",
        "reconciliation_proof",
        "kill_switch_proof",
        "rollback_proof",
        "freshness_proof",
        "final_disarm_proof",
        "one_shot_controls",
        "post_trade_journal_path",
    ]:
        state.pop(key)
    result = evaluate_protected_broker_demo_runtime_plan(state)
    _assert_ready(result)


def test_runtime_plan_contract_hard_false_permissions_enforced():
    result = evaluate_protected_broker_demo_runtime_plan(_ready_state())
    contract = result["runtime_plan_contract"]
    assert contract["broker_connection_allowed"] is False
    assert contract["network_access_allowed"] is False
    assert contract["credential_access_allowed"] is False
    assert contract["account_identifier_access_allowed"] is False
    assert contract["order_execution_allowed"] is False
    assert contract["live_trading_authorized"] is False
    assert contract["execution_authority_granted"] is False


def test_safety_never_authorizes_broker_connection():
    result = evaluate_protected_broker_demo_runtime_plan(_ready_state())
    safety = result["safety"]
    assert safety["broker_connection_active"] is False


def test_safety_never_authorizes_network_access():
    assert evaluate_protected_broker_demo_runtime_plan(_ready_state())["safety"]["network_access"] is False


def test_safety_never_authorizes_order_execution():
    assert evaluate_protected_broker_demo_runtime_plan(_ready_state())["safety"]["order_execution_enabled"] is False


def test_safety_never_authorizes_live_trading():
    assert evaluate_protected_broker_demo_runtime_plan(_ready_state())["safety"]["live_trading_authorized"] is False


def test_safety_never_grants_execution_authority():
    assert evaluate_protected_broker_demo_runtime_plan(_ready_state())["safety"]["execution_authority_granted"] is False


def test_next_safe_action_deterministic():
    ready = evaluate_protected_broker_demo_runtime_plan(_ready_state())
    incomplete = evaluate_protected_broker_demo_runtime_plan({})
    assert ready["runtime_plan_next_safe_action"] == "prepare_future_connector_implementation_packet"
    assert incomplete["runtime_plan_next_safe_action"] == "collect_missing_protected_runtime_plan_blockers"


def test_required_next_packets_deterministic():
    ready = evaluate_protected_broker_demo_runtime_plan(_ready_state())
    rejected = evaluate_protected_broker_demo_runtime_plan(
        {**_ready_state(), "approval_workflow_status": "APPROVAL_WORKFLOW_REJECTED"}
    )
    revoked = evaluate_protected_broker_demo_runtime_plan({**_ready_state(), "runtime_plan_revoked": True})
    assert ready["runtime_plan_required_next_packets"] != []
    assert revoked["runtime_plan_required_next_packets"][0] == "revoke_runtime_plan"
    assert len(rejected["runtime_plan_required_next_packets"]) == 3


def test_blockers_deterministic_and_deduplicated():
    state = _ready_state()
    state["approval_workflow_status"] = "BROKEN"
    result = evaluate_protected_broker_demo_runtime_plan(state)
    assert result["runtime_plan_blockers"] == ["approval_workflow_not_ready"]
    result2 = evaluate_protected_broker_demo_runtime_plan(state)
    assert result2["runtime_plan_blockers"] == result["runtime_plan_blockers"]


def test_protected_runtime_plan_only_true():
    assert evaluate_protected_broker_demo_runtime_plan(_ready_state())["safety"]["protected_runtime_plan_only"] is True


def test_broker_demo_connector_not_active_true():
    assert evaluate_protected_broker_demo_runtime_plan(_ready_state())["safety"]["broker_demo_connector_not_active"] is True
