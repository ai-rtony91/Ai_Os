from __future__ import annotations

from typing import Any, Dict, Mapping


CREDENTIAL_BOUNDARY_BLOCKED = "CREDENTIAL_BOUNDARY_BLOCKED"
CREDENTIAL_BOUNDARY_INCOMPLETE = "CREDENTIAL_BOUNDARY_INCOMPLETE"
CREDENTIAL_BOUNDARY_REVIEW_READY = "CREDENTIAL_BOUNDARY_REVIEW_READY"
CREDENTIAL_BOUNDARY_REJECTED = "CREDENTIAL_BOUNDARY_REJECTED"
CREDENTIAL_BOUNDARY_REVOKED = "CREDENTIAL_BOUNDARY_REVOKED"
CREDENTIAL_BOUNDARY_EXPIRED = "CREDENTIAL_BOUNDARY_EXPIRED"


def _to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in {"1", "true", "yes", "on", "pass", "passed", "ready", "complete", "present", "verified"}


def _read_first(mapping: Mapping[str, Any], *keys: str, default: Any = None) -> Any:
    for key in keys:
        if key in mapping:
            return mapping[key]
    return default


def _append(items: list[str], value: str) -> None:
    if value not in items:
        items.append(value)


def _present(value: Any) -> bool:
    if isinstance(value, Mapping):
        return any(_to_bool(value.get(k)) for k in ("present", "verified", "available", "complete", "ready"))
    return _to_bool(value)


def evaluate_broker_demo_credential_boundary(state: Mapping[str, Any] | None, optional_limits: Mapping[str, Any] | None = None) -> Dict[str, Any]:
    state = state or {}
    blockers: list[str] = []
    warnings: list[str] = []

    upstream = [
        (_read_first(state, "implementation_plan_status", "connector_implementation_plan_status", default=""), "IMPLEMENTATION_PLAN_REVIEW_READY", "missing_implementation_plan", "implementation_plan_not_ready", "rejected_implementation_plan"),
        (_read_first(state, "dry_run_orchestration_status", "broker_demo_dry_run_orchestration_status", default=""), "DRY_RUN_ORCHESTRATION_READY", "missing_dry_run_orchestration", "dry_run_orchestration_not_ready", "rejected_dry_run_orchestration"),
        (_read_first(state, "runtime_plan_status", "protected_runtime_plan_status", default=""), "PROTECTED_RUNTIME_PLAN_REVIEW_READY", "missing_runtime_plan", "runtime_plan_not_ready", "rejected_runtime_plan"),
        (_read_first(state, "approval_workflow_status", "approval_status", default=""), "APPROVAL_WORKFLOW_REVIEW_READY", "missing_approval_workflow", "approval_workflow_not_ready", "rejected_approval_workflow"),
        (_read_first(state, "protected_connector_gate_status", "connector_gate_status", default=""), "PROTECTED_CONNECTOR_GATE_REVIEW_READY", "missing_protected_connector_gate", "protected_connector_gate_not_ready", "rejected_protected_connector_gate"),
    ]

    rejected = False
    for value, expected, missing, not_ready, rejected_blocker in upstream:
        if not value:
            _append(blockers, missing)
        elif "REJECTED" in str(value).upper():
            _append(blockers, rejected_blocker)
            rejected = True
        elif str(value).strip() != expected:
            _append(blockers, not_ready)

    required = {
        "missing_credential_boundary_request": ("credential_boundary_request_present", "credential_request_present"),
        "missing_credential_boundary_trace": ("credential_boundary_trace", "credential_trace"),
        "missing_credential_boundary_scope": ("credential_boundary_scope", "credential_scope"),
        "missing_credential_boundary_owner": ("credential_boundary_owner", "credential_owner"),
        "missing_credential_boundary_expiration": ("credential_boundary_expiration", "credential_expiration"),
        "missing_credential_boundary_freshness": ("credential_boundary_freshness", "credential_freshness"),
        "missing_credential_boundary_audit_record": ("credential_boundary_audit_record", "credential_audit_record"),
        "missing_credential_boundary_handoff_boundary": ("credential_boundary_handoff_boundary", "credential_handoff_boundary"),
        "missing_credential_redaction_requirement": ("credential_redaction_required", "redaction_required"),
        "missing_credential_external_only_requirement": ("credential_external_only", "external_only_credentials"),
        "missing_credential_operator_injected_only_requirement": ("credential_operator_injected_only", "operator_injected_credentials_only"),
        "missing_credential_secret_scan_requirement": ("credential_secret_scan_required", "secret_scan_required"),
        "missing_credential_redacted_proof_requirement": ("credential_redacted_proof_required", "redacted_proof_required"),
        "missing_credential_access_proof_redacted_only_requirement": ("credential_access_proof_redacted_only", "access_proof_redacted_only"),
        "missing_approval_trace": ("approval_trace", "approval"),
        "missing_approval_evidence_bundle": ("approval_evidence_bundle", "approval_evidence"),
        "missing_runtime_plan_trace": ("runtime_plan_trace", "plan_trace"),
        "missing_runtime_plan_evidence_bundle": ("runtime_plan_evidence_bundle", "plan_evidence_bundle"),
        "missing_dry_run_orchestration_trace": ("dry_run_orchestration_trace", "dry_run_trace"),
        "missing_replay_prevention": ("replay_prevention", "anti_replay"),
        "missing_kill_switch_proof": ("kill_switch_proof", "kill_switch"),
        "missing_rollback_proof": ("rollback_proof", "rollback"),
        "missing_reconciliation_proof": ("reconciliation_proof", "reconciliation"),
        "missing_final_disarm_proof": ("final_disarm_proof", "final_disarm"),
        "missing_operator_review_requirement": ("operator_review_required",),
        "missing_manual_arming_requirement": ("manual_arming_required",),
        "missing_timeout_requirement": ("timeout_required",),
    }

    for blocker, keys in required.items():
        if not _present(_read_first(state, *keys, default=False)):
            _append(blockers, blocker)

    negative_rules = {
        "credential_committed_detected": ("credential_committed_detected", "credential_committed"),
        "credential_logged_detected": ("credential_logged_detected", "credential_logged"),
        "credential_reported_detected": ("credential_reported_detected", "credential_reported"),
        "credential_in_tests_detected": ("credential_in_tests_detected", "credential_in_tests"),
        "credential_in_fixtures_detected": ("credential_in_fixtures_detected", "credential_in_fixtures"),
        "credential_persisted_detected": ("credential_persisted_detected", "credential_persisted"),
        "retry_loop_detected": ("retry_loop_detected", "retry_loop_active"),
        "autonomous_reentry_detected": ("autonomous_reentry_detected", "autonomous_reentry_active"),
        "credential_access_detected": ("credential_access_detected", "credentials_accessed"),
        "account_identifier_access_detected": ("account_identifier_access_detected", "account_identifiers_accessed"),
        "broker_connection_detected": ("broker_connection_detected", "broker_connection_active"),
        "network_access_detected": ("network_access_detected", "network_access"),
        "order_execution_detected": ("order_execution_detected", "order_execution_enabled"),
        "live_trading_authorization_detected": ("live_trading_authorization_detected", "live_trading_authorized"),
        "execution_authority_detected": ("execution_authority_detected", "execution_authority_granted"),
        "capital_allocation_detected": ("capital_allocation_detected", "capital_allocated"),
    }

    unsafe_active = False
    for blocker, keys in negative_rules.items():
        if _to_bool(_read_first(state, *keys, default=False)):
            _append(blockers, blocker)
            unsafe_active = True

    if not _to_bool(_read_first(state, "approval_window_active", "approval_active", default=False)):
        _append(blockers, "approval_window_inactive")

    revoked = _to_bool(_read_first(state, "credential_boundary_revoked", default=False))
    expired = (
        _to_bool(_read_first(state, "credential_boundary_expired", default=False))
        or not _to_bool(_read_first(state, "credential_boundary_freshness", "credential_freshness", default=False))
        or not _to_bool(_read_first(state, "approval_window_active", "approval_active", default=False))
    )

    if revoked:
        _append(blockers, "credential_boundary_revoked")
        status = CREDENTIAL_BOUNDARY_REVOKED
    elif expired:
        _append(blockers, "credential_boundary_expired")
        status = CREDENTIAL_BOUNDARY_EXPIRED
    elif rejected:
        status = CREDENTIAL_BOUNDARY_REJECTED
    elif unsafe_active:
        status = CREDENTIAL_BOUNDARY_BLOCKED
    elif blockers:
        status = CREDENTIAL_BOUNDARY_INCOMPLETE
    else:
        status = CREDENTIAL_BOUNDARY_REVIEW_READY

    ready = status == CREDENTIAL_BOUNDARY_REVIEW_READY

    contract = {
        "contract_version": "BROKER_DEMO_CREDENTIAL_BOUNDARY_V1",
        "implementation_plan_required": True,
        "dry_run_orchestration_required": True,
        "runtime_plan_required": True,
        "approval_workflow_required": True,
        "protected_connector_gate_required": True,
        "credential_boundary_request_required": True,
        "credential_boundary_trace_required": True,
        "credential_boundary_scope_required": True,
        "credential_boundary_owner_required": True,
        "credential_boundary_expiration_required": True,
        "credential_boundary_freshness_required": True,
        "credential_boundary_audit_required": True,
        "credential_boundary_handoff_boundary_required": True,
        "credential_redaction_required": True,
        "credential_external_only_required": True,
        "credential_operator_injected_only_required": True,
        "credential_not_committed_required": True,
        "credential_not_logged_required": True,
        "credential_not_reported_required": True,
        "credential_not_in_tests_required": True,
        "credential_not_in_fixtures_required": True,
        "credential_not_persisted_required": True,
        "credential_secret_scan_required": True,
        "credential_redacted_proof_required": True,
        "credential_access_proof_redacted_only_required": True,
        "credential_access_allowed": False,
        "credential_storage_allowed": False,
        "credential_logging_allowed": False,
        "credential_reporting_allowed": False,
        "credential_test_fixture_allowed": False,
        "credential_persistence_allowed": False,
        "broker_connection_allowed": False,
        "network_access_allowed": False,
        "account_identifier_access_allowed": False,
        "order_execution_allowed": False,
        "live_trading_authorized": False,
        "execution_authority_granted": False,
    }

    redaction_contract = {
        "redaction_version": "BROKER_DEMO_CREDENTIAL_REDACTION_V1",
        "credential_values_allowed": False,
        "credential_hashes_allowed": False,
        "credential_lengths_allowed": False,
        "credential_prefixes_allowed": False,
        "credential_suffixes_allowed": False,
        "credential_redacted_proof_allowed": True,
        "credential_metadata_allowed": True,
        "credential_presence_boolean_allowed": True,
    }

    safety = {
        "credentials_accessed": False,
        "credential_values_visible": False,
        "credential_storage_allowed": False,
        "credential_logging_allowed": False,
        "credential_reporting_allowed": False,
        "credential_test_fixture_allowed": False,
        "credential_persistence_allowed": False,
        "account_identifiers_accessed": False,
        "broker_connection_active": False,
        "network_access": False,
        "order_execution_enabled": False,
        "live_trading_authorized": False,
        "execution_authority_granted": False,
        "capital_allocated": False,
        "credential_boundary_only": True,
        "operator_review_required": True,
        "manual_arming_required": True,
        "timeout_required": True,
        "no_retry_loop": True,
        "no_autonomous_reentry": True,
        "final_disarm_required": True,
        "replay_prevention_required": True,
    }

    return {
        "credential_boundary_completed": ready,
        "credential_boundary_status": status,
        "credential_boundary_ready": ready,
        "credential_boundary_blocked": status == CREDENTIAL_BOUNDARY_BLOCKED,
        "credential_boundary_review_required": True,
        "credential_boundary_summary": {"upstream_count": len(upstream), "blocker_count": len(blockers)},
        "credential_boundary_blockers": blockers,
        "credential_boundary_warnings": warnings,
        "credential_boundary_next_safe_action": "proceed_to_account_boundary" if ready else "resolve_credential_boundary_blockers",
        "credential_boundary_required_next_packets": [
            "AIOS_FOREX_BROKER_DEMO_ACCOUNT_BOUNDARY_V1",
            "AIOS_FOREX_BROKER_DEMO_NO_ORDER_CONNECTOR_DESIGN_V1",
        ],
        "credential_boundary_contract": contract,
        "redaction_contract": redaction_contract,
        "safety": safety,
    }