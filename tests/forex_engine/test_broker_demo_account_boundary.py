from __future__ import annotations

from automation.forex_engine.broker_demo_account_boundary import (
    ACCOUNT_BOUNDARY_BLOCKED,
    ACCOUNT_BOUNDARY_EXPIRED,
    ACCOUNT_BOUNDARY_INCOMPLETE,
    ACCOUNT_BOUNDARY_REVIEW_READY,
    ACCOUNT_BOUNDARY_REVOKED,
    ACCOUNT_BOUNDARY_REJECTED,
    CREDENTIAL_BOUNDARY_REVIEW_READY,
    DRY_RUN_ORCHESTRATION_READY,
    IMPLEMENTATION_PLAN_REVIEW_READY,
    PROTECTED_CONNECTOR_GATE_REVIEW_READY,
    PROTECTED_RUNTIME_PLAN_REVIEW_READY,
    APPROVAL_WORKFLOW_REVIEW_READY,
    evaluate_broker_demo_account_boundary,
)


def base_state():
    return {
        "credential_boundary_status": CREDENTIAL_BOUNDARY_REVIEW_READY,
        "implementation_plan_status": IMPLEMENTATION_PLAN_REVIEW_READY,
        "dry_run_orchestration_status": DRY_RUN_ORCHESTRATION_READY,
        "runtime_plan_status": PROTECTED_RUNTIME_PLAN_REVIEW_READY,
        "approval_workflow_status": APPROVAL_WORKFLOW_REVIEW_READY,
        "protected_connector_gate_status": PROTECTED_CONNECTOR_GATE_REVIEW_READY,
        "account_boundary_request_present": True,
        "account_boundary_trace": True,
        "account_boundary_scope": True,
        "account_boundary_owner": True,
        "account_boundary_expiration": True,
        "account_boundary_freshness": True,
        "account_boundary_audit_record": True,
        "account_boundary_handoff_boundary": True,
        "account_redaction_required": True,
        "account_external_only": True,
        "account_operator_injected_only": True,
        "account_not_committed": True,
        "account_not_logged": True,
        "account_not_reported": True,
        "account_not_in_tests": True,
        "account_not_in_fixtures": True,
        "account_not_persisted": True,
        "account_secret_scan_required": True,
        "account_redacted_proof_required": True,
        "account_access_proof_redacted_only": True,
        "approval_trace": True,
        "approval_evidence_bundle": True,
        "approval_window_active": True,
        "runtime_plan_trace": True,
        "runtime_plan_evidence_bundle": True,
        "dry_run_orchestration_trace": True,
        "credential_boundary_trace": True,
        "replay_prevention": True,
        "kill_switch_proof": True,
        "rollback_proof": True,
        "reconciliation_proof": True,
        "final_disarm_proof": True,
        "operator_review_required": True,
        "manual_arming_required": True,
        "timeout_required": True,
        "no_retry_loop": True,
        "no_autonomous_reentry": True,
    }


def test_complete_state_review_ready():
    result = evaluate_broker_demo_account_boundary(base_state())
    assert result["account_boundary_status"] == ACCOUNT_BOUNDARY_REVIEW_READY
    assert result["account_boundary_ready"] is True
    assert result["account_boundary_blocked"] is False
    assert result["account_boundary_blockers"] == []


def test_empty_state_expires_deterministically():
    result = evaluate_broker_demo_account_boundary({})
    assert result["account_boundary_status"] == ACCOUNT_BOUNDARY_EXPIRED
    assert "approval_window_inactive" in result["account_boundary_blockers"]


def test_rejected_upstream_returns_rejected():
    state = base_state()
    state["implementation_plan_status"] = "REJECTED"
    assert evaluate_broker_demo_account_boundary(state)["account_boundary_status"] == ACCOUNT_BOUNDARY_REJECTED


def test_revoked_returns_revoked():
    state = base_state()
    state["account_boundary_revoked"] = True
    result = evaluate_broker_demo_account_boundary(state)
    assert result["account_boundary_status"] == ACCOUNT_BOUNDARY_REVOKED
    assert result["account_boundary_blockers"] == ["account_boundary_revoked"]


def test_account_identifier_access_blocks():
    state = base_state()
    state["account_identifier_access_detected"] = True
    result = evaluate_broker_demo_account_boundary(state)
    assert result["account_boundary_status"] == ACCOUNT_BOUNDARY_BLOCKED
    assert "account_identifier_access_detected" in result["account_boundary_blockers"]


def test_redaction_contract_denies_sensitive_fields():
    c = evaluate_broker_demo_account_boundary(base_state())["redaction_contract"]
    assert c["account_identifier_values_allowed"] is False
    assert c["account_identifier_hashes_allowed"] is False
    assert c["account_identifier_lengths_allowed"] is False
    assert c["account_identifier_prefixes_allowed"] is False
    assert c["account_identifier_suffixes_allowed"] is False


def test_redaction_contract_allows_sanitized_only():
    c = evaluate_broker_demo_account_boundary(base_state())["redaction_contract"]
    assert c["account_identifier_redacted_proof_allowed"] is True
    assert c["account_identifier_metadata_allowed"] is True
    assert c["account_identifier_presence_boolean_allowed"] is True


def test_safety_never_authorizes_account_access():
    s = evaluate_broker_demo_account_boundary(base_state())["safety"]
    assert s["account_identifiers_accessed"] is False
    assert s["account_identifier_values_visible"] is False


def test_safety_never_authorizes_broker_connection():
    assert evaluate_broker_demo_account_boundary(base_state())["safety"]["broker_connection_active"] is False


def test_safety_never_authorizes_network_access():
    assert evaluate_broker_demo_account_boundary(base_state())["safety"]["network_access"] is False


def test_safety_never_authorizes_order_execution():
    assert evaluate_broker_demo_account_boundary(base_state())["safety"]["order_execution_enabled"] is False


def test_safety_never_authorizes_live_trading():
    assert evaluate_broker_demo_account_boundary(base_state())["safety"]["live_trading_authorized"] is False


def test_safety_never_grants_execution_authority():
    assert evaluate_broker_demo_account_boundary(base_state())["safety"]["execution_authority_granted"] is False


def test_next_safe_action_deterministic():
    state = base_state()
    state["account_not_persisted"] = False
    first = evaluate_broker_demo_account_boundary(state)["account_boundary_next_safe_action"]
    second = evaluate_broker_demo_account_boundary(state)["account_boundary_next_safe_action"]
    assert first == second


def test_required_next_packets_deterministic():
    first = evaluate_broker_demo_account_boundary(base_state())["account_boundary_required_next_packets"]
    second = evaluate_broker_demo_account_boundary(base_state())["account_boundary_required_next_packets"]
    assert first == second == ["AIOS_FOREX_BROKER_DEMO_NO_ORDER_CONNECTOR_DESIGN_V1"]


def test_blockers_deduplicated():
    state = base_state()
    state["runtime_plan_status"] = "REJECTED"
    state["runtime_plan_status"] = "MISSING"
    blockers = evaluate_broker_demo_account_boundary(state)["account_boundary_blockers"]
    assert blockers.count("rejected_runtime_plan") == 0
    assert len(blockers) == len(set(blockers))


def test_account_boundary_only_true():
    assert evaluate_broker_demo_account_boundary(base_state())["safety"]["account_boundary_only"] is True


def test_contract_forbids_permissions():
    c = evaluate_broker_demo_account_boundary(base_state())["account_boundary_contract"]
    assert c["account_identifier_access_allowed"] is False
    assert c["account_identifier_storage_allowed"] is False
    assert c["network_access_allowed"] is False
    assert c["broker_connection_allowed"] is False
    assert c["order_execution_allowed"] is False
    assert c["live_trading_authorized"] is False
    assert c["execution_authority_granted"] is False


def test_missing_account_boundary_request_blocks():
    state = base_state()
    state["account_boundary_request_present"] = False
    result = evaluate_broker_demo_account_boundary(state)
    assert result["account_boundary_status"] in {ACCOUNT_BOUNDARY_INCOMPLETE, ACCOUNT_BOUNDARY_BLOCKED}
    assert "missing_account_boundary_request" in result["account_boundary_blockers"]
