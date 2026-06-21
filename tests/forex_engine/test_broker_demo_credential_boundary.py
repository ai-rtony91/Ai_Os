from automation.forex_engine.broker_demo_credential_boundary import (
    CREDENTIAL_BOUNDARY_BLOCKED,
    CREDENTIAL_BOUNDARY_EXPIRED,
    CREDENTIAL_BOUNDARY_REJECTED,
    CREDENTIAL_BOUNDARY_REVIEW_READY,
    CREDENTIAL_BOUNDARY_REVOKED,
    evaluate_broker_demo_credential_boundary,
)


def ready_state():
    return {
        "implementation_plan_status": "IMPLEMENTATION_PLAN_REVIEW_READY",
        "dry_run_orchestration_status": "DRY_RUN_ORCHESTRATION_READY",
        "runtime_plan_status": "PROTECTED_RUNTIME_PLAN_REVIEW_READY",
        "approval_workflow_status": "APPROVAL_WORKFLOW_REVIEW_READY",
        "protected_connector_gate_status": "PROTECTED_CONNECTOR_GATE_REVIEW_READY",
        "credential_boundary_request_present": True,
        "credential_boundary_trace": True,
        "credential_boundary_scope": True,
        "credential_boundary_owner": True,
        "credential_boundary_expiration": True,
        "credential_boundary_freshness": True,
        "credential_boundary_audit_record": True,
        "credential_boundary_handoff_boundary": True,
        "credential_redaction_required": True,
        "credential_external_only": True,
        "credential_operator_injected_only": True,
        "credential_secret_scan_required": True,
        "credential_redacted_proof_required": True,
        "credential_access_proof_redacted_only": True,
        "approval_trace": True,
        "approval_evidence_bundle": True,
        "approval_window_active": True,
        "runtime_plan_trace": True,
        "runtime_plan_evidence_bundle": True,
        "dry_run_orchestration_trace": True,
        "replay_prevention": True,
        "kill_switch_proof": True,
        "rollback_proof": True,
        "reconciliation_proof": True,
        "final_disarm_proof": True,
        "operator_review_required": True,
        "manual_arming_required": True,
        "timeout_required": True,
    }


def test_complete_state_ready():
    result = evaluate_broker_demo_credential_boundary(ready_state())
    assert result["credential_boundary_status"] == CREDENTIAL_BOUNDARY_REVIEW_READY


def test_empty_state_expires():
    result = evaluate_broker_demo_credential_boundary({})
    assert result["credential_boundary_status"] == CREDENTIAL_BOUNDARY_EXPIRED


def test_rejected_upstream():
    state = ready_state()
    state["implementation_plan_status"] = "IMPLEMENTATION_PLAN_REJECTED"
    result = evaluate_broker_demo_credential_boundary(state)
    assert result["credential_boundary_status"] == CREDENTIAL_BOUNDARY_REJECTED


def test_revoked():
    state = ready_state()
    state["credential_boundary_revoked"] = True
    result = evaluate_broker_demo_credential_boundary(state)
    assert result["credential_boundary_status"] == CREDENTIAL_BOUNDARY_REVOKED


def test_credential_access_blocks():
    state = ready_state()
    state["credentials_accessed"] = True
    result = evaluate_broker_demo_credential_boundary(state)
    assert result["credential_boundary_status"] == CREDENTIAL_BOUNDARY_BLOCKED


def test_redaction_contract():
    result = evaluate_broker_demo_credential_boundary(ready_state())
    redaction = result["redaction_contract"]
    assert redaction["credential_values_allowed"] is False
    assert redaction["credential_hashes_allowed"] is False
    assert redaction["credential_redacted_proof_allowed"] is True


def test_safety_false():
    result = evaluate_broker_demo_credential_boundary(ready_state())
    safety = result["safety"]
    assert safety["credentials_accessed"] is False
    assert safety["broker_connection_active"] is False
    assert safety["network_access"] is False
    assert safety["order_execution_enabled"] is False
    assert safety["live_trading_authorized"] is False
    assert safety["execution_authority_granted"] is False