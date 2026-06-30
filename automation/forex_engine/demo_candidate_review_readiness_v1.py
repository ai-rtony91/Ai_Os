"""Read-only Forex demo candidate review readiness evaluator."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from math import isfinite
from typing import Any


SCHEMA = "AIOS_FOREX_DEMO_CANDIDATE_REVIEW_READINESS_V1"
MODE = "READ_ONLY_DEMO_CANDIDATE_REVIEW_READINESS"

DEMO_REVIEW_READY = "DEMO_REVIEW_READY"
NEEDS_MORE_EVIDENCE = "NEEDS_MORE_EVIDENCE"
BLOCKED_BY_EVIDENCE_SUFFICIENCY = "BLOCKED_BY_EVIDENCE_SUFFICIENCY"
BLOCKED_BY_CANDIDATE_QUALITY = "BLOCKED_BY_CANDIDATE_QUALITY"
BLOCKED_BY_RISK_CONTROLS = "BLOCKED_BY_RISK_CONTROLS"
BLOCKED_BY_OBSERVABILITY = "BLOCKED_BY_OBSERVABILITY"
BLOCKED_BY_OWNER_GATE = "BLOCKED_BY_OWNER_GATE"
BLOCKED_BY_BROKER_BOUNDARY = "BLOCKED_BY_BROKER_BOUNDARY"
BLOCKED_BY_DATA_QUALITY = "BLOCKED_BY_DATA_QUALITY"
INCOMPLETE_INPUTS = "INCOMPLETE_INPUTS"

THIS_PACKET = SCHEMA
NEXT_PACKET_IF_READY = "AIOS_FOREX_SUPERVISED_DEMO_READINESS_PACKET_V1"
CURRENT_LANE_ID = "DEMO_CANDIDATE_REVIEW_READINESS"
NEXT_LANE_ID = "SUPERVISED_DEMO_READINESS"

OPPORTUNITY_CAPTURE_OBJECTIVE = (
    "maximize validated risk-adjusted opportunity capture while preserving capital and proving edge"
)

DEFAULT_THRESHOLDS: dict[str, float] = {
    "min_readiness_score": 0.80,
    "min_evidence_sufficiency_score": 0.75,
    "min_candidate_quality_score": 0.75,
    "min_risk_control_score": 0.80,
    "min_observability_score": 0.75,
    "min_data_quality_score": 0.80,
}

THRESHOLD_FLOORS: dict[str, float] = {
    "min_readiness_score": 0.70,
    "min_evidence_sufficiency_score": 0.70,
    "min_candidate_quality_score": 0.70,
    "min_risk_control_score": 0.75,
    "min_observability_score": 0.70,
    "min_data_quality_score": 0.75,
}

SENSITIVE_KEY_PARTS = (
    "routing_number",
    "account_number",
    "debit_card_number",
    "card_number",
    "cvv",
    "password",
    "api_key",
    "token",
    "secret",
    "credential",
    "credentials",
    "broker_token",
    "access_token",
)

CORE_EVIDENCE_KEYS = (
    "evidence_sufficiency",
    "profit_candidate_quality",
    "risk_controls",
    "observability",
    "owner_gate",
    "broker_boundary",
)

BROKER_BOUNDARY_FLAGS = (
    "broker_api_allowed",
    "trade_execution_allowed",
    "credential_use_allowed",
    "demo_execution_allowed",
    "money_movement_allowed",
    "bank_access_allowed",
)

SAFE_BOUNDARY_KEYS = frozenset(BROKER_BOUNDARY_FLAGS)


def evaluate_demo_candidate_review_readiness_v1(
    payload: dict | None = None,
) -> dict[str, Any]:
    """Evaluate sanitized demo-candidate readiness evidence without execution authority."""

    source = payload if isinstance(payload, Mapping) else {}
    threshold_policy = _threshold_policy(_mapping(source.get("thresholds")))
    thresholds = threshold_policy["active_thresholds"]

    if _contains_sensitive_key(source):
        return _sensitive_payload(source, threshold_policy)

    missing_information = _missing_information(source)
    missing_core_evidence = bool(missing_information)

    evidence_summary = _evidence_sufficiency_summary(source, thresholds)
    quality_summary = _quality_improvement_summary(source, thresholds)
    risk_summary = _risk_control_summary(source, thresholds)
    observability_summary = _observability_summary(source, thresholds)
    owner_gate_summary = _owner_gate_summary(source)
    broker_boundary_summary = _broker_boundary_summary(source)
    data_quality_summary = _data_quality_summary(source, thresholds)

    sub_scores = {
        "evidence_sufficiency_score": evidence_summary["score"],
        "candidate_quality_score": quality_summary["score"],
        "risk_control_score": risk_summary["score"],
        "observability_score": observability_summary["score"],
        "data_quality_score": data_quality_summary["score"],
    }
    explicit_readiness_score = _score_from_contexts(
        _contexts(source, "readiness_snapshot"),
        ("readiness_score",),
    )
    derived_readiness_score = _average_score(sub_scores.values())
    readiness_score = explicit_readiness_score if explicit_readiness_score is not None else derived_readiness_score

    readiness_blockers = _unique(
        [
            *threshold_policy["threshold_blockers"],
            *missing_information,
            *evidence_summary["blockers"],
            *quality_summary["blockers"],
            *risk_summary["blockers"],
            *observability_summary["blockers"],
            *owner_gate_summary["blockers"],
            *broker_boundary_summary["blockers"],
            *data_quality_summary["blockers"],
        ]
    )

    readiness_status = _resolve_readiness_status(
        missing_core_evidence=missing_core_evidence,
        evidence_summary=evidence_summary,
        quality_summary=quality_summary,
        risk_summary=risk_summary,
        observability_summary=observability_summary,
        owner_gate_summary=owner_gate_summary,
        broker_boundary_summary=broker_boundary_summary,
        data_quality_summary=data_quality_summary,
        readiness_score=readiness_score,
        min_readiness_score=thresholds["min_readiness_score"],
    )
    next_best_packet = NEXT_PACKET_IF_READY if readiness_status == DEMO_REVIEW_READY else THIS_PACKET

    return _base_result(
        source=source,
        threshold_policy=threshold_policy,
        readiness_status=readiness_status,
        readiness_score=readiness_score,
        explicit_readiness_score=explicit_readiness_score,
        derived_readiness_score=derived_readiness_score,
        sub_scores=sub_scores,
        evidence_summary=evidence_summary,
        quality_summary=quality_summary,
        risk_summary=risk_summary,
        observability_summary=observability_summary,
        owner_gate_summary=owner_gate_summary,
        broker_boundary_summary=broker_boundary_summary,
        data_quality_summary=data_quality_summary,
        missing_information=missing_information,
        readiness_blockers=readiness_blockers,
        next_best_packet=next_best_packet,
    )


def _sensitive_payload(source: Mapping[str, Any], threshold_policy: Mapping[str, Any]) -> dict[str, Any]:
    blockers = ["sensitive_data_provided"]
    summary = _empty_summary("blocked_by_sensitive_data", blockers)
    next_best_packet = THIS_PACKET
    result = _base_result(
        source=source,
        threshold_policy=threshold_policy,
        readiness_status=BLOCKED_BY_DATA_QUALITY,
        readiness_score=None,
        explicit_readiness_score=None,
        derived_readiness_score=None,
        sub_scores={
            "evidence_sufficiency_score": None,
            "candidate_quality_score": None,
            "risk_control_score": None,
            "observability_score": None,
            "data_quality_score": None,
        },
        evidence_summary=summary,
        quality_summary=summary,
        risk_summary=summary,
        observability_summary=summary,
        owner_gate_summary={
            "ready": False,
            "owner_gate_required": True,
            "owner_approval_required": True,
            "owner_review_ready": False,
            "execution_allowed": False,
            "manual_execution_only": True,
            "blockers": blockers,
        },
        broker_boundary_summary={
            "ready": False,
            "input_flags": {flag: None for flag in BROKER_BOUNDARY_FLAGS},
            "boundary_preserved": True,
            "blockers": blockers,
        },
        data_quality_summary=summary,
        missing_information=["remove_sensitive_data"],
        readiness_blockers=blockers,
        next_best_packet=next_best_packet,
    )
    result["input_summary"]["input_redacted"] = True
    result["audit_record"]["input_redacted"] = True
    result["safe_manual_next_action"] = (
        "Remove sensitive data and rerun the read-only readiness evaluator with sanitized "
        "demo-candidate evidence only."
    )
    return result


def _base_result(
    *,
    source: Mapping[str, Any],
    threshold_policy: Mapping[str, Any],
    readiness_status: str,
    readiness_score: float | None,
    explicit_readiness_score: float | None,
    derived_readiness_score: float | None,
    sub_scores: Mapping[str, float | None],
    evidence_summary: Mapping[str, Any],
    quality_summary: Mapping[str, Any],
    risk_summary: Mapping[str, Any],
    observability_summary: Mapping[str, Any],
    owner_gate_summary: Mapping[str, Any],
    broker_boundary_summary: Mapping[str, Any],
    data_quality_summary: Mapping[str, Any],
    missing_information: Sequence[str],
    readiness_blockers: Sequence[str],
    next_best_packet: str,
) -> dict[str, Any]:
    demo_review_ready = readiness_status == DEMO_REVIEW_READY
    return {
        "schema": SCHEMA,
        "mode": MODE,
        "read_only": True,
        "money_movement_allowed": False,
        "bank_access_allowed": False,
        "broker_api_allowed": False,
        "trade_execution_allowed": False,
        "demo_execution_allowed": False,
        "credential_use_allowed": False,
        "scheduler_created": False,
        "daemon_created": False,
        "webhook_created": False,
        "dashboard_runtime_created": False,
        "owner_decision_required": True,
        "readiness_status": readiness_status,
        "demo_review_ready": demo_review_ready,
        "supervised_demo_execution_authorized": False,
        "opportunity_capture_objective": OPPORTUNITY_CAPTURE_OBJECTIVE,
        "input_summary": _input_summary(
            source=source,
            explicit_readiness_score=explicit_readiness_score,
            derived_readiness_score=derived_readiness_score,
            sub_scores=sub_scores,
            missing_information=missing_information,
        ),
        "threshold_policy": dict(threshold_policy),
        "evidence_sufficiency_summary": dict(evidence_summary),
        "quality_improvement_summary": dict(quality_summary),
        "risk_control_summary": dict(risk_summary),
        "observability_summary": dict(observability_summary),
        "owner_gate_summary": dict(owner_gate_summary),
        "broker_boundary_summary": dict(broker_boundary_summary),
        "data_quality_summary": dict(data_quality_summary),
        "readiness_score": readiness_score,
        "readiness_blockers": list(readiness_blockers),
        "missing_information": list(missing_information),
        "owner_action_queue": _owner_action_queue(
            evidence_summary=evidence_summary,
            quality_summary=quality_summary,
            risk_summary=risk_summary,
            observability_summary=observability_summary,
            owner_gate_summary=owner_gate_summary,
            broker_boundary_summary=broker_boundary_summary,
            data_quality_summary=data_quality_summary,
            next_best_packet=next_best_packet,
        ),
        "next_best_packet": next_best_packet,
        "next_remaining_lane": _next_remaining_lane(
            _mapping(source.get("remaining_work_closure_index")),
            next_best_packet,
        ),
        "safe_manual_next_action": _safe_manual_next_action(readiness_status),
        "audit_record": {
            "schema": SCHEMA,
            "mode": MODE,
            "as_of_date": _text(source.get("as_of_date"), datetime.now(timezone.utc).isoformat()),
            "owner_name": _text(source.get("owner_name"), "Anthony"),
            "input_fields_seen": sorted(str(key) for key in source.keys()),
            "readiness_status": readiness_status,
            "readiness_score": readiness_score,
            "demo_review_ready": demo_review_ready,
            "next_best_packet": next_best_packet,
            "read_only": True,
        },
        "safety": _safety(),
    }


def _threshold_policy(overrides: Mapping[str, Any]) -> dict[str, Any]:
    active = dict(DEFAULT_THRESHOLDS)
    rejected: list[dict[str, str]] = []
    for key, raw_value in overrides.items():
        if key not in DEFAULT_THRESHOLDS:
            continue
        value = _score(raw_value)
        if value is None or value < THRESHOLD_FLOORS[key]:
            rejected.append({"threshold": key, "reason": "threshold_override_rejected"})
            continue
        active[key] = value
    return {
        "default_thresholds": dict(DEFAULT_THRESHOLDS),
        "active_thresholds": active,
        "rejected_overrides": rejected,
        "threshold_blockers": ["threshold_override_rejected"] if rejected else [],
        "guardrails": dict(THRESHOLD_FLOORS),
    }


def _evidence_sufficiency_summary(source: Mapping[str, Any], thresholds: Mapping[str, float]) -> dict[str, Any]:
    contexts = _contexts(source, "evidence_sufficiency")
    score = _score_from_contexts(contexts, ("evidence_sufficiency_score",))
    flags = {
        "sufficient_for_next_profit_lane": _bool_from_contexts(contexts, ("sufficient_for_next_profit_lane",)),
        "sufficient_for_demo_candidate_review": _bool_from_contexts(
            contexts,
            ("sufficient_for_demo_candidate_review",),
        ),
        "sample_sufficient": _bool_from_contexts(contexts, ("sample_sufficient",)),
        "walk_forward_gate_cleared": _bool_from_contexts(contexts, ("walk_forward_gate_cleared",)),
        "oos_stable": _bool_from_contexts(contexts, ("oos_stable",)),
        "regime_coverage_sufficient": _bool_from_contexts(contexts, ("regime_coverage_sufficient",)),
    }
    derived_score = _bool_score(flags.values())
    active_score = score if score is not None else derived_score
    status = _text_from_contexts(contexts, ("evidence_status",))
    blockers: list[str] = []
    if active_score is None:
        blockers.append("evidence_sufficiency_score_missing")
    elif active_score < thresholds["min_evidence_sufficiency_score"]:
        blockers.append("evidence_sufficiency_score_below_threshold")
    for key, value in flags.items():
        if value is False:
            blockers.append(f"{key}_false")
    if status and status.upper() not in {
        "SUFFICIENT_FOR_DEMO_CANDIDATE_REVIEW",
        "SUFFICIENT_FOR_NEXT_PROFIT_LANE",
        "EVIDENCE_SUFFICIENT",
        "READY",
        "PASS",
    }:
        blockers.append("evidence_status_not_sufficient")
    ready_signal = status or any(value is True for value in flags.values())
    if not ready_signal:
        blockers.append("evidence_sufficiency_ready_signal_missing")
    return {
        "ready": not blockers,
        "evidence_status": status,
        "score": active_score,
        "explicit_score": score,
        "derived_score": derived_score,
        "threshold": thresholds["min_evidence_sufficiency_score"],
        "flags": flags,
        "blockers": _unique(blockers),
    }


def _quality_improvement_summary(source: Mapping[str, Any], thresholds: Mapping[str, float]) -> dict[str, Any]:
    contexts = _contexts(source, "profit_candidate_quality")
    score = _score_from_contexts(contexts, ("candidate_quality_score", "quality_score"))
    quality_status = _text_from_contexts(contexts, ("quality_status",))
    demo_review_ready = _bool_from_contexts(contexts, ("demo_review_ready",))
    can_queue = _bool_from_contexts(contexts, ("can_queue_demo_candidate_review_readiness",))
    improvement_blockers = _blockers_from_contexts(contexts, ("improvement_blockers", "blocker_summary"))
    blockers: list[str] = []
    if score is None:
        blockers.append("candidate_quality_score_missing")
    elif score < thresholds["min_candidate_quality_score"]:
        blockers.append("candidate_quality_score_below_threshold")
    if quality_status and quality_status.upper() not in {
        "QUALITY_IMPROVEMENT_READY",
        "DEMO_REVIEW_READY",
        "CANDIDATE_QUALITY_READY",
        "READY",
        "PASS",
    }:
        blockers.append("quality_status_not_ready")
    if demo_review_ready is False:
        blockers.append("demo_review_ready_false")
    if can_queue is False:
        blockers.append("can_queue_demo_candidate_review_readiness_false")
    if improvement_blockers:
        blockers.extend(improvement_blockers)
    if not quality_status and demo_review_ready is not True and can_queue is not True:
        blockers.append("candidate_quality_ready_signal_missing")
    return {
        "ready": not blockers,
        "quality_status": quality_status,
        "score": score,
        "threshold": thresholds["min_candidate_quality_score"],
        "demo_review_ready": demo_review_ready,
        "can_queue_demo_candidate_review_readiness": can_queue,
        "improvement_blockers": improvement_blockers,
        "blockers": _unique(blockers),
    }


def _risk_control_summary(source: Mapping[str, Any], thresholds: Mapping[str, float]) -> dict[str, Any]:
    contexts = _contexts(source, "risk_controls")
    score = _score_from_contexts(contexts, ("risk_control_score",))
    controls = {
        "daily_loss_stop_configured": _bool_from_contexts(contexts, ("daily_loss_stop_configured",)),
        "kill_switch_present": _bool_from_contexts(contexts, ("kill_switch_present",)),
        "max_loss_gate_present": _bool_from_contexts(contexts, ("max_loss_gate_present",)),
        "position_size_limit_present": _bool_from_contexts(contexts, ("position_size_limit_present",)),
    }
    active_score = score if score is not None else _bool_score(controls.values())
    max_drawdown_pct = _number_from_contexts(contexts, ("max_drawdown_pct", "max_drawdown_percent"))
    risk_blocks = _blockers_from_contexts(contexts, ("risk_blocks",))
    blockers: list[str] = []
    if active_score is None:
        blockers.append("risk_control_score_missing")
    elif active_score < thresholds["min_risk_control_score"]:
        blockers.append("risk_control_score_below_threshold")
    for key, value in controls.items():
        if value is None:
            blockers.append(f"{key}_missing")
        elif value is False:
            blockers.append(f"{key}_false")
    if max_drawdown_pct is not None and max_drawdown_pct > 10.0:
        blockers.append("max_drawdown_pct_above_review_limit")
    blockers.extend(risk_blocks)
    return {
        "ready": not blockers,
        "score": active_score,
        "explicit_score": score,
        "threshold": thresholds["min_risk_control_score"],
        "max_drawdown_pct": max_drawdown_pct,
        "controls": controls,
        "risk_blocks": risk_blocks,
        "blockers": _unique(blockers),
    }


def _observability_summary(source: Mapping[str, Any], thresholds: Mapping[str, float]) -> dict[str, Any]:
    contexts = _contexts(source, "observability")
    score = _score_from_contexts(contexts, ("observability_score",))
    evidence = {
        "audit_log_present": _bool_from_contexts(contexts, ("audit_log_present",)),
        "sanitized_evidence_present": _bool_from_contexts(contexts, ("sanitized_evidence_present",)),
        "owner_review_packet_present": _bool_from_contexts(contexts, ("owner_review_packet_present",)),
        "monitoring_plan_present": _bool_from_contexts(contexts, ("monitoring_plan_present",)),
        "dashboard_projection_safe": _bool_from_contexts(contexts, ("dashboard_projection_safe",)),
    }
    active_score = score if score is not None else _bool_score(evidence.values())
    observability_blocks = _blockers_from_contexts(contexts, ("observability_blocks",))
    blockers: list[str] = []
    if active_score is None:
        blockers.append("observability_score_missing")
    elif active_score < thresholds["min_observability_score"]:
        blockers.append("observability_score_below_threshold")
    for key, value in evidence.items():
        if value is None:
            blockers.append(f"{key}_missing")
        elif value is False:
            blockers.append(f"{key}_false")
    blockers.extend(observability_blocks)
    return {
        "ready": not blockers,
        "score": active_score,
        "explicit_score": score,
        "threshold": thresholds["min_observability_score"],
        "evidence": evidence,
        "observability_blocks": observability_blocks,
        "blockers": _unique(blockers),
    }


def _owner_gate_summary(source: Mapping[str, Any]) -> dict[str, Any]:
    contexts = _contexts(source, "owner_gate")
    owner_gate_required = _bool_from_contexts(contexts, ("owner_gate_required",))
    owner_approval_required = _bool_from_contexts(contexts, ("owner_approval_required",))
    owner_review_ready = _bool_from_contexts(contexts, ("owner_review_ready",))
    execution_allowed = _bool_from_contexts(contexts, ("execution_allowed",))
    manual_execution_only = _bool_from_contexts(contexts, ("manual_execution_only",))
    blockers: list[str] = []
    expected_true = {
        "owner_gate_required": owner_gate_required,
        "owner_approval_required": owner_approval_required,
        "owner_review_ready": owner_review_ready,
        "manual_execution_only": manual_execution_only,
    }
    for key, value in expected_true.items():
        if value is None:
            blockers.append(f"{key}_missing")
        elif value is False:
            blockers.append(f"{key}_false")
    if execution_allowed is None:
        blockers.append("execution_allowed_missing")
    elif execution_allowed is True:
        blockers.append("execution_allowed_true")
    return {
        "ready": not blockers,
        "owner_gate_required": owner_gate_required,
        "owner_approval_required": owner_approval_required,
        "owner_review_ready": owner_review_ready,
        "execution_allowed": execution_allowed,
        "manual_execution_only": manual_execution_only,
        "blockers": _unique(blockers),
    }


def _broker_boundary_summary(source: Mapping[str, Any]) -> dict[str, Any]:
    contexts = _contexts(source, "broker_boundary")
    input_flags = {flag: _bool_from_contexts(contexts, (flag,)) for flag in BROKER_BOUNDARY_FLAGS}
    blockers: list[str] = []
    for flag, value in input_flags.items():
        if value is None:
            blockers.append(f"{flag}_missing")
        elif value is True:
            blockers.append(f"{flag}_true")
    return {
        "ready": not blockers,
        "input_flags": input_flags,
        "boundary_preserved": not any(value is True for value in input_flags.values()),
        "blockers": _unique(blockers),
    }


def _data_quality_summary(source: Mapping[str, Any], thresholds: Mapping[str, float]) -> dict[str, Any]:
    contexts = [
        _mapping(source.get("data_quality")),
        _mapping(source.get("profit_candidate_quality")),
        _mapping(source.get("readiness_snapshot")),
        source,
    ]
    score = _score_from_contexts(contexts, ("data_quality_score",))
    missing_fields = _as_list(_value_from_contexts(contexts, ("missing_fields",)))
    invalid_rows = _number_from_contexts(contexts, ("invalid_rows",))
    duplicate_trades = _number_from_contexts(contexts, ("duplicate_trades",))
    malformed_timestamps = _number_from_contexts(contexts, ("malformed_timestamps",))
    blockers: list[str] = []
    if score is None:
        blockers.append("data_quality_score_missing")
    elif score < thresholds["min_data_quality_score"]:
        blockers.append("data_quality_score_below_threshold")
    if missing_fields:
        blockers.append("data_quality_missing_fields")
    for key, value in {
        "invalid_rows": invalid_rows,
        "duplicate_trades": duplicate_trades,
        "malformed_timestamps": malformed_timestamps,
    }.items():
        if value is not None and value > 0:
            blockers.append(f"{key}_present")
    return {
        "ready": not blockers,
        "score": score,
        "threshold": thresholds["min_data_quality_score"],
        "missing_fields": missing_fields,
        "invalid_rows": invalid_rows,
        "duplicate_trades": duplicate_trades,
        "malformed_timestamps": malformed_timestamps,
        "blockers": _unique(blockers),
    }


def _resolve_readiness_status(
    *,
    missing_core_evidence: bool,
    evidence_summary: Mapping[str, Any],
    quality_summary: Mapping[str, Any],
    risk_summary: Mapping[str, Any],
    observability_summary: Mapping[str, Any],
    owner_gate_summary: Mapping[str, Any],
    broker_boundary_summary: Mapping[str, Any],
    data_quality_summary: Mapping[str, Any],
    readiness_score: float | None,
    min_readiness_score: float,
) -> str:
    if missing_core_evidence:
        return INCOMPLETE_INPUTS
    if not evidence_summary["ready"]:
        return BLOCKED_BY_EVIDENCE_SUFFICIENCY
    if not quality_summary["ready"]:
        return BLOCKED_BY_CANDIDATE_QUALITY
    if not risk_summary["ready"]:
        return BLOCKED_BY_RISK_CONTROLS
    if not observability_summary["ready"]:
        return BLOCKED_BY_OBSERVABILITY
    if not owner_gate_summary["ready"]:
        return BLOCKED_BY_OWNER_GATE
    if not broker_boundary_summary["ready"]:
        return BLOCKED_BY_BROKER_BOUNDARY
    if not data_quality_summary["ready"]:
        return BLOCKED_BY_DATA_QUALITY
    if readiness_score is None or readiness_score < min_readiness_score:
        return NEEDS_MORE_EVIDENCE
    return DEMO_REVIEW_READY


def _owner_action_queue(
    *,
    evidence_summary: Mapping[str, Any],
    quality_summary: Mapping[str, Any],
    risk_summary: Mapping[str, Any],
    observability_summary: Mapping[str, Any],
    owner_gate_summary: Mapping[str, Any],
    broker_boundary_summary: Mapping[str, Any],
    data_quality_summary: Mapping[str, Any],
    next_best_packet: str,
) -> list[dict[str, Any]]:
    actions = [
        (
            "REVIEW_EVIDENCE_SUFFICIENCY",
            "Review evidence sufficiency",
            "high",
            evidence_summary.get("blockers", []),
            "Review sanitized evidence depth, walk-forward, OOS, and regime coverage before any owner decision.",
        ),
        (
            "REVIEW_CANDIDATE_QUALITY",
            "Review candidate quality",
            "high",
            quality_summary.get("blockers", []),
            "Review sanitized quality-improvement evidence before any owner decision.",
        ),
        (
            "REVIEW_RISK_CONTROLS",
            "Review risk controls",
            "high",
            risk_summary.get("blockers", []),
            "Review loss stops, kill switch, max-loss gates, and position-size limits before any owner decision.",
        ),
        (
            "REVIEW_OBSERVABILITY",
            "Review observability",
            "high",
            observability_summary.get("blockers", []),
            "Review audit logs, sanitized evidence, owner packet, monitoring plan, and dashboard projection safety.",
        ),
        (
            "REVIEW_OWNER_GATE",
            "Review owner gate",
            "high",
            owner_gate_summary.get("blockers", []),
            "Confirm owner review is required and no execution authority is granted.",
        ),
        (
            "REVIEW_BROKER_BOUNDARY",
            "Review broker boundary",
            "high",
            broker_boundary_summary.get("blockers", []),
            "Confirm broker, bank, credential, trading, and money boundaries remain closed.",
        ),
        (
            "REVIEW_DATA_QUALITY",
            "Review data quality",
            "high",
            data_quality_summary.get("blockers", []),
            "Review sanitized data quality evidence before any owner decision.",
        ),
        (
            "REVIEW_NEXT_PACKET",
            f"Review next packet: {next_best_packet}",
            "medium",
            ["owner_review_required"],
            "Review the next packet manually; no execution is authorized.",
        ),
    ]
    return [_action(action_id, title, priority, blocked_by, safe_action) for action_id, title, priority, blocked_by, safe_action in actions]


def _action(
    action_id: str,
    title: str,
    priority: str,
    blocked_by: Sequence[str],
    safe_action: str,
) -> dict[str, Any]:
    return {
        "action_id": action_id,
        "title": title,
        "priority": priority,
        "owner_decision_required": True,
        "execution_allowed": False,
        "safe_action": safe_action,
        "blocked_by": list(blocked_by) or ["owner_review_required"],
    }


def _safe_manual_next_action(readiness_status: str) -> str:
    if readiness_status == DEMO_REVIEW_READY:
        return (
            "Owner may review the demo-candidate readiness packet and queue supervised demo readiness. "
            "AIOS does not trade, access brokers, authorize money movement, or use credentials."
        )
    if readiness_status == INCOMPLETE_INPUTS:
        return (
            "Provide sanitized evidence sufficiency, profit candidate quality, risk controls, observability, "
            "owner gate, and broker-boundary evidence, then rerun this evaluator."
        )
    return (
        "Collect sanitized demo-readiness evidence, rerun the read-only readiness evaluator, and keep all "
        "trading, broker, bank, credential, and money actions outside AIOS until owner approval."
    )


def _next_remaining_lane(remaining: Mapping[str, Any], next_best_packet: str) -> dict[str, Any]:
    lanes = remaining.get("remaining_lanes")
    if isinstance(lanes, Sequence) and not isinstance(lanes, (str, bytes)):
        for item in lanes:
            lane = _mapping(item)
            if not lane:
                continue
            safe_packet_name = _text(lane.get("safe_packet_name"), "")
            lane_id = _text(lane.get("lane_id"), "")
            if safe_packet_name == next_best_packet or (
                next_best_packet == NEXT_PACKET_IF_READY and NEXT_LANE_ID in lane_id
            ):
                return {
                    "lane_id": lane_id or NEXT_LANE_ID,
                    "title": _text(lane.get("title"), "Supervised demo readiness"),
                    "status": _text(lane.get("status"), "OWNER_REVIEW_REQUIRED"),
                    "safe_packet_name": safe_packet_name or next_best_packet,
                }
    if next_best_packet == NEXT_PACKET_IF_READY:
        return {
            "lane_id": NEXT_LANE_ID,
            "title": "Supervised demo readiness",
            "status": "OWNER_REVIEW_REQUIRED",
            "safe_packet_name": NEXT_PACKET_IF_READY,
        }
    return {
        "lane_id": CURRENT_LANE_ID,
        "title": "Demo candidate review readiness",
        "status": "LOCAL_EVIDENCE_REQUIRED",
        "safe_packet_name": THIS_PACKET,
    }


def _input_summary(
    *,
    source: Mapping[str, Any],
    explicit_readiness_score: float | None,
    derived_readiness_score: float | None,
    sub_scores: Mapping[str, float | None],
    missing_information: Sequence[str],
) -> dict[str, Any]:
    return {
        "input_fields_seen": sorted(str(key) for key in source.keys()),
        "meaningful_evidence_present": any(_has_meaningful_value(source.get(key)) for key in CORE_EVIDENCE_KEYS),
        "explicit_readiness_score": explicit_readiness_score,
        "derived_readiness_score": derived_readiness_score,
        "sub_scores": dict(sub_scores),
        "missing_information": list(missing_information),
    }


def _safety() -> dict[str, bool]:
    return {
        "read_only": True,
        "manual_execution_only": True,
        "money_movement_allowed": False,
        "bank_access_allowed": False,
        "broker_api_allowed": False,
        "trade_execution_allowed": False,
        "demo_execution_allowed": False,
        "credential_use_allowed": False,
        "scheduler_allowed": False,
        "daemon_allowed": False,
        "webhook_allowed": False,
        "dashboard_runtime_allowed": False,
        "owner_gate_required": True,
        "fixed_return_target_promised": False,
        "profit_claim_authorized": False,
    }


def _empty_summary(name: str, blockers: Sequence[str]) -> dict[str, Any]:
    return {
        "ready": False,
        "summary": name,
        "score": None,
        "threshold": None,
        "blockers": list(blockers),
    }


def _missing_information(source: Mapping[str, Any]) -> list[str]:
    return [key for key in CORE_EVIDENCE_KEYS if not _has_meaningful_value(source.get(key))]


def _has_meaningful_value(value: Any) -> bool:
    if isinstance(value, Mapping):
        return bool(value)
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return bool(value)
    return value is not None


def _contains_sensitive_key(value: Any) -> bool:
    if isinstance(value, Mapping):
        for key, item in value.items():
            lowered = str(key).lower()
            if lowered not in SAFE_BOUNDARY_KEYS and any(part in lowered for part in SENSITIVE_KEY_PARTS):
                return True
            if _contains_sensitive_key(item):
                return True
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return any(_contains_sensitive_key(item) for item in value)
    return False


def _contexts(source: Mapping[str, Any], section: str) -> list[Mapping[str, Any]]:
    return [
        _mapping(source.get(section)),
        _mapping(source.get("readiness_snapshot")),
        source,
    ]


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _value_from_contexts(contexts: Sequence[Mapping[str, Any]], keys: Sequence[str]) -> Any:
    for context in contexts:
        for key in keys:
            if key in context:
                return context[key]
    return None


def _score_from_contexts(contexts: Sequence[Mapping[str, Any]], keys: Sequence[str]) -> float | None:
    return _score(_value_from_contexts(contexts, keys))


def _number_from_contexts(contexts: Sequence[Mapping[str, Any]], keys: Sequence[str]) -> float | None:
    return _number(_value_from_contexts(contexts, keys))


def _bool_from_contexts(contexts: Sequence[Mapping[str, Any]], keys: Sequence[str]) -> bool | None:
    return _as_bool(_value_from_contexts(contexts, keys))


def _text_from_contexts(contexts: Sequence[Mapping[str, Any]], keys: Sequence[str]) -> str:
    return _text(_value_from_contexts(contexts, keys), "")


def _blockers_from_contexts(contexts: Sequence[Mapping[str, Any]], keys: Sequence[str]) -> list[str]:
    blockers: list[str] = []
    for key in keys:
        value = _value_from_contexts(contexts, (key,))
        if isinstance(value, Mapping):
            for item in value.values():
                blockers.extend(_as_list(item))
        else:
            blockers.extend(_as_list(value))
    return _unique(str(item) for item in blockers if str(item))


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, Mapping):
        return list(value.values())
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return list(value)
    return [value]


def _score(value: Any) -> float | None:
    number = _number(value)
    if number is None:
        return None
    if number > 1.0:
        number = number / 100.0 if number <= 100.0 else 1.0
    return max(0.0, min(1.0, number))


def _number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        number = float(value)
    elif isinstance(value, str):
        try:
            number = float(value.strip())
        except ValueError:
            return None
    else:
        return None
    return number if isfinite(number) else None


def _as_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "yes", "y", "1", "pass", "passed", "ready"}:
            return True
        if lowered in {"false", "no", "n", "0", "fail", "failed", "blocked"}:
            return False
    if isinstance(value, (int, float)):
        return bool(value)
    return None


def _text(value: Any, default: str) -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def _bool_score(values: Sequence[bool | None]) -> float | None:
    present = [value for value in values if value is not None]
    if not present:
        return None
    return sum(1.0 for value in present if value is True) / len(present)


def _average_score(values: Sequence[float | None]) -> float | None:
    present = [value for value in values if value is not None]
    if not present:
        return None
    return round(sum(present) / len(present), 6)


def _unique(values: Sequence[str] | Any) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for raw_value in values:
        value = str(raw_value)
        if value and value not in seen:
            seen.add(value)
            ordered.append(value)
    return ordered


__all__ = [
    "SCHEMA",
    "MODE",
    "evaluate_demo_candidate_review_readiness_v1",
]
