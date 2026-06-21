from __future__ import annotations

from typing import Any, Iterable, Mapping

LIVE_REVIEW_CERTIFICATE_BLOCKED = "LIVE_REVIEW_CERTIFICATE_BLOCKED"
LIVE_REVIEW_CERTIFICATE_INCOMPLETE = "LIVE_REVIEW_CERTIFICATE_INCOMPLETE"
LIVE_REVIEW_CERTIFICATE_REVIEW_READY = "LIVE_REVIEW_CERTIFICATE_REVIEW_READY"
LIVE_REVIEW_CERTIFICATE_REJECTED = "LIVE_REVIEW_CERTIFICATE_REJECTED"

DEMO_CONTRACT_COMPLETE = "DEMO_CONTRACT_COMPLETE"
DEMO_CONTRACT_REJECTED = "DEMO_CONTRACT_REJECTED"
ONE_SHOT_EXCEPTION_REVIEW_READY = "ONE_SHOT_EXCEPTION_REVIEW_READY"
ONE_SHOT_EXCEPTION_REJECTED = "ONE_SHOT_EXCEPTION_REJECTED"


def _get(mapping: Mapping[str, Any], aliases: Iterable[str], default: Any = None) -> Any:
    for key in aliases:
        if key in mapping:
            return mapping[key]
    return default


def _as_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "on", "active", "ok", "pass", "passed"}:
        return True
    if text in {"0", "false", "no", "off", "inactive", "fail", "failed"}:
        return False
    return bool(value)


def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _mapping(value: Any) -> Mapping[str, Any] | None:
    return value if isinstance(value, Mapping) else None


def _append(blockers: list[str], item: str) -> None:
    if item not in blockers:
        blockers.append(item)


def _proof_present(state: Mapping[str, Any], aliases: Iterable[str]) -> bool:
    proof = _mapping(_get(state, aliases))
    if not isinstance(proof, Mapping):
        return False
    return _as_bool(_get(proof, ("present", "verified", "available"), default=False), default=False)


def _next_action(status: str) -> str:
    return {
        LIVE_REVIEW_CERTIFICATE_REVIEW_READY: "submit_for_human_live_review",
        LIVE_REVIEW_CERTIFICATE_REJECTED: "remediate_rejected_state",
        LIVE_REVIEW_CERTIFICATE_BLOCKED: "resolve_unsafe_or_authorization_blockers",
        LIVE_REVIEW_CERTIFICATE_INCOMPLETE: "collect_and_refresh_missing_evidence",
    }[status]


def _required_next_packets(status: str) -> list[str]:
    if status == LIVE_REVIEW_CERTIFICATE_REVIEW_READY:
        return ["prepare_live_review_bundle", "request_human_live_review", "final_readiness_acknowledgment"]
    if status == LIVE_REVIEW_CERTIFICATE_REJECTED:
        return ["repair_demo_validation_gate", "rework_evidence", "reset_rejected_state"]
    if status == LIVE_REVIEW_CERTIFICATE_BLOCKED:
        return ["clear_unsafe_runtime_flags", "restore_safety_invariants", "resolve_control_gaps"]
    return ["collect_missing_evidence", "refresh_risk_controls", "repair_live_readiness_inputs"]


def generate_live_review_readiness_certificate(
    state: Mapping[str, Any] | None = None,
    optional_limits: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    state = state or {}
    optional_limits = optional_limits or {}

    max_evidence_age = _as_float(
        _get(optional_limits, ("maximum_evidence_age_minutes",), default=60.0),
        default=60.0,
    )

    blockers: list[str] = []
    warnings: list[str] = []

    demo_contract = _mapping(_get(state, ("demo_validation_contract", "demo_contract")))
    if demo_contract is None:
        demo_status = ""
        demo_completed = False
        demo_readiness = False
        demo_blockers: list[str] = ["missing_demo_validation_contract"]
    else:
        demo_status = _get(
            demo_contract,
            ("demo_validation_contract_status", "demo_contract_status"),
            default="",
        )
        demo_completed = _as_bool(
            _get(
                demo_contract,
                ("demo_validation_contract_completed", "demo_contract_completed"),
                default=False,
            ),
            default=False,
        )
        demo_readiness = _as_bool(_get(demo_contract, ("live_readiness_candidate", "candidate_ready"), default=False), default=False)
        demo_blockers = []
        if demo_status == DEMO_CONTRACT_REJECTED:
            demo_blockers.append("demo_or_profitability_rejected")
        if demo_status != DEMO_CONTRACT_COMPLETE:
            demo_blockers.append("demo_validation_contract_not_complete")

    one_shot = _mapping(_get(state, ("one_shot_exception_package", "exception_package")))
    if one_shot is None:
        one_shot_status = ""
        one_shot_completed = False
        one_shot_readiness = False
        one_shot_blockers = ["missing_one_shot_exception_package"]
    else:
        one_shot_status = _get(
            one_shot,
            ("exception_package_status", "one_shot_status"),
            default="",
        )
        one_shot_completed = _as_bool(
            _get(one_shot, ("exception_package_completed", "package_completed"), default=False),
            default=False,
        )
        one_shot_readiness = _as_bool(
            _get(one_shot, ("live_micro_trade_review_ready", "review_ready"), default=False),
            default=False,
        )
        one_shot_blockers = []
        if one_shot_status == ONE_SHOT_EXCEPTION_REJECTED:
            one_shot_blockers.append("demo_or_profitability_rejected")
            one_shot_blockers.append("one_shot_exception_package_not_review_ready")
        elif one_shot_status != ONE_SHOT_EXCEPTION_REVIEW_READY or not one_shot_completed or not one_shot_readiness:
            one_shot_blockers.append("one_shot_exception_package_not_review_ready")

    for b in demo_blockers + one_shot_blockers:
        _append(blockers, b)

    live_readiness_candidate = _as_bool(_get(state, ("live_readiness_candidate", "candidate_ready"), default=False), default=False)
    if not live_readiness_candidate:
        _append(blockers, "missing_live_readiness_candidate")

    approval = _mapping(_get(state, ("approval_trace", "approval")))
    if approval is None:
        _append(blockers, "missing_approval_trace")
    else:
        approval_active = _as_bool(_get(approval, ("approval_window_active",), default=False), default=False)
        approval_status = str(_get(approval, ("approval_window_status",), default="")).upper()
        if not (approval_active or approval_status == "ACTIVE"):
            _append(blockers, "missing_approval_trace")

    risk = _mapping(_get(state, ("risk_limits", "risk")))
    if risk is None:
        _append(blockers, "missing_risk_limits")
    else:
        if _as_float(_get(risk, ("maximum_loss",), default=None), default=-1.0) < 0:
            _append(blockers, "missing_risk_limits")
        if _as_float(_get(risk, ("daily_loss_cap",), default=None), default=-1.0) < 0:
            _append(blockers, "missing_risk_limits")
        if _as_float(_get(risk, ("stop_loss",), default=None), default=-1.0) < 0:
            _append(blockers, "missing_risk_limits")
        if not _get(risk, ("order_type",), default=None):
            _append(blockers, "missing_risk_limits")
        if _as_float(_get(risk, ("units_or_notional_limit",), default=None), default=-1.0) < 0:
            _append(blockers, "missing_risk_limits")

    if not _proof_present(state, ("kill_switch_proof", "kill_switch")):
        _append(blockers, "missing_kill_switch_proof")
    if not _proof_present(state, ("rollback_proof", "rollback")):
        _append(blockers, "missing_rollback_proof")
    if not _proof_present(state, ("reconciliation_proof", "reconciliation")):
        _append(blockers, "missing_reconciliation_proof")

    evidence = _mapping(_get(state, ("evidence_freshness", "evidence_fresh")))
    if evidence is None:
        evidence_fresh = False
        _append(blockers, "missing_evidence_freshness")
    else:
        fresh_flag = _as_bool(_get(evidence, ("fresh", "evidence_fresh", "is_fresh"), default=False), default=False)
        if fresh_flag:
            evidence_fresh = True
        else:
            evidence_age = _as_float(_get(evidence, ("evidence_age_minutes", "age_minutes"), default=float("inf")), default=float("inf"))
            evidence_fresh = evidence_age <= max_evidence_age
            if not evidence_fresh:
                _append(blockers, "missing_evidence_freshness")

    if not _proof_present(state, ("replayability_proof", "replay")):
        _append(blockers, "missing_replayability_proof")
    if not _proof_present(state, ("final_disarm_proof", "final_disarm")):
        _append(blockers, "missing_final_disarm_proof")

    if not _get(state, ("post_trade_journal_path", "journal_path"), default=""):
        _append(blockers, "missing_post_trade_journal_path")

    operator_review_required = _as_bool(_get(state, ("operator_review_required",), default=True), default=False)
    if not operator_review_required:
        _append(blockers, "missing_operator_review_requirement")

    if not demo_readiness:
        _append(blockers, "stale_or_incomplete_evidence")
    if not one_shot_readiness:
        _append(blockers, "stale_or_incomplete_evidence")
    if not evidence_fresh:
        _append(blockers, "stale_or_incomplete_evidence")

    unsafe_map = {
        "live_trading_authorization_detected": _as_bool(
            _get(state, ("unsafe_live_trading_detected", "live_trading_authorization_detected", "live_trading_authorized"), default=False),
            default=False,
        ),
        "order_execution_enabled_detected": _as_bool(
            _get(state, ("unsafe_order_execution_detected", "order_execution_enabled_detected", "order_execution_enabled"), default=False),
            default=False,
        ),
        "broker_connection_detected": _as_bool(
            _get(state, ("unsafe_broker_connection_detected", "broker_connection_detected", "broker_connection_active"), default=False),
            default=False,
        ),
        "network_access_detected": _as_bool(
            _get(state, ("unsafe_network_access_detected", "network_access_detected", "network_access"), default=False),
            default=False,
        ),
        "credential_access_detected": _as_bool(
            _get(state, ("unsafe_credential_access_detected", "credential_access_detected", "credentials_accessed"), default=False),
            default=False,
        ),
        "account_identifier_access_detected": _as_bool(
            _get(state, ("unsafe_account_identifier_access_detected", "account_identifier_access_detected", "account_identifiers_accessed"), default=False),
            default=False,
        ),
        "capital_allocation_detected": _as_bool(
            _get(state, ("unsafe_capital_allocation_detected", "capital_allocation_detected"), default=False),
            default=False,
        ),
    }
    for key, active in unsafe_map.items():
        if active:
            _append(blockers, key)

    incomplete_blockers = {
        "demo_validation_contract_not_complete",
        "one_shot_exception_package_not_review_ready",
        "missing_live_readiness_candidate",
        "missing_approval_trace",
        "missing_risk_limits",
        "missing_kill_switch_proof",
        "missing_rollback_proof",
        "missing_reconciliation_proof",
        "missing_evidence_freshness",
        "missing_replayability_proof",
        "missing_final_disarm_proof",
        "missing_post_trade_journal_path",
        "missing_operator_review_requirement",
        "stale_or_incomplete_evidence",
    }
    unsafe_blockers = {
        "live_trading_authorization_detected",
        "order_execution_enabled_detected",
        "broker_connection_detected",
        "network_access_detected",
        "credential_access_detected",
        "account_identifier_access_detected",
        "capital_allocation_detected",
    }

    if any(unsafe_map.values()):
        status = LIVE_REVIEW_CERTIFICATE_BLOCKED
    elif "missing_demo_validation_contract" in blockers:
        status = LIVE_REVIEW_CERTIFICATE_BLOCKED
    elif "demo_or_profitability_rejected" in blockers:
        status = LIVE_REVIEW_CERTIFICATE_REJECTED
    elif not demo_blockers and not one_shot_blockers and not any(b in blockers for b in incomplete_blockers) and not any(
        b in blockers for b in unsafe_blockers
    ):
        status = LIVE_REVIEW_CERTIFICATE_REVIEW_READY
    else:
        status = LIVE_REVIEW_CERTIFICATE_INCOMPLETE

    certificate_ready = status == LIVE_REVIEW_CERTIFICATE_REVIEW_READY
    certificate_completed = status in {
        LIVE_REVIEW_CERTIFICATE_REVIEW_READY,
        LIVE_REVIEW_CERTIFICATE_REJECTED,
        LIVE_REVIEW_CERTIFICATE_BLOCKED,
    }

    controls = _mapping(_get(state, ("one_shot_controls",), default={})) or {}
    one_shot_only = _as_bool(_get(controls, ("one_shot_only",), default=True), default=True)
    no_retry_loop = _as_bool(_get(controls, ("no_retry_loop",), default=True), default=True)
    no_autonomous_reentry = _as_bool(_get(controls, ("no_autonomous_reentry",), default=True), default=True)
    manual_arming_required = _as_bool(_get(controls, ("manual_arming_required",), default=True), default=True)
    final_disarm_required = _as_bool(_get(controls, ("final_disarm_required",), default=True), default=True)
    if isinstance(one_shot, Mapping):
        one_shot_safety = _mapping(_get(one_shot, ("safety",), default={})) or {}
        no_retry_loop = _as_bool(_get(one_shot_safety, ("no_retry_loop",), default=no_retry_loop), default=no_retry_loop)
        no_autonomous_reentry = _as_bool(_get(one_shot_safety, ("no_autonomous_reentry",), default=no_autonomous_reentry), default=no_autonomous_reentry)
        manual_arming_required = _as_bool(_get(one_shot_safety, ("manual_arming_required",), default=manual_arming_required), default=manual_arming_required)
        final_disarm_required = _as_bool(_get(one_shot_safety, ("final_disarm_required",), default=final_disarm_required), default=final_disarm_required)

    safety = {
        "broker_connection_active": bool(unsafe_map["broker_connection_detected"]),
        "network_access": bool(unsafe_map["network_access_detected"]),
        "credentials_accessed": bool(unsafe_map["credential_access_detected"]),
        "account_identifiers_accessed": bool(unsafe_map["account_identifier_access_detected"]),
        "order_execution_enabled": bool(unsafe_map["order_execution_enabled_detected"]),
        "live_trading_authorized": False,
        "capital_allocated": bool(_as_bool(_get(state, ("capital_allocated", "capital_allocation_modified"), default=False), default=False)
        or unsafe_map["capital_allocation_detected"]),
        "operator_review_required": True,
        "review_certificate_only": True,
        "execution_authority_granted": False,
        "one_shot_only": bool(one_shot_only),
        "no_retry_loop": bool(no_retry_loop),
        "no_autonomous_reentry": bool(no_autonomous_reentry),
        "manual_arming_required": bool(manual_arming_required),
        "final_disarm_required": bool(final_disarm_required),
    }

    source_summary = {
        "demo_alias_used": "demo_validation_contract" if "demo_validation_contract" in state else ("demo_contract" if "demo_contract" in state else None),
        "one_shot_alias_used": "one_shot_exception_package" if "one_shot_exception_package" in state else ("exception_package" if "exception_package" in state else None),
    }

    return {
        "certificate_completed": certificate_completed,
        "certificate_status": status,
        "human_live_review_ready": certificate_ready,
        "live_micro_trade_review_ready": certificate_ready,
        "live_trading_authorized": False,
        "blockers": blockers,
        "warnings": warnings,
        "next_safe_action": _next_action(status),
        "required_next_packets": _required_next_packets(status),
        "certificate_summary": {
            "status": status,
            "ready": certificate_ready,
            "demo_contract_complete": demo_status == DEMO_CONTRACT_COMPLETE if demo_contract is not None else False,
            "one_shot_review_ready": one_shot_status == ONE_SHOT_EXCEPTION_REVIEW_READY if one_shot is not None else False,
        },
        "readiness_summary": {
            "demo_complete": demo_status == DEMO_CONTRACT_COMPLETE if demo_contract is not None else False,
            "one_shot_review_ready": one_shot_readiness,
            "evidence_fresh": evidence_fresh,
            "approval_present": approval is not None,
            "risk_limits_present": risk is not None,
        },
        "source_summary": source_summary,
        "safety": safety,
    }
