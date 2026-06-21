"""Deterministic dry-run broker-demo connector evaluator for Forex delivery."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping, Tuple


STATUS_BLOCKED = "BROKER_DEMO_DRY_RUN_BLOCKED"
STATUS_INCOMPLETE = "BROKER_DEMO_DRY_RUN_INCOMPLETE"
STATUS_READY = "BROKER_DEMO_DRY_RUN_READY"
STATUS_REJECTED = "BROKER_DEMO_DRY_RUN_REJECTED"
STATUS_REVOKED = "BROKER_DEMO_DRY_RUN_REVOKED"
STATUS_EXPIRED = "BROKER_DEMO_DRY_RUN_EXPIRED"


def _as_bool(value: Any) -> bool:
    return bool(value)


def _first_value(state: Mapping[str, Any], keys: Iterable[str]) -> tuple[str | None, Any]:
    for key in reversed(list(keys)):
        if key in state:
            return key, state[key]
    return None, None


def _has_truthy_alias(state: Mapping[str, Any], keys: Iterable[str]) -> bool:
    for key in keys:
        if key in state and _as_bool(state[key]):
            return True
    return False


def _dedupe(items: Iterable[str]) -> List[str]:
    return sorted(set(items))


def _required_status_map() -> List[Tuple[str, str, List[str], str, str, str]]:
    return [
        ("runtime_plan_status", "PROTECTED_RUNTIME_PLAN_REVIEW_READY", ["runtime_plan_status", "protected_runtime_plan_status"], "missing_runtime_plan", "runtime_plan_not_ready", "rejected_runtime_plan"),
        ("approval_workflow_status", "APPROVAL_WORKFLOW_REVIEW_READY", ["approval_workflow_status", "approval_status"], "missing_approval_workflow", "approval_workflow_not_ready", "rejected_approval_workflow"),
        ("protected_connector_gate_status", "PROTECTED_CONNECTOR_GATE_REVIEW_READY", ["protected_connector_gate_status", "connector_gate_status"], "missing_protected_connector_gate", "protected_connector_gate_not_ready", "rejected_protected_connector_gate"),
        ("broker_demo_runtime_review_status", "BROKER_DEMO_RUNTIME_REVIEW_READY", ["broker_demo_runtime_review_status", "broker_demo_review_status"], "missing_broker_demo_runtime_review", "broker_demo_runtime_review_not_ready", "rejected_broker_demo_runtime_review"),
        ("runtime_connector_status", "RUNTIME_CONNECTOR_REVIEW_READY", ["runtime_connector_status", "broker_demo_runtime_connector_status"], "missing_runtime_connector", "runtime_connector_not_ready", "rejected_runtime_connector"),
        ("connector_contract_status", "CONNECTOR_CONTRACT_REVIEW_READY", ["connector_contract_status", "live_review_connector_contract_status"], "missing_connector_contract", "connector_contract_not_ready", "rejected_connector_contract"),
        ("review_chain_status", "REVIEW_CHAIN_REVIEW_READY", ["review_chain_status", "chain_status"], "missing_review_chain", "review_chain_not_ready", "rejected_review_chain"),
        ("certificate_status", "LIVE_REVIEW_CERTIFICATE_REVIEW_READY", ["certificate_status", "live_review_certificate_status"], "missing_certificate", "certificate_not_ready", "rejected_certificate"),
        ("one_shot_status", "ONE_SHOT_EXCEPTION_REVIEW_READY", ["one_shot_status", "exception_package_status"], "missing_one_shot_package", "one_shot_package_not_ready", "rejected_one_shot_package"),
    ]


def _required_input_map() -> List[Tuple[str, str, List[str]]]:
    return [
        ("dry_run_request_present", "missing_dry_run_request", ["dry_run_request_present", "request_present"]),
        ("dry_run_trace", "missing_dry_run_trace", ["dry_run_trace", "request_trace"]),
        ("dry_run_scope", "missing_dry_run_scope", ["dry_run_scope", "request_scope"]),
        ("dry_run_owner", "missing_dry_run_owner", ["dry_run_owner", "request_owner"]),
        ("dry_run_expiration", "missing_dry_run_expiration", ["dry_run_expiration", "request_expiration"]),
        ("dry_run_freshness", "missing_dry_run_freshness", ["dry_run_freshness", "request_freshness"]),
        ("dry_run_audit_record", "missing_dry_run_audit_record", ["dry_run_audit_record", "request_audit_record"]),
        ("dry_run_handoff_boundary", "missing_dry_run_handoff_boundary", ["dry_run_handoff_boundary", "request_handoff_boundary"]),
        ("dry_run_connector_scope", "missing_dry_run_connector_scope", ["dry_run_connector_scope", "request_connector_scope"]),
        ("dry_run_request_shape", "missing_dry_run_request_shape", ["dry_run_request_shape", "request_shape"]),
        ("dry_run_response_shape", "missing_dry_run_response_shape", ["dry_run_response_shape", "response_shape"]),
        ("sanitized_payload_only", "missing_sanitized_payload_only", ["sanitized_payload_only", "sanitized_only"]),
    ]


def _required_control_map() -> List[Tuple[str, str, List[str], str | None]]:
    return [
        ("approval_trace", "missing_approval_trace", ["approval_trace", "approval"], None),
        ("approval_evidence_bundle", "missing_approval_evidence_bundle", ["approval_evidence_bundle", "approval_evidence"], None),
        ("approval_window_active", "approval_window_inactive", ["approval_window_active", "approval_active"], "approval_window_inactive"),
        ("runtime_plan_trace", "missing_runtime_plan_trace", ["runtime_plan_trace", "plan_trace"], None),
        ("runtime_plan_evidence_bundle", "missing_runtime_plan_evidence_bundle", ["runtime_plan_evidence_bundle", "plan_evidence_bundle"], None),
        ("replay_prevention", "missing_replay_prevention", ["replay_prevention", "anti_replay"], None),
        ("replay_proof", "missing_replay_proof", ["replay_proof", "replayability_proof", "replay"], None),
        ("reconciliation_proof", "missing_reconciliation_proof", ["reconciliation_proof", "reconciliation"], None),
        ("kill_switch_proof", "missing_kill_switch_proof", ["kill_switch_proof", "kill_switch"], None),
        ("rollback_proof", "missing_rollback_proof", ["rollback_proof", "rollback"], None),
        ("freshness_proof", "missing_freshness_proof", ["freshness_proof", "evidence_freshness", "evidence_fresh"], None),
        ("final_disarm_proof", "missing_final_disarm_proof", ["final_disarm_proof", "final_disarm"], None),
        ("one_shot_controls", "missing_one_shot_controls", ["one_shot_controls", "controls"], None),
        ("post_trade_journal_path", "missing_post_trade_journal_path", ["post_trade_journal_path", "journal_path"], None),
        ("operator_review_required", "missing_operator_review_requirement", ["operator_review_required"], None),
        ("manual_arming_required", "missing_manual_arming_requirement", ["manual_arming_required"], None),
        ("timeout_required", "missing_timeout_requirement", ["timeout_required"], None),
        ("no_retry_loop", "retry_loop_detected", ["no_retry_loop"], "retry_loop_detected"),
        ("no_autonomous_reentry", "autonomous_reentry_detected", ["no_autonomous_reentry"], "autonomous_reentry_detected"),
    ]


def _unsafe_runtime_map() -> List[Tuple[str, str]]:
    return [
        ("broker_connection_detected", "broker_connection_detected"),
        ("network_access_detected", "network_access_detected"),
        ("credential_access_detected", "credential_access_detected"),
        ("account_identifier_access_detected", "account_identifier_access_detected"),
        ("order_execution_detected", "order_execution_detected"),
        ("live_trading_authorization_detected", "live_trading_authorization_detected"),
        ("execution_authority_detected", "execution_authority_detected"),
        ("capital_allocation_detected", "capital_allocation_detected"),
    ]


def _required_next_packets_by_status(status: str) -> List[str]:
    return {
        STATUS_READY: sorted(["forex_dry_run_connector_handoff", "forex_dry_run_connector_safety_audit", "forex_dry_run_connector_prepare_review"]),
        STATUS_INCOMPLETE: sorted(["forex_dry_run_connector_collect_missing_inputs", "forex_dry_run_connector_collect_missing_proofs"]),
        STATUS_BLOCKED: sorted(["forex_dry_run_connector_clear_blockers", "forex_dry_run_connector_review_safety_flags"]),
        STATUS_REJECTED: sorted(["forex_dry_run_connector_reconcile_upstream_rejection", "forex_dry_run_connector_re_submit_review"]),
        STATUS_REVOKED: sorted(["forex_dry_run_connector_revoke_resolution", "forex_dry_run_connector_request_clearance"]),
        STATUS_EXPIRED: sorted(["forex_dry_run_connector_refresh_window", "forex_dry_run_connector_refresh_freshness", "forex_dry_run_connector_refresh_approval_window"]),
    }[status]


def _next_safe_action(status: str) -> str:
    return {
        STATUS_READY: "Proceed to dry-run handoff with strict simulation-only routing.",
        STATUS_INCOMPLETE: "Populate all mandatory fields/proofs and re-run the evaluator.",
        STATUS_BLOCKED: "Remove unsafe runtime flags and re-run only after proving dry-run-only execution boundaries.",
        STATUS_REJECTED: "Address upstream rejection sources and re-submit required approvals.",
        STATUS_REVOKED: "Resolve revocation event through the approved revocation workflow before re-running.",
        STATUS_EXPIRED: "Refresh freshness and approval-window evidence before re-running dry-run.",
    }[status]


def _status_to_summary(status: str, blockers: List[str]) -> str:
    if not blockers:
        return f"Broker demo connector dry-run status: {status}"
    return f"Broker demo connector dry-run status: {status}; blockers: {', '.join(blockers)}"


def _build_contract() -> Dict[str, Any]:
    required_fields = {
        "runtime_plan_required",
        "approval_workflow_required",
        "protected_connector_gate_required",
        "broker_demo_runtime_review_required",
        "runtime_connector_required",
        "connector_contract_required",
        "review_chain_required",
        "certificate_required",
        "one_shot_package_required",
        "dry_run_request_required",
        "dry_run_trace_required",
        "dry_run_scope_required",
        "dry_run_owner_required",
        "dry_run_expiration_required",
        "dry_run_freshness_required",
        "dry_run_audit_required",
        "dry_run_handoff_boundary_required",
        "dry_run_connector_scope_required",
        "dry_run_request_shape_required",
        "dry_run_response_shape_required",
        "sanitized_payload_required",
        "approval_trace_required",
        "approval_evidence_required",
        "approval_window_required",
        "runtime_plan_trace_required",
        "runtime_plan_evidence_required",
        "replay_prevention_required",
        "replay_required",
        "reconciliation_required",
        "kill_switch_required",
        "rollback_required",
        "freshness_required",
        "final_disarm_required",
        "one_shot_controls_required",
        "post_trade_journal_required",
        "operator_review_required",
        "manual_arming_required",
        "timeout_required",
        "no_retry_loop_required",
        "no_autonomous_reentry_required",
    }
    contract = {"contract_version": "BROKER_DEMO_CONNECTOR_DRY_RUN_V1"}
    contract.update({name: True for name in required_fields})
    contract.update(
        {
            "broker_connection_allowed": False,
            "network_access_allowed": False,
            "credential_access_allowed": False,
            "account_identifier_access_allowed": False,
            "order_execution_allowed": False,
            "live_trading_authorized": False,
            "execution_authority_granted": False,
        }
    )
    return contract


def _build_request_envelope() -> Dict[str, Any]:
    return {
        "envelope_version": "BROKER_DEMO_CONNECTOR_DRY_RUN_REQUEST_V1",
        "request_type": "BROKER_DEMO_DRY_RUN",
        "dry_run_only": True,
        "sanitized_payload_only": True,
        "broker_connection_requested": False,
        "network_requested": False,
        "credential_access_requested": False,
        "account_identifier_requested": False,
        "order_execution_requested": False,
        "live_trading_requested": False,
        "execution_authority_requested": False,
    }


def _build_response_envelope() -> Dict[str, Any]:
    return {
        "envelope_version": "BROKER_DEMO_CONNECTOR_DRY_RUN_RESPONSE_V1",
        "response_type": "BROKER_DEMO_DRY_RUN_RESULT",
        "dry_run_only": True,
        "sanitized_payload_only": True,
        "broker_connection_performed": False,
        "network_performed": False,
        "credential_access_performed": False,
        "account_identifier_access_performed": False,
        "order_execution_performed": False,
        "live_trading_performed": False,
        "execution_authority_granted": False,
    }


def _is_rejected_status(value: Any) -> bool:
    return isinstance(value, str) and "reject" in value.lower()


def evaluate_broker_demo_connector_dry_run(state: Mapping[str, Any] | None, optional_limits: Mapping[str, Any] | None = None) -> Dict[str, Any]:
    state_dict = dict(state or {})
    optional_limits = optional_limits or {}
    blockers: List[str] = []

    for _base_key, expected, aliases, missing_blocker, not_ready_blocker, reject_blocker in _required_status_map():
        _found_key, value = _first_value(state_dict, aliases)
        if value is None:
            blockers.append(missing_blocker)
            continue
        if value != expected:
            blockers.append(not_ready_blocker)
            if _is_rejected_status(value) or _as_bool(state_dict.get(reject_blocker, False)):
                blockers.append(reject_blocker)

    for _base_key, blocker, aliases in _required_input_map():
        if not _has_truthy_alias(state_dict, aliases):
            blockers.append(blocker)

    for _base_key, blocker, aliases, negative_blocker in _required_control_map():
        if not _has_truthy_alias(state_dict, aliases):
            blockers.append(blocker)
        if _base_key == "approval_window_active" and not _has_truthy_alias(state_dict, aliases) and negative_blocker:
            blockers.append(negative_blocker)

    for unsafe_key, blocker in _unsafe_runtime_map():
        if _as_bool(state_dict.get(unsafe_key, False)):
            blockers.append(blocker)

    freshness_keys = ["dry_run_freshness", "request_freshness"]
    freshness_present = any(k in state_dict for k in freshness_keys)
    freshness_value = any(_as_bool(state_dict.get(k, False)) for k in freshness_keys if k in state_dict)
    if freshness_present and not freshness_value:
            blockers.append("dry_run_expired")

    approval_window_keys = ["approval_window_active", "approval_active"]
    approval_window_present = any(k in state_dict for k in approval_window_keys)
    approval_window_value = any(_as_bool(state_dict.get(k, False)) for k in approval_window_keys if k in state_dict)
    if approval_window_present:
        if not approval_window_value:
            blockers.append("dry_run_expired")
    if _as_bool(state_dict.get("dry_run_expired", False)):
        blockers.append("dry_run_expired")

    if _as_bool(state_dict.get("dry_run_revoked", False)):
        blockers.append("dry_run_revoked")

    rejected = any(reject in blockers for reject in {
        "rejected_runtime_plan",
        "rejected_approval_workflow",
        "rejected_protected_connector_gate",
        "rejected_broker_demo_runtime_review",
        "rejected_runtime_connector",
        "rejected_connector_contract",
        "rejected_review_chain",
        "rejected_certificate",
        "rejected_one_shot_package",
    })

    revoked = _as_bool(state_dict.get("dry_run_revoked", False))
    expired = "dry_run_expired" in blockers and not revoked

    unsafe = any(flag in blockers for flag in {
        "broker_connection_detected",
        "network_access_detected",
        "credential_access_detected",
        "account_identifier_access_detected",
        "order_execution_detected",
        "live_trading_authorization_detected",
        "execution_authority_detected",
        "capital_allocation_detected",
    })

    if revoked:
        status = STATUS_REVOKED
    elif expired:
        status = STATUS_EXPIRED
    elif rejected:
        status = STATUS_REJECTED
    elif unsafe:
        status = STATUS_BLOCKED
    elif any(
        blocker in {"retry_loop_detected", "autonomous_reentry_detected"}
        or "missing_" in blocker
        or "_not_ready" in blocker
        for blocker in blockers
    ):
        status = STATUS_INCOMPLETE
    else:
        status = STATUS_READY

    blockers = _dedupe(blockers)
    return {
        "dry_run_completed": status == STATUS_READY,
        "dry_run_status": status,
        "dry_run_ready": status == STATUS_READY,
        "dry_run_blocked": status == STATUS_BLOCKED,
        "dry_run_review_required": status != STATUS_READY,
        "dry_run_summary": _status_to_summary(status, blockers),
        "dry_run_blockers": blockers,
        "dry_run_warnings": _dedupe([f"unexpected_optional_limit:{key}" for key in optional_limits if not key.startswith("_")]),
        "dry_run_next_safe_action": _next_safe_action(status),
        "dry_run_required_next_packets": _required_next_packets_by_status(status),
        "dry_run_request_envelope": _build_request_envelope(),
        "dry_run_response_envelope": _build_response_envelope(),
        "dry_run_contract": _build_contract(),
        "safety": {
            "broker_connection_active": False,
            "network_access": False,
            "credentials_accessed": False,
            "account_identifiers_accessed": False,
            "order_execution_enabled": False,
            "live_trading_authorized": False,
            "execution_authority_granted": False,
            "capital_allocated": False,
            "broker_demo_dry_run_only": True,
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
        },
    }
