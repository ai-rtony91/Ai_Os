from __future__ import annotations

from typing import Any, Dict, Mapping


DRY_RUN_ORCHESTRATION_BLOCKED = "DRY_RUN_ORCHESTRATION_BLOCKED"
DRY_RUN_ORCHESTRATION_INCOMPLETE = "DRY_RUN_ORCHESTRATION_INCOMPLETE"
DRY_RUN_ORCHESTRATION_READY = "DRY_RUN_ORCHESTRATION_READY"
DRY_RUN_ORCHESTRATION_REJECTED = "DRY_RUN_ORCHESTRATION_REJECTED"
DRY_RUN_ORCHESTRATION_REVOKED = "DRY_RUN_ORCHESTRATION_REVOKED"
DRY_RUN_ORCHESTRATION_EXPIRED = "DRY_RUN_ORCHESTRATION_EXPIRED"


def _to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in {
        "1", "true", "yes", "on", "pass", "passed", "ready", "complete", "present", "verified"
    }


def _read_first(mapping: Mapping[str, Any], *keys: str, default: Any = None) -> Any:
    for key in keys:
        if key in mapping:
            return mapping[key]
    return default


def _append(items: list[str], value: str) -> None:
    if value not in items:
        items.append(value)


def _proof_present(value: Any) -> bool:
    if isinstance(value, Mapping):
        return any(_to_bool(value.get(k)) for k in ("present", "verified", "available", "complete", "ready"))
    return _to_bool(value)


