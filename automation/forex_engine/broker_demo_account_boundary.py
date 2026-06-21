"""Account boundary evaluator for broker-demo planning controls.

No broker I/O, credentials, account identifiers, network, or external deps.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

ACCOUNT_BOUNDARY_BLOCKED = "ACCOUNT_BOUNDARY_BLOCKED"
ACCOUNT_BOUNDARY_INCOMPLETE = "ACCOUNT_BOUNDARY_INCOMPLETE"
ACCOUNT_BOUNDARY_REVIEW_READY = "ACCOUNT_BOUNDARY_REVIEW_READY"
ACCOUNT_BOUNDARY_REJECTED = "ACCOUNT_BOUNDARY_REJECTED"
ACCOUNT_BOUNDARY_REVOKED = "ACCOUNT_BOUNDARY_REVOKED"
ACCOUNT_BOUNDARY_EXPIRED = "ACCOUNT_BOUNDARY_EXPIRED"

IMPLEMENTATION_PLAN_REVIEW_READY = "IMPLEMENTATION_PLAN_REVIEW_READY"
DRY_RUN_ORCHESTRATION_READY = "DRY_RUN_ORCHESTRATION_READY"
PROTECTED_RUNTIME_PLAN_REVIEW_READY = "PROTECTED_RUNTIME_PLAN_REVIEW_READY"
APPROVAL_WORKFLOW_REVIEW_READY = "APPROVAL_WORKFLOW_REVIEW_READY"
PROTECTED_CONNECTOR_GATE_REVIEW_READY = "PROTECTED_CONNECTOR_GATE_REVIEW_READY"

CREDENTIAL_BOUNDARY_REVIEW_READY = "CREDENTIAL_BOUNDARY_REVIEW_READY"


def _to_bool(v: Any) -> Optional[bool]:
    if v is None:
        return None
    if isinstance(v, bool):
        return v
    if isinstance(v, str):
        low = v.lower()
        if low in {"true", "1", "yes", "on"}:
            return True
        if low in {"false", "0", "no", "off"}:
            return False
    return bool(v)


def _coalesce(state: Dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in state:
            return state[key]
    return None


def _coalesce_bool(state: Dict[str, Any], *keys: str) -> Optional[bool]:
    return _to_bool(_coalesce(state, *keys))


def _dedup(items: List[str]) -> List[str]:
    seen = set()
    out = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        out.append(item)
    return out


def _next_safe_action(blockers: List[str]) -> str:
    if not blockers:
        return "Proceed to next packet: AIOS_FOREX_BROKER_DEMO_NO_ORDER_CONNECTOR_DESIGN_V1"
    mapping = {
        "missing_credential_boundary": "Set credential boundary status to CREDENTIAL_BOUNDARY_REVIEW_READY",
        "credential_boundary_not_ready": "Repair credential boundary to review ready",
        "missing_implementation_plan": "Set implementation_plan_status to IMPLEMENTATION_PLAN_REVIEW_READY",
        "implementation_plan_not_ready": "Advance implementation plan to review ready",
        "missing_dry_run_orchestration": "Set dry_run_orchestration_status to DRY_RUN_ORCHESTRATION_READY",
        "dry_run_orchestration_not_ready": "Advance dry-run orchestration to ready",
        "missing_runtime_plan": "Set runtime_plan_status to PROTECTED_RUNTIME_PLAN_REVIEW_READY",
        "runtime_plan_not_ready": "Advance runtime plan to review ready",
        "missing_approval_workflow": "Set approval_workflow_status to APPROVAL_WORKFLOW_REVIEW_READY",
        "approval_workflow_not_ready": "Advance approval workflow to review ready",
        "missing_protected_connector_gate": "Set protected_connector_gate_status to PROTECTED_CONNECTOR_GATE_REVIEW_READY",
        "protected_connector_gate_not_ready": "Advance connector gate to review ready",
    }
    return mapping.get(blockers[0], "Re-run after applying account boundary controls")


def evaluate_broker_demo_account_boundary(
    state: Optional[Dict[str, Any]] = None,
    optional_limits: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    state = state or {}
    optional_limits = optional_limits or {}

    contract = {
        "contract_version": "BROKER_DEMO_ACCOUNT_BOUNDARY_V1",
        "credential_boundary_required": True,
        "implementation_plan_required": True,
        "dry_run_orchestration_required": True,
        "runtime_plan_required": True,
        "approval_workflow_required": True,
        "protected_connector_gate_required": True,
        "account_boundary_request_required": True,
        "account_boundary_trace_required": True,
        "account_boundary_scope_required": True,
        "account_boundary_owner_required": True,
        "account_boundary_expiration_required": True,
        "account_boundary_freshness_required": True,
        "account_boundary_audit_required": True,
        "account_boundary_handoff_boundary_required": True,
        "account_redaction_required": True,
        "account_external_only_required": True,
        "account_operator_injected_only_required": True,
        "account_not_committed_required": True,
        "account_not_logged_required": True,
        "account_not_reported_required": True,
        "account_not_in_tests_required": True,
        "account_not_in_fixtures_required": True,
        "account_not_persisted_required": True,
        "account_secret_scan_required": True,
        "account_redacted_proof_required": True,
        "account_access_proof_redacted_only_required": True,
        "approval_trace_required": True,
        "approval_evidence_required": True,
        "approval_window_required": True,
        "runtime_plan_trace_required": True,
        "runtime_plan_evidence_required": True,
        "dry_run_orchestration_trace_required": True,
        "credential_boundary_trace_required": True,
        "replay_prevention_required": True,
        "kill_switch_required": True,
        "rollback_required": True,
        "reconciliation_required": True,
        "final_disarm_required": True,
        "operator_review_required": True,
        "manual_arming_required": True,
        "timeout_required": True,
        "no_retry_loop_required": True,
        "no_autonomous_reentry_required": True,
        "credential_access_allowed": False,
        "account_identifier_access_allowed": False,
        "account_identifier_storage_allowed": False,
        "account_identifier_logging_allowed": False,
        "account_identifier_reporting_allowed": False,
        "account_identifier_test_fixture_allowed": False,
        "account_identifier_persistence_allowed": False,
        "broker_connection_allowed": False,
        "network_access_allowed": False,
        "order_execution_allowed": False,
        "live_trading_authorized": False,
        "execution_authority_granted": False,
    }

    redaction_contract = {
        "redaction_version": "BROKER_DEMO_ACCOUNT_REDACTION_V1",
        "account_identifier_values_allowed": False,
        "account_identifier_hashes_allowed": False,
        "account_identifier_lengths_allowed": False,
        "account_identifier_prefixes_allowed": False,
        "account_identifier_suffixes_allowed": False,
        "account_identifier_redacted_proof_allowed": True,
        "account_identifier_metadata_allowed": True,
        "account_identifier_presence_boolean_allowed": True,
    }

    safety = {
        "credentials_accessed": False,
        "account_identifiers_accessed": False,
        "account_identifier_values_visible": False,
        "account_identifier_storage_allowed": False,
        "account_identifier_logging_allowed": False,
        "account_identifier_reporting_allowed": False,
        "account_identifier_test_fixture_allowed": False,
        "account_identifier_persistence_allowed": False,
        "broker_connection_active": False,
        "network_access": False,
        "order_execution_enabled": False,
        "live_trading_authorized": False,
        "execution_authority_granted": False,
        "capital_allocated": False,
        "account_boundary_only": True,
        "operator_review_required": True,
        "manual_arming_required": True,
        "timeout_required": True,
        "no_retry_loop": True,
        "no_autonomous_reentry": True,
        "final_disarm_required": True,
        "replay_prevention_required": True,
    }

    cb_status = state.get("credential_boundary_status")
    impl_status = state.get("implementation_plan_status")
    dry_status = state.get("dry_run_orchestration_status")
    run_status = state.get("runtime_plan_status")
    appr_status = state.get("approval_workflow_status")
    gate_status = state.get("protected_connector_gate_status")

    blockers: List[str] = []

    if state.get("account_boundary_revoked") is True:
        return {
            "account_boundary_completed": False,
            "account_boundary_status": ACCOUNT_BOUNDARY_REVOKED,
            "account_boundary_ready": False,
            "account_boundary_blocked": False,
            "account_boundary_review_required": False,
            "account_boundary_summary": {"status": ACCOUNT_BOUNDARY_REVOKED, "limits": optional_limits},
            "account_boundary_blockers": ["account_boundary_revoked"],
            "account_boundary_warnings": ["account boundary revoked"],
            "account_boundary_next_safe_action": "Re-run after explicit boundary re-authorization",
            "account_boundary_required_next_packets": ["AIOS_FOREX_BROKER_DEMO_NO_ORDER_CONNECTOR_DESIGN_V1"],
            "account_boundary_contract": contract,
            "redaction_contract": redaction_contract,
            "safety": safety,
        }

    if cb_status != CREDENTIAL_BOUNDARY_REVIEW_READY:
        if cb_status is None:
            blockers.append("missing_credential_boundary")
        elif cb_status == "CREDENTIAL_BOUNDARY_REJECTED":
            blockers.append("rejected_credential_boundary")
        else:
            blockers.append("credential_boundary_not_ready")

    if impl_status != IMPLEMENTATION_PLAN_REVIEW_READY:
        if impl_status is None:
            blockers.append("missing_implementation_plan")
        elif impl_status == "REJECTED":
            blockers.append("rejected_implementation_plan")
        else:
            blockers.append("implementation_plan_not_ready")

    if dry_status != DRY_RUN_ORCHESTRATION_READY:
        if dry_status is None:
            blockers.append("missing_dry_run_orchestration")
        elif dry_status == "REJECTED":
            blockers.append("rejected_dry_run_orchestration")
        else:
            blockers.append("dry_run_orchestration_not_ready")

    if run_status != PROTECTED_RUNTIME_PLAN_REVIEW_READY:
        if run_status is None:
            blockers.append("missing_runtime_plan")
        elif run_status == "REJECTED":
            blockers.append("rejected_runtime_plan")
        else:
            blockers.append("runtime_plan_not_ready")

    if appr_status != APPROVAL_WORKFLOW_REVIEW_READY:
        if appr_status is None:
            blockers.append("missing_approval_workflow")
        elif appr_status == "REJECTED":
            blockers.append("rejected_approval_workflow")
        else:
            blockers.append("approval_workflow_not_ready")

    if gate_status != PROTECTED_CONNECTOR_GATE_REVIEW_READY:
        if gate_status is None:
            blockers.append("missing_protected_connector_gate")
        elif gate_status == "REJECTED":
            blockers.append("rejected_protected_connector_gate")
        else:
            blockers.append("protected_connector_gate_not_ready")

    required_truthy = {
        "missing_account_boundary_request": ("account_boundary_request_present", True),
        "missing_account_boundary_trace": ("account_boundary_trace", True),
        "missing_account_boundary_scope": ("account_boundary_scope", True),
        "missing_account_boundary_owner": ("account_boundary_owner", True),
        "missing_account_boundary_expiration": ("account_boundary_expiration", True),
        "missing_account_boundary_freshness": ("account_boundary_freshness", True),
        "missing_account_boundary_audit_record": ("account_boundary_audit_record", True),
        "missing_account_boundary_handoff_boundary": ("account_boundary_handoff_boundary", True),
        "missing_account_redaction_requirement": ("account_redaction_required", True),
        "missing_account_external_only_requirement": ("account_external_only", True),
        "missing_account_operator_injected_only_requirement": ("account_operator_injected_only", True),
        "account_identifier_committed_detected": ("account_not_committed", True),
        "account_identifier_logged_detected": ("account_not_logged", True),
        "account_identifier_reported_detected": ("account_not_reported", True),
        "account_identifier_in_tests_detected": ("account_not_in_tests", True),
        "account_identifier_in_fixtures_detected": ("account_not_in_fixtures", True),
        "account_identifier_persisted_detected": ("account_not_persisted", True),
        "missing_account_secret_scan_requirement": ("account_secret_scan_required", True),
        "missing_account_redacted_proof_requirement": ("account_redacted_proof_required", True),
        "missing_account_access_proof_redacted_only_requirement": ("account_access_proof_redacted_only", True),
        "missing_approval_trace": ("approval_trace", True),
        "missing_approval_evidence_bundle": ("approval_evidence_bundle", True),
        "missing_runtime_plan_trace": ("runtime_plan_trace", True),
        "missing_runtime_plan_evidence_bundle": ("runtime_plan_evidence_bundle", True),
        "missing_dry_run_orchestration_trace": ("dry_run_orchestration_trace", True),
        "missing_credential_boundary_trace": ("credential_boundary_trace", True),
        "missing_replay_prevention": ("replay_prevention", True),
        "missing_kill_switch_proof": ("kill_switch_proof", True),
        "missing_rollback_proof": ("rollback_proof", True),
        "missing_reconciliation_proof": ("reconciliation_proof", True),
        "missing_final_disarm_proof": ("final_disarm_proof", True),
        "missing_operator_review_requirement": ("operator_review_required", True),
        "missing_manual_arming_requirement": ("manual_arming_required", True),
        "missing_timeout_requirement": ("timeout_required", True),
    }
    for key, (field, expect_true) in required_truthy.items():
        value = _coalesce_bool(state, field)
        if value is None or value != expect_true:
            blockers.append(key)

    if not _to_bool(state.get("approval_window_active")):
        blockers.append("approval_window_inactive")
    if _to_bool(state.get("account_boundary_freshness")) is False:
        blockers.append("missing_account_boundary_freshness")
    if state.get("account_boundary_expired") is True:
        blockers.append("account_boundary_expired")

    unsafe_flags = [
        "credential_access_detected",
        "account_identifier_access_detected",
        "broker_connection_detected",
        "network_access_detected",
        "order_execution_detected",
        "live_trading_authorization_detected",
        "execution_authority_detected",
        "capital_allocation_detected",
        "retry_loop_detected",
        "autonomous_reentry_detected",
    ]
    for flag in unsafe_flags:
        if state.get(flag):
            blockers.append(flag)

    blockers = _dedup(blockers)

    status = ACCOUNT_BOUNDARY_REVIEW_READY
    if "account_boundary_revoked" in blockers:
        status = ACCOUNT_BOUNDARY_REVOKED
    elif any(b.startswith("rejected_") for b in blockers):
        status = ACCOUNT_BOUNDARY_REJECTED
    elif "account_boundary_expired" in blockers or "missing_account_boundary_freshness" in blockers or "approval_window_inactive" in blockers:
        status = ACCOUNT_BOUNDARY_EXPIRED
    elif any(b in blockers for b in {
        "credential_access_detected",
        "account_identifier_access_detected",
        "broker_connection_detected",
        "network_access_detected",
        "order_execution_detected",
        "live_trading_authorization_detected",
        "execution_authority_detected",
        "capital_allocation_detected",
        "retry_loop_detected",
        "autonomous_reentry_detected",
    }) and status == ACCOUNT_BOUNDARY_REVIEW_READY:
        status = ACCOUNT_BOUNDARY_BLOCKED
    elif blockers:
        status = ACCOUNT_BOUNDARY_INCOMPLETE

    warnings = []
    if status == ACCOUNT_BOUNDARY_EXPIRED:
        warnings.append("boundary expired")
    if status == ACCOUNT_BOUNDARY_REVOKED:
        warnings.append("boundary revoked")
    if status == ACCOUNT_BOUNDARY_REJECTED:
        warnings.append("upstream rejection present")

    return {
        "account_boundary_completed": status == ACCOUNT_BOUNDARY_REVIEW_READY,
        "account_boundary_status": status,
        "account_boundary_ready": status == ACCOUNT_BOUNDARY_REVIEW_READY,
        "account_boundary_blocked": status in {ACCOUNT_BOUNDARY_INCOMPLETE, ACCOUNT_BOUNDARY_BLOCKED},
        "account_boundary_review_required": status == ACCOUNT_BOUNDARY_REVIEW_READY,
        "account_boundary_summary": {
            "status": status,
            "block_count": len(blockers),
            "limits": optional_limits,
        },
        "account_boundary_blockers": blockers,
        "account_boundary_warnings": warnings,
        "account_boundary_next_safe_action": _next_safe_action(blockers),
        "account_boundary_required_next_packets": ["AIOS_FOREX_BROKER_DEMO_NO_ORDER_CONNECTOR_DESIGN_V1"],
        "account_boundary_contract": contract,
        "redaction_contract": redaction_contract,
        "safety": safety,
    }
