"""Protected broker-demo runtime plan evaluator."""

from __future__ import annotations

from typing import Any, Dict, Iterable, Mapping, Sequence


PROTECTED_RUNTIME_PLAN_BLOCKED = "PROTECTED_RUNTIME_PLAN_BLOCKED"
PROTECTED_RUNTIME_PLAN_INCOMPLETE = "PROTECTED_RUNTIME_PLAN_INCOMPLETE"
PROTECTED_RUNTIME_PLAN_REVIEW_READY = "PROTECTED_RUNTIME_PLAN_REVIEW_READY"
PROTECTED_RUNTIME_PLAN_REJECTED = "PROTECTED_RUNTIME_PLAN_REJECTED"
PROTECTED_RUNTIME_PLAN_REVOKED = "PROTECTED_RUNTIME_PLAN_REVOKED"
PROTECTED_RUNTIME_PLAN_EXPIRED = "PROTECTED_RUNTIME_PLAN_EXPIRED"

APPROVAL_WORKFLOW_REVIEW_READY = "APPROVAL_WORKFLOW_REVIEW_READY"
APPROVAL_WORKFLOW_REJECTED = "APPROVAL_WORKFLOW_REJECTED"
APPROVAL_WORKFLOW_REVOKED = "APPROVAL_WORKFLOW_REVOKED"
APPROVAL_WORKFLOW_EXPIRED = "APPROVAL_WORKFLOW_EXPIRED"

PROTECTED_CONNECTOR_GATE_REVIEW_READY = "PROTECTED_CONNECTOR_GATE_REVIEW_READY"
PROTECTED_CONNECTOR_GATE_REJECTED = "PROTECTED_CONNECTOR_GATE_REJECTED"
PROTECTED_CONNECTOR_GATE_REVOKED = "PROTECTED_CONNECTOR_GATE_REVOKED"
PROTECTED_CONNECTOR_GATE_EXPIRED = "PROTECTED_CONNECTOR_GATE_EXPIRED"

BROKER_DEMO_RUNTIME_REVIEW_READY = "BROKER_DEMO_RUNTIME_REVIEW_READY"
BROKER_DEMO_RUNTIME_REVIEW_REJECTED = "BROKER_DEMO_RUNTIME_REVIEW_REJECTED"
RUNTIME_CONNECTOR_REVIEW_READY = "RUNTIME_CONNECTOR_REVIEW_READY"
RUNTIME_CONNECTOR_REJECTED = "RUNTIME_CONNECTOR_REJECTED"
CONNECTOR_CONTRACT_REVIEW_READY = "CONNECTOR_CONTRACT_REVIEW_READY"
CONNECTOR_CONTRACT_REJECTED = "CONNECTOR_CONTRACT_REJECTED"
REVIEW_CHAIN_REVIEW_READY = "REVIEW_CHAIN_REVIEW_READY"
REVIEW_CHAIN_REJECTED = "REVIEW_CHAIN_REJECTED"
LIVE_REVIEW_CERTIFICATE_REVIEW_READY = "LIVE_REVIEW_CERTIFICATE_REVIEW_READY"
LIVE_REVIEW_CERTIFICATE_REJECTED = "LIVE_REVIEW_CERTIFICATE_REJECTED"
ONE_SHOT_EXCEPTION_REVIEW_READY = "ONE_SHOT_EXCEPTION_REVIEW_READY"
ONE_SHOT_EXCEPTION_REJECTED = "ONE_SHOT_EXCEPTION_REJECTED"

REQUIRED_BLOCKERS_ORDER: Sequence[str] = [
    "missing_approval_workflow",
    "approval_workflow_not_ready",
    "missing_protected_connector_gate",
    "protected_connector_gate_not_ready",
    "missing_broker_demo_runtime_review",
    "broker_demo_runtime_review_not_ready",
    "missing_runtime_connector",
    "runtime_connector_not_ready",
    "missing_connector_contract",
    "connector_contract_not_ready",
    "missing_review_chain",
    "review_chain_not_ready",
    "missing_certificate",
    "certificate_not_ready",
    "missing_one_shot_package",
    "one_shot_package_not_ready",
    "missing_runtime_plan_request",
    "missing_runtime_plan_trace",
    "missing_runtime_plan_evidence_bundle",
    "missing_runtime_plan_scope",
    "missing_runtime_plan_owner",
    "missing_runtime_plan_expiration",
    "missing_runtime_plan_freshness",
    "missing_runtime_plan_revocation_path",
    "missing_runtime_plan_audit_record",
    "missing_runtime_plan_connector_scope",
    "missing_runtime_plan_handoff_boundary",
    "missing_approval_trace",
    "missing_approval_evidence_bundle",
    "approval_window_inactive",
    "missing_replay_prevention",
    "missing_replay_proof",
    "missing_reconciliation_proof",
    "missing_kill_switch_proof",
    "missing_rollback_proof",
    "missing_freshness_proof",
    "missing_final_disarm_proof",
    "missing_one_shot_controls",
    "missing_post_trade_journal_path",
    "missing_operator_review_requirement",
    "missing_manual_arming_requirement",
    "missing_timeout_requirement",
    "retry_loop_detected",
    "autonomous_reentry_detected",
    "broker_connection_detected",
    "network_access_detected",
    "credential_access_detected",
    "account_identifier_access_detected",
    "order_execution_detected",
    "live_trading_authorization_detected",
    "execution_authority_detected",
    "capital_allocation_detected",
    "runtime_plan_expired",
    "runtime_plan_revoked",
]


def _normalize_key(value: str) -> str:
    return "".join(c.lower() for c in str(value) if c.isalnum())


def _normalize_inputs(state: Mapping[str, Any] | None) -> Dict[str, Any]:
    if state is None:
        return {}

    alias_map = {
        "approval_workflow_status": "approval_workflow_status",
        "approval_status": "approval_workflow_status",
        "protected_connector_gate_status": "protected_connector_gate_status",
        "connector_gate_status": "protected_connector_gate_status",
        "broker_demo_runtime_review_status": "broker_demo_runtime_review_status",
        "broker_demo_review_status": "broker_demo_runtime_review_status",
        "runtime_connector_status": "runtime_connector_status",
        "broker_demo_runtime_connector_status": "runtime_connector_status",
        "connector_contract_status": "connector_contract_status",
        "live_review_connector_contract_status": "connector_contract_status",
        "review_chain_status": "review_chain_status",
        "chain_status": "review_chain_status",
        "certificate_status": "certificate_status",
        "live_review_certificate_status": "certificate_status",
        "one_shot_status": "one_shot_status",
        "exception_package_status": "one_shot_status",

        "runtime_plan_request_present": "runtime_plan_request_present",
        "plan_request_present": "runtime_plan_request_present",
        "runtime_plan_trace": "runtime_plan_trace",
        "plan_trace": "runtime_plan_trace",
        "runtime_plan_evidence_bundle": "runtime_plan_evidence_bundle",
        "plan_evidence_bundle": "runtime_plan_evidence_bundle",
        "runtime_plan_scope": "runtime_plan_scope",
        "plan_scope": "runtime_plan_scope",
        "runtime_plan_owner": "runtime_plan_owner",
        "plan_owner": "runtime_plan_owner",
        "runtime_plan_expiration": "runtime_plan_expiration",
        "plan_expiration": "runtime_plan_expiration",
        "runtime_plan_freshness": "runtime_plan_freshness",
        "plan_freshness": "runtime_plan_freshness",
        "runtime_plan_revocation_path": "runtime_plan_revocation_path",
        "plan_revocation_path": "runtime_plan_revocation_path",
        "runtime_plan_audit_record": "runtime_plan_audit_record",
        "plan_audit_record": "runtime_plan_audit_record",
        "runtime_plan_connector_scope": "runtime_plan_connector_scope",
        "plan_connector_scope": "runtime_plan_connector_scope",
        "runtime_plan_handoff_boundary": "runtime_plan_handoff_boundary",
        "plan_handoff_boundary": "runtime_plan_handoff_boundary",

        "approval_trace": "approval_trace",
        "approval": "approval_trace",
        "approval_evidence_bundle": "approval_evidence_bundle",
        "approval_evidence": "approval_evidence_bundle",
        "approval_window_active": "approval_window_active",
        "approval_active": "approval_window_active",
        "replay_prevention": "replay_prevention",
        "anti_replay": "replay_prevention",
        "replay_proof": "replay_proof",
        "replayability_proof": "replay_proof",
        "replay": "replay_proof",
        "reconciliation_proof": "reconciliation_proof",
        "reconciliation": "reconciliation_proof",
        "kill_switch_proof": "kill_switch_proof",
        "kill_switch": "kill_switch_proof",
        "rollback_proof": "rollback_proof",
        "rollback": "rollback_proof",
        "freshness_proof": "freshness_proof",
        "evidence_freshness": "freshness_proof",
        "evidence_fresh": "freshness_proof",
        "final_disarm_proof": "final_disarm_proof",
        "final_disarm": "final_disarm_proof",
        "one_shot_controls": "one_shot_controls",
        "controls": "one_shot_controls",
        "post_trade_journal_path": "post_trade_journal_path",
        "journal_path": "post_trade_journal_path",

        "operator_review_required": "operator_review_required",
        "manual_arming_required": "manual_arming_required",
        "timeout_required": "timeout_required",
        "no_retry_loop": "no_retry_loop",
        "no_autonomous_reentry": "no_autonomous_reentry",
        "runtime_plan_expired": "runtime_plan_expired",
        "runtime_plan_revoked": "runtime_plan_revoked",
        "broker_connection_detected": "broker_connection_detected",
        "network_access_detected": "network_access_detected",
        "credential_access_detected": "credential_access_detected",
        "account_identifier_access_detected": "account_identifier_access_detected",
        "order_execution_detected": "order_execution_detected",
        "live_trading_authorization_detected": "live_trading_authorization_detected",
        "execution_authority_detected": "execution_authority_detected",
        "capital_allocation_detected": "capital_allocation_detected",
        "approval_window_inactive": "approval_window_inactive",
    }

    raw_aliases = {_normalize_key(key): canonical for key, canonical in alias_map.items()}
    normalized: Dict[str, Any] = {}
    for key, value in dict(state).items():
        normalized_key = _normalize_key(key)
        canonical = raw_aliases.get(normalized_key, normalized_key)
        normalized[canonical] = value

    return normalized


def _append(blockers: list[str], blocker: str) -> None:
    if blocker not in blockers:
        blockers.append(blocker)


def _to_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "on", "ready", "complete", "pass", "passed", "active", "required"}:
        return True
    if text in {"0", "false", "no", "off", "inactive", "fail", "failed", "blocked", "rejected", "not ready"}:
        return False
    return bool(value)


def _is_present_proof(value: Any) -> bool:
    if isinstance(value, Mapping):
        return any(_to_bool(value.get(field, False), default=False) for field in ("present", "verified", "available", "fresh", "active", "enabled", "ok"))
    return _to_bool(value, default=False)


def _read_first(mapping: Mapping[str, Any], aliases: Iterable[str], default: Any = None) -> Any:
    for key in aliases:
        if key in mapping:
            return mapping[key]
    return default


def _required_input_blockers(state: Mapping[str, Any], blockers: list[str]) -> None:
    requirements = [
        ("runtime_plan_request_present", "missing_runtime_plan_request"),
        ("runtime_plan_trace", "missing_runtime_plan_trace"),
        ("runtime_plan_evidence_bundle", "missing_runtime_plan_evidence_bundle"),
        ("runtime_plan_scope", "missing_runtime_plan_scope"),
        ("runtime_plan_owner", "missing_runtime_plan_owner"),
        ("runtime_plan_expiration", "missing_runtime_plan_expiration"),
        ("runtime_plan_freshness", "missing_runtime_plan_freshness"),
        ("runtime_plan_revocation_path", "missing_runtime_plan_revocation_path"),
        ("runtime_plan_audit_record", "missing_runtime_plan_audit_record"),
        ("runtime_plan_connector_scope", "missing_runtime_plan_connector_scope"),
        ("runtime_plan_handoff_boundary", "missing_runtime_plan_handoff_boundary"),
    ]
    for field, blocker in requirements:
        if field == "runtime_plan_request_present":
            if not _to_bool(state.get(field), default=False):
                _append(blockers, blocker)
        else:
            value = state.get(field)
            if value is None or (isinstance(value, str) and value.strip() == ""):
                _append(blockers, blocker)


def _required_control_blockers(state: Mapping[str, Any], blockers: list[str]) -> None:
    controls = [
        ("approval_trace", "missing_approval_trace"),
        ("approval_evidence_bundle", "missing_approval_evidence_bundle"),
        ("replay_prevention", "missing_replay_prevention"),
        ("replay_proof", "missing_replay_proof"),
        ("reconciliation_proof", "missing_reconciliation_proof"),
        ("kill_switch_proof", "missing_kill_switch_proof"),
        ("rollback_proof", "missing_rollback_proof"),
        ("freshness_proof", "missing_freshness_proof"),
        ("final_disarm_proof", "missing_final_disarm_proof"),
        ("post_trade_journal_path", "missing_post_trade_journal_path"),
    ]
    for field, blocker in controls:
        if not _is_present_proof(state.get(field)):
            _append(blockers, blocker)


def _status_field(blockers: list[str], field: str, expected: str, missing_msg: str, not_ready_msg: str) -> str:
    if field not in blockers:
        pass
    value = None
    if field == "approval_workflow_status":
        value = None
    if field not in blockers:
        pass
    return ""


def _evaluate_status(
    value: Any,
    expected: str,
    missing_msg: str,
    not_ready_msg: str,
    reject_msg: str | None = None,
    blockers: list[str] | None = None,
) -> str:
    if blockers is None:
        blockers = []
    if value is None:
        _append(blockers, missing_msg)
        return not_ready_msg.replace("_not_ready", "_not_ready")
    if value == expected:
        return expected
    if reject_msg and value == reject_msg:
        _append(blockers, reject_msg.replace("REVIEW", "rejected").lower())
        return value
    _append(blockers, not_ready_msg)
    return value


def _required_next_packets(status: str) -> list[str]:
    if status == PROTECTED_RUNTIME_PLAN_REVIEW_READY:
        return [
            "collect_handoff_evidence_for_implementation_review",
            "run_implemented_connector_preflight_checklist",
        ]
    if status == PROTECTED_RUNTIME_PLAN_REJECTED:
        return [
            "repair_rejected_protected_runtime_plan_input",
            "request_human_intervention_for_plan_rejection",
            "refresh_upstream_review_outputs",
        ]
    if status == PROTECTED_RUNTIME_PLAN_EXPIRED:
        return [
            "refresh_runtime_plan_window",
            "refresh_runtime_plan_freshness",
        ]
    if status == PROTECTED_RUNTIME_PLAN_REVOKED:
        return [
            "revoke_runtime_plan",
            "request_new_runtime_plan_token",
            "restore_runtime_plan_authority",
        ]
    if status == PROTECTED_RUNTIME_PLAN_BLOCKED:
        return [
            "remove_unsafe_runtime_flags",
            "restore_plan_only_invariants",
        ]
    return [
        "collect_missing_protected_runtime_plan_inputs",
        "collect_missing_runtime_plan_proofs",
    ]


def _next_safe_action(status: str) -> str:
    if status == PROTECTED_RUNTIME_PLAN_REVIEW_READY:
        return "prepare_future_connector_implementation_packet"
    if status == PROTECTED_RUNTIME_PLAN_REJECTED:
        return "repair_rejected_runtime_plan_inputs"
    if status == PROTECTED_RUNTIME_PLAN_EXPIRED:
        return "refresh_runtime_plan_and_window"
    if status == PROTECTED_RUNTIME_PLAN_REVOKED:
        return "restore_runtime_plan_authority_before_restart"
    if status == PROTECTED_RUNTIME_PLAN_BLOCKED:
        return "clear_unsafe_plan_runtime_flags"
    return "collect_missing_protected_runtime_plan_blockers"


def _dedupe(blockers: Sequence[str]) -> list[str]:
    return list(dict.fromkeys(blockers))


def evaluate_protected_broker_demo_runtime_plan(
    state: Mapping[str, Any] | None,
    optional_limits: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    _ = optional_limits
    s = _normalize_inputs(state)
    blockers: list[str] = []

    approval_status = s.get("approval_workflow_status")
    connector_gate_status = s.get("protected_connector_gate_status")
    review_status = s.get("broker_demo_runtime_review_status")
    runtime_connector_status = s.get("runtime_connector_status")
    connector_contract_status = s.get("connector_contract_status")
    review_chain_status = s.get("review_chain_status")
    certificate_status = s.get("certificate_status")
    one_shot_status = s.get("one_shot_status")

    if approval_status is None:
        _append(blockers, "missing_approval_workflow")
    elif approval_status == APPROVAL_WORKFLOW_REJECTED:
        _append(blockers, "rejected_approval_workflow")
    elif approval_status != APPROVAL_WORKFLOW_REVIEW_READY:
        _append(blockers, "approval_workflow_not_ready")

    if connector_gate_status is None:
        _append(blockers, "missing_protected_connector_gate")
    elif connector_gate_status == PROTECTED_CONNECTOR_GATE_REJECTED:
        _append(blockers, "rejected_protected_connector_gate")
    elif connector_gate_status != PROTECTED_CONNECTOR_GATE_REVIEW_READY:
        _append(blockers, "protected_connector_gate_not_ready")

    if review_status is None:
        _append(blockers, "missing_broker_demo_runtime_review")
    elif review_status == BROKER_DEMO_RUNTIME_REVIEW_REJECTED:
        _append(blockers, "rejected_broker_demo_runtime_review")
    elif review_status != BROKER_DEMO_RUNTIME_REVIEW_READY:
        _append(blockers, "broker_demo_runtime_review_not_ready")

    if runtime_connector_status is None:
        _append(blockers, "missing_runtime_connector")
    elif runtime_connector_status == RUNTIME_CONNECTOR_REJECTED:
        _append(blockers, "rejected_runtime_connector")
    elif runtime_connector_status != RUNTIME_CONNECTOR_REVIEW_READY:
        _append(blockers, "runtime_connector_not_ready")

    if connector_contract_status is None:
        _append(blockers, "missing_connector_contract")
    elif connector_contract_status == CONNECTOR_CONTRACT_REJECTED:
        _append(blockers, "rejected_connector_contract")
    elif connector_contract_status != CONNECTOR_CONTRACT_REVIEW_READY:
        _append(blockers, "connector_contract_not_ready")

    if review_chain_status is None:
        _append(blockers, "missing_review_chain")
    elif review_chain_status == REVIEW_CHAIN_REJECTED:
        _append(blockers, "rejected_review_chain")
    elif review_chain_status != REVIEW_CHAIN_REVIEW_READY:
        _append(blockers, "review_chain_not_ready")

    if certificate_status is None:
        _append(blockers, "missing_certificate")
    elif certificate_status == LIVE_REVIEW_CERTIFICATE_REJECTED:
        _append(blockers, "rejected_certificate")
    elif certificate_status != LIVE_REVIEW_CERTIFICATE_REVIEW_READY:
        _append(blockers, "certificate_not_ready")

    if one_shot_status is None:
        _append(blockers, "missing_one_shot_package")
    elif one_shot_status == ONE_SHOT_EXCEPTION_REJECTED:
        _append(blockers, "rejected_one_shot_package")
    elif one_shot_status != ONE_SHOT_EXCEPTION_REVIEW_READY:
        _append(blockers, "one_shot_package_not_ready")

    _required_input_blockers(s, blockers)
    _required_control_blockers(s, blockers)

    for flag in (
        "operator_review_required",
        "manual_arming_required",
        "timeout_required",
        "no_retry_loop",
        "no_autonomous_reentry",
    ):
        if not _to_bool(_read_first(s, (flag,), default=True), default=True):
            if flag == "no_retry_loop":
                _append(blockers, "retry_loop_detected")
            elif flag == "no_autonomous_reentry":
                _append(blockers, "autonomous_reentry_detected")
            elif flag == "operator_review_required":
                _append(blockers, "missing_operator_review_requirement")
            elif flag == "manual_arming_required":
                _append(blockers, "missing_manual_arming_requirement")
            elif flag == "timeout_required":
                _append(blockers, "missing_timeout_requirement")

    if not _to_bool(_read_first(s, ("one_shot_controls",), default={}), default=False):
        _append(blockers, "missing_one_shot_controls")

    unsafe_map = {
        "broker_connection_detected": _to_bool(_read_first(s, ("broker_connection_detected",), default=False), default=False),
        "network_access_detected": _to_bool(_read_first(s, ("network_access_detected",), default=False), default=False),
        "credential_access_detected": _to_bool(_read_first(s, ("credential_access_detected",), default=False), default=False),
        "account_identifier_access_detected": _to_bool(_read_first(s, ("account_identifier_access_detected",), default=False), default=False),
        "order_execution_detected": _to_bool(_read_first(s, ("order_execution_detected",), default=False), default=False),
        "live_trading_authorization_detected": _to_bool(_read_first(s, ("live_trading_authorization_detected",), default=False), default=False),
        "execution_authority_detected": _to_bool(_read_first(s, ("execution_authority_detected",), default=False), default=False),
        "capital_allocation_detected": _to_bool(_read_first(s, ("capital_allocation_detected",), default=False), default=False),
    }
    for key, active in unsafe_map.items():
        if active:
            _append(blockers, key)

    # Expiry/revocation checks can be represented in two ways.
    runtime_plan_expired = _to_bool(_read_first(s, ("runtime_plan_expired",), default=False), default=False)
    runtime_plan_revoked = _to_bool(_read_first(s, ("runtime_plan_revoked",), default=False), default=False)
    approval_window_active = _to_bool(_read_first(s, ("approval_window_active",), default=True), default=True)
    runtime_plan_freshness = _to_bool(_read_first(s, ("runtime_plan_freshness",), default=True), default=True)
    if not approval_window_active and runtime_plan_freshness:
        _append(blockers, "approval_window_inactive")
    if not runtime_plan_freshness:
        _append(blockers, "runtime_plan_expired")
    if runtime_plan_expired:
        _append(blockers, "runtime_plan_expired")
    if runtime_plan_revoked:
        _append(blockers, "runtime_plan_revoked")

    blockers = _dedupe(blockers)
    blockers = [b for b in REQUIRED_BLOCKERS_ORDER if b in blockers] + [b for b in blockers if b not in REQUIRED_BLOCKERS_ORDER]

    if runtime_plan_revoked:
        status = PROTECTED_RUNTIME_PLAN_REVOKED
    elif not approval_window_active or runtime_plan_expired or not runtime_plan_freshness:
        status = PROTECTED_RUNTIME_PLAN_EXPIRED
    elif any(
        b.startswith("rejected_")
        for b in blockers
    ):
        status = PROTECTED_RUNTIME_PLAN_REJECTED
    elif any(flag in blockers for flag in (
        "broker_connection_detected",
        "network_access_detected",
        "credential_access_detected",
        "account_identifier_access_detected",
        "order_execution_detected",
        "live_trading_authorization_detected",
        "execution_authority_detected",
        "capital_allocation_detected",
        "retry_loop_detected",
        "autonomous_reentry_detected",
    )):
        status = PROTECTED_RUNTIME_PLAN_BLOCKED
    elif blockers:
        status = PROTECTED_RUNTIME_PLAN_INCOMPLETE
    elif (
        approval_status == APPROVAL_WORKFLOW_REVIEW_READY
        and connector_gate_status == PROTECTED_CONNECTOR_GATE_REVIEW_READY
        and review_status == BROKER_DEMO_RUNTIME_REVIEW_READY
        and runtime_connector_status == RUNTIME_CONNECTOR_REVIEW_READY
        and connector_contract_status == CONNECTOR_CONTRACT_REVIEW_READY
        and review_chain_status == REVIEW_CHAIN_REVIEW_READY
        and certificate_status == LIVE_REVIEW_CERTIFICATE_REVIEW_READY
        and one_shot_status == ONE_SHOT_EXCEPTION_REVIEW_READY
    ):
        status = PROTECTED_RUNTIME_PLAN_REVIEW_READY
    else:
        status = PROTECTED_RUNTIME_PLAN_INCOMPLETE

    completed = status in {
        PROTECTED_RUNTIME_PLAN_REVIEW_READY,
        PROTECTED_RUNTIME_PLAN_INCOMPLETE,
        PROTECTED_RUNTIME_PLAN_BLOCKED,
        PROTECTED_RUNTIME_PLAN_REJECTED,
        PROTECTED_RUNTIME_PLAN_REVOKED,
        PROTECTED_RUNTIME_PLAN_EXPIRED,
    }

    review_required = status != PROTECTED_RUNTIME_PLAN_REVIEW_READY
    blocked = status == PROTECTED_RUNTIME_PLAN_BLOCKED

    summary = {
        "approval_workflow_status": approval_status,
        "protected_connector_gate_status": connector_gate_status,
        "broker_demo_runtime_review_status": review_status,
        "runtime_connector_status": runtime_connector_status,
        "connector_contract_status": connector_contract_status,
        "review_chain_status": review_chain_status,
        "certificate_status": certificate_status,
        "one_shot_status": one_shot_status,
        "runtime_plan_freshness": runtime_plan_freshness,
        "approval_window_active": approval_window_active,
        "runtime_plan_expired": runtime_plan_expired,
        "runtime_plan_revoked": runtime_plan_revoked,
        "blocker_count": len(blockers),
    }

    contract = {
        "contract_version": "PROTECTED_BROKER_DEMO_RUNTIME_PLAN_V1",
        "approval_workflow_required": True,
        "protected_connector_gate_required": True,
        "broker_demo_runtime_review_required": True,
        "runtime_connector_required": True,
        "connector_contract_required": True,
        "review_chain_required": True,
        "certificate_required": True,
        "one_shot_package_required": True,
        "runtime_plan_request_required": True,
        "runtime_plan_trace_required": True,
        "runtime_plan_evidence_required": True,
        "runtime_plan_scope_required": True,
        "runtime_plan_owner_required": True,
        "runtime_plan_expiration_required": True,
        "runtime_plan_freshness_required": True,
        "runtime_plan_revocation_required": True,
        "runtime_plan_audit_required": True,
        "runtime_plan_connector_scope_required": True,
        "runtime_plan_handoff_boundary_required": True,
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

    safety = {
        "broker_connection_active": False,
        "network_access": False,
        "credentials_accessed": False,
        "account_identifiers_accessed": False,
        "order_execution_enabled": False,
        "live_trading_authorized": False,
        "execution_authority_granted": False,
        "capital_allocated": False,
        "protected_runtime_plan_only": True,
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

    warnings = []
    if _read_first(s, ("approval_window_inactive",), default=False):
        warnings.append("approval_window_inactive")
    if _read_first(s, ("missing_runtime_plan_evidence_bundle",), default=False):
        warnings.append("runtime_plan_evidence_bundle_incomplete")

    return {
        "runtime_plan_completed": completed,
        "runtime_plan_status": status,
        "runtime_plan_review_ready": status == PROTECTED_RUNTIME_PLAN_REVIEW_READY,
        "runtime_plan_blocked": blocked,
        "runtime_plan_review_required": review_required,
        "runtime_plan_summary": summary,
        "runtime_plan_blockers": blockers,
        "runtime_plan_warnings": warnings,
        "runtime_plan_next_safe_action": _next_safe_action(status),
        "runtime_plan_required_next_packets": _required_next_packets(status),
        "runtime_plan_contract": contract,
        "safety": safety,
    }