def orchestrate_broker_demo_dry_run(
    state: Mapping[str, Any] | None,
    optional_limits: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    state = state or {}
    blockers: list[str] = []
    warnings: list[str] = []

    statuses = {
        "dry_run_status": (
            _read_first(state, "dry_run_status", "broker_demo_dry_run_status", default=""),
            "BROKER_DEMO_DRY_RUN_READY",
            "missing_dry_run_connector",
            "dry_run_connector_not_ready",
            "rejected_dry_run_connector",
        ),
        "runtime_plan_status": (
            _read_first(state, "runtime_plan_status", "protected_runtime_plan_status", default=""),
            "PROTECTED_RUNTIME_PLAN_REVIEW_READY",
            "missing_runtime_plan",
            "runtime_plan_not_ready",
            "rejected_runtime_plan",
        ),
        "approval_workflow_status": (
            _read_first(state, "approval_workflow_status", "approval_status", default=""),
            "APPROVAL_WORKFLOW_REVIEW_READY",
            "missing_approval_workflow",
            "approval_workflow_not_ready",
            "rejected_approval_workflow",
        ),
        "protected_connector_gate_status": (
            _read_first(state, "protected_connector_gate_status", "connector_gate_status", default=""),
            "PROTECTED_CONNECTOR_GATE_REVIEW_READY",
            "missing_protected_connector_gate",
            "protected_connector_gate_not_ready",
            "rejected_protected_connector_gate",
        ),
        "broker_demo_runtime_review_status": (
            _read_first(state, "broker_demo_runtime_review_status", "broker_demo_review_status", default=""),
            "BROKER_DEMO_RUNTIME_REVIEW_READY",
            "missing_broker_demo_runtime_review",
            "broker_demo_runtime_review_not_ready",
            "rejected_broker_demo_runtime_review",
        ),
        "runtime_connector_status": (
            _read_first(state, "runtime_connector_status", "broker_demo_runtime_connector_status", default=""),
            "RUNTIME_CONNECTOR_REVIEW_READY",
            "missing_runtime_connector",
            "runtime_connector_not_ready",
            "rejected_runtime_connector",
        ),
        "connector_contract_status": (
            _read_first(state, "connector_contract_status", "live_review_connector_contract_status", default=""),
            "CONNECTOR_CONTRACT_REVIEW_READY",
            "missing_connector_contract",
            "connector_contract_not_ready",
            "rejected_connector_contract",
        ),
        "review_chain_status": (
            _read_first(state, "review_chain_status", "chain_status", default=""),
            "REVIEW_CHAIN_REVIEW_READY",
            "missing_review_chain",
            "review_chain_not_ready",
            "rejected_review_chain",
        ),
        "certificate_status": (
            _read_first(state, "certificate_status", "live_review_certificate_status", default=""),
            "LIVE_REVIEW_CERTIFICATE_REVIEW_READY",
            "missing_certificate",
            "certificate_not_ready",
            "rejected_certificate",
        ),
        "one_shot_status": (
            _read_first(state, "one_shot_status", "exception_package_status", default=""),
            "ONE_SHOT_EXCEPTION_REVIEW_READY",
            "missing_one_shot_package",
            "one_shot_package_not_ready",
            "rejected_one_shot_package",
        ),
    }

    rejected = False
    for value, expected, missing_blocker, not_ready_blocker, rejected_blocker in statuses.values():
        if not value:
            _append(blockers, missing_blocker)
        elif "REJECTED" in str(value).upper():
            _append(blockers, rejected_blocker)
            rejected = True
        elif str(value).strip() != expected:
            _append(blockers, not_ready_blocker)

    required_fields = {
        "missing_orchestration_request": ("orchestration_request_present", "dry_run_orchestration_request_present"),
        "missing_orchestration_trace": ("orchestration_trace", "dry_run_orchestration_trace"),
        "missing_orchestration_scope": ("orchestration_scope", "dry_run_orchestration_scope"),
        "missing_orchestration_owner": ("orchestration_owner", "dry_run_orchestration_owner"),
        "missing_orchestration_expiration": ("orchestration_expiration", "dry_run_orchestration_expiration"),
        "missing_orchestration_freshness": ("orchestration_freshness", "dry_run_orchestration_freshness"),
        "missing_orchestration_audit_record": ("orchestration_audit_record", "dry_run_orchestration_audit_record"),
        "missing_orchestration_handoff_boundary": ("orchestration_handoff_boundary", "dry_run_orchestration_handoff_boundary"),
        "missing_orchestration_connector_scope": ("orchestration_connector_scope", "dry_run_orchestration_connector_scope"),
        "missing_orchestration_replay_id": ("orchestration_replay_id", "dry_run_replay_id"),
        "missing_orchestration_idempotency_key": ("orchestration_idempotency_key", "dry_run_idempotency_key"),
        "missing_orchestration_result_sink": ("orchestration_result_sink", "dry_run_result_sink"),
        "missing_sanitized_payload_only": ("sanitized_payload_only", "sanitized_only"),
        "missing_dry_run_trace": ("dry_run_trace", "request_trace"),
        "missing_dry_run_request_shape": ("dry_run_request_shape", "request_shape"),
        "missing_dry_run_response_shape": ("dry_run_response_shape", "response_shape"),
        "missing_runtime_plan_trace": ("runtime_plan_trace", "plan_trace"),
        "missing_runtime_plan_evidence_bundle": ("runtime_plan_evidence_bundle", "plan_evidence_bundle"),
        "missing_approval_trace": ("approval_trace", "approval"),
        "missing_approval_evidence_bundle": ("approval_evidence_bundle", "approval_evidence"),
        "missing_replay_prevention": ("replay_prevention", "anti_replay"),
        "missing_replay_proof": ("replay_proof", "replayability_proof", "replay"),
        "missing_reconciliation_proof": ("reconciliation_proof", "reconciliation"),
        "missing_kill_switch_proof": ("kill_switch_proof", "kill_switch"),
        "missing_rollback_proof": ("rollback_proof", "rollback"),
        "missing_freshness_proof": ("freshness_proof", "evidence_freshness", "evidence_fresh"),
        "missing_final_disarm_proof": ("final_disarm_proof", "final_disarm"),
        "missing_one_shot_controls": ("one_shot_controls", "controls"),
        "missing_post_trade_journal_path": ("post_trade_journal_path", "journal_path"),
        "missing_operator_review_requirement": ("operator_review_required",),
        "missing_manual_arming_requirement": ("manual_arming_required",),
        "missing_timeout_requirement": ("timeout_required",),
    }

    for blocker, keys in required_fields.items():
        if not _proof_present(_read_first(state, *keys, default=False)):
            _append(blockers, blocker)

    if not _to_bool(_read_first(state, "approval_window_active", "approval_active", default=False)):
        _append(blockers, "approval_window_inactive")

    unsafe = {
        "retry_loop_detected": ("retry_loop_detected", "retry_loop_active"),
        "autonomous_reentry_detected": ("autonomous_reentry_detected", "autonomous_reentry_active"),
        "broker_connection_detected": ("broker_connection_active", "broker_connection_detected"),
        "network_access_detected": ("network_access", "network_access_detected"),
        "credential_access_detected": ("credentials_accessed", "credential_access_detected"),
        "account_identifier_access_detected": ("account_identifiers_accessed", "account_identifier_access_detected"),
        "order_execution_detected": ("order_execution_enabled", "order_execution_detected"),
        "live_trading_authorization_detected": ("live_trading_authorized", "live_trading_authorization_detected"),
        "execution_authority_detected": ("execution_authority_granted", "execution_authority_detected"),
        "capital_allocation_detected": ("capital_allocated", "capital_allocation_detected"),
    }

    unsafe_active = False
    for blocker, keys in unsafe.items():
        if _to_bool(_read_first(state, *keys, default=False)):
            _append(blockers, blocker)
            unsafe_active = True

    revoked = _to_bool(_read_first(state, "dry_run_orchestration_revoked", default=False))
    expired = (
        _to_bool(_read_first(state, "dry_run_orchestration_expired", default=False))
        or not _to_bool(_read_first(state, "orchestration_freshness", "dry_run_orchestration_freshness", default=False))
        or not _to_bool(_read_first(state, "approval_window_active", "approval_active", default=False))
    )

    if revoked:
        _append(blockers, "dry_run_orchestration_revoked")
        status = DRY_RUN_ORCHESTRATION_REVOKED
    elif expired:
        _append(blockers, "dry_run_orchestration_expired")
        status = DRY_RUN_ORCHESTRATION_EXPIRED
    elif rejected:
        status = DRY_RUN_ORCHESTRATION_REJECTED
    elif unsafe_active:
        status = DRY_RUN_ORCHESTRATION_BLOCKED
    elif blockers:
        status = DRY_RUN_ORCHESTRATION_INCOMPLETE
    else:
        status = DRY_RUN_ORCHESTRATION_READY

    ready = status == DRY_RUN_ORCHESTRATION_READY

    contract = {
        "contract_version": "BROKER_DEMO_DRY_RUN_ORCHESTRATOR_V1",
        "dry_run_connector_required": True,
        "runtime_plan_required": True,
        "approval_workflow_required": True,
        "protected_connector_gate_required": True,
        "broker_demo_runtime_review_required": True,
        "runtime_connector_required": True,
        "connector_contract_required": True,
        "review_chain_required": True,
        "certificate_required": True,
        "one_shot_package_required": True,
        "orchestration_request_required": True,
        "orchestration_trace_required": True,
        "orchestration_scope_required": True,
        "orchestration_owner_required": True,
        "orchestration_expiration_required": True,
        "orchestration_freshness_required": True,
        "orchestration_audit_required": True,
        "orchestration_handoff_boundary_required": True,
        "orchestration_connector_scope_required": True,
        "orchestration_replay_id_required": True,
        "orchestration_idempotency_key_required": True,
        "orchestration_result_sink_required": True,
        "sanitized_payload_required": True,
        "dry_run_trace_required": True,
        "dry_run_request_shape_required": True,
        "dry_run_response_shape_required": True,
        "runtime_plan_trace_required": True,
        "runtime_plan_evidence_required": True,
        "approval_trace_required": True,
        "approval_evidence_required": True,
        "approval_window_required": True,
        "replay_prevention_required": True,
        "replay_required": True,
        "reconciliation_required": True,
        "kill_switch_required": True,
        "rollback_required": True,
        "freshness_required": True,
        "final_disarm_required": True,
        "one_shot_controls_required": True,
        "post_trade_journal_required": True,
        "operator_review_required": True,
        "manual_arming_required": True,
        "timeout_required": True,
        "no_retry_loop_required": True,
        "no_autonomous_reentry_required": True,
        "broker_connection_allowed": False,
        "network_access_allowed": False,
        "credential_access_allowed": False,
        "account_identifier_access_allowed": False,
        "order_execution_allowed": False,
        "live_trading_authorized": False,
        "execution_authority_granted": False,
    }

    handoff = {
        "handoff_version": "BROKER_DEMO_DRY_RUN_HANDOFF_V1",
        "handoff_type": "BROKER_DEMO_DRY_RUN_ORCHESTRATION",
        "dry_run_only": True,
        "simulation_only": True,
        "sanitized_payload_only": True,
        "broker_connection_performed": False,
        "network_performed": False,
        "credential_access_performed": False,
        "account_identifier_access_performed": False,
        "order_execution_performed": False,
        "live_trading_performed": False,
        "execution_authority_granted": False,
        "ready_for_future_broker_demo_connector_review": ready,
    }

    safety = {
        "broker_connection_active": False,
        "network_access": False,
        "credentials_accessed": False,
        "account_identifiers_accessed": False,
        "order_execution_enabled": False,
        "live_trading_authorized": False,
        "execution_authority_granted": False,
        "capital_allocated": False,
        "broker_demo_dry_run_orchestration_only": True,
        "simulation_only": True,
        "sanitized_payload_only": True,
        "broker_demo_connector_not_active": True,
        "operator_review_required": True,
        "manual_arming_required": True,
        "timeout_required": True,
        "no_retry_loop": True,
        "no_autonomous_reentry": True,
        "final_disarm_required": True,
        "revocation_path_required": True,
        "replay_prevention_required": True,
    }

    return {
        "dry_run_orchestration_completed": ready,
        "dry_run_orchestration_status": status,
        "dry_run_orchestration_ready": ready,
        "dry_run_orchestration_blocked": status == DRY_RUN_ORCHESTRATION_BLOCKED,
        "dry_run_orchestration_review_required": True,
        "dry_run_orchestration_summary": {name: values[0] for name, values in statuses.items()},
        "dry_run_orchestration_blockers": blockers,
        "dry_run_orchestration_warnings": warnings,
        "dry_run_orchestration_next_safe_action": (
            "proceed_to_future_broker_demo_connector_review" if ready else "resolve_dry_run_orchestration_blockers"
        ),
        "dry_run_orchestration_required_next_packets": [
            "AIOS_FOREX_PROTECTED_BROKER_DEMO_CONNECTOR_REVIEW_V1",
            "AIOS_FOREX_BROKER_DEMO_CONNECTOR_IMPLEMENTATION_PLAN_V1",
            "AIOS_FOREX_BROKER_DEMO_CREDENTIAL_BOUNDARY_V1",
        ],
        "dry_run_orchestration_contract": contract,
        "dry_run_handoff_package": handoff,
        "safety": safety,
    }