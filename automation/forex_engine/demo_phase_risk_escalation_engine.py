"""Demo-phase risk escalation engine for paper-only demo evidence governance."""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from automation.forex_engine.demo_phase_performance_monitor import (
    DECISION_DEGRADING,
    DECISION_IMPROVING,
    DECISION_INSUFFICIENT,
    DECISION_RISK_VIOLATION,
    DECISION_STABLE,
    run_demo_phase_performance_monitor,
)
from automation.forex_engine.demo_phase_evidence_tracker import DEMO_PHASE_MORE_EVIDENCE_REQUIRED

MODE = "DEMO_PHASE_RISK_ESCALATION_ENGINE"
ESCALATION_NO_ESCALATION = "NO_ESCALATION"
ESCALATION_WARNING = "WARNING"
ESCALATION_RISK = "RISK_ESCALATION"
ESCALATION_SUSPENSION = "DEMO_PHASE_SUSPENSION_RECOMMENDED"

ACTION_CONTINUE = "continue_demo_phase"
ACTION_MONITOR = "monitor_and_collect_additional_evidence"
ACTION_REVIEW = "review_strategy_parameters_and_risk_controls"
ACTION_REDUCE = "reduce_risk_exposure_and_stop_adding_risk"
ACTION_SUSPEND = "suspend_demo_phase_until_operator_review"

RISK_REPETITION_THRESHOLD = 2


def _as_list(value: Any) -> list[Any]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [item for item in value]


def _to_bool(value: Any) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1", "yes"}:
            return True
        if normalized in {"false", "0", "no"}:
            return False
    return None


def _safety() -> dict[str, bool]:
    return {
        "paper_only": True,
        "demo_phase_risk_escalation_engine_only": True,
        "broker_access": False,
        "credentials_access": False,
        "network_access": False,
        "live_trading_active": False,
        "demo_execution_active": False,
        "demo_activation_active": False,
        "capital_allocation_modified": False,
    }


def _safe(value: Any) -> bool:
    safety = value if isinstance(value, Mapping) else {}
    if not isinstance(safety, Mapping):
        return False
    if _to_bool(safety.get("paper_only")) is False:
        return False
    keys = (
        "broker_access",
        "credentials_access",
        "network_access",
        "live_trading_active",
        "demo_execution_active",
        "demo_activation_active",
        "capital_allocation_modified",
    )
    for key in keys:
        if _to_bool(safety.get(key)) is True:
            return False
    return True


def _safe_payload(value: Any) -> dict[str, bool]:
    if isinstance(value, Mapping):
        return {str(key): bool(v) for key, v in value.items()}
    return {}


def _normalize_levels(value: Any) -> list[str]:
    levels = []
    for item in _as_list(value):
        if str(item) in {ESCALATION_NO_ESCALATION, ESCALATION_WARNING, ESCALATION_RISK, ESCALATION_SUSPENSION}:
            levels.append(str(item))
    return levels


def _is_unsafe(reason: str) -> bool:
    return any(
        reason.startswith("unsafe_evidence")
        or reason.startswith("malformed_evidence")
        or reason.startswith("evidence_quality_issues")
        or reason == "insufficient_evidence"
        for reason in {reason} if reason
    )


def run_demo_phase_risk_escalation_engine(
    *,
    monitor_result: Mapping[str, Any] | None = None,
    evidence_events: Any = None,
    safe_context: Mapping[str, Any] | None = None,
    escalation_history: Any = None,
    tracker_result: Mapping[str, Any] | None = None,
    repeated_risk_violation_count: int | None = None,
) -> dict[str, Any]:
    safety = _safety()
    if isinstance(safe_context, Mapping):
        for key, value in safe_context.items():
            safety[str(key)] = bool(value)

    if not _safe(safety):
        blocked_reasons = ["safety_violation_detected"]
    else:
        blocked_reasons = []

    monitor_from_external = monitor_result is not None
    if not monitor_from_external:
        monitor = run_demo_phase_performance_monitor(
            evidence_events=evidence_events,
            tracker_result=tracker_result,
            safe_context=safety,
        )
        if isinstance(monitor, Mapping):
            blocked_reasons.extend(str(reason) for reason in monitor.get("blocked_reasons", []))
            performance_state = str(monitor.get("performance_state", DECISION_INSUFFICIENT))
            risk_status = str(monitor.get("risk_status", "RISK_UNCONFIRMED"))
            expectation_completed = bool(monitor.get("monitor_completed", False))
        else:
            performance_state = DECISION_INSUFFICIENT
            risk_status = "RISK_UNCONFIRMED"
            expectation_completed = False
    else:
        blocked_reasons.extend(str(reason) for reason in monitor_result.get("blocked_reasons", []))
        performance_state = str(monitor_result.get("performance_state", DECISION_INSUFFICIENT))
        risk_status = str(monitor_result.get("risk_status", "RISK_UNCONFIRMED"))
        expectation_completed = bool(monitor_result.get("monitor_completed", False))

    blocked_reasons = list(dict.fromkeys(str(reason) for reason in blocked_reasons if reason))

    risk_violation_reasons = [reason for reason in blocked_reasons if "risk" in reason and "risk" in reason.lower()]
    has_unsafe_evidence = any(_is_unsafe(reason) for reason in blocked_reasons)
    missing_evidence = False if monitor_from_external else not evidence_events or len(_as_list(evidence_events)) == 0
    if not expectation_completed and not has_unsafe_evidence:
        blocked_reasons.append("missing_performance_result")

    repeated_risk_violations = 0
    if repeated_risk_violation_count is not None:
        repeated_risk_violations = max(0, int(repeated_risk_violation_count))
    else:
        previous = _normalize_levels(escalation_history)
        repeated_risk_violations = sum(
            1 for level in previous if level in {ESCALATION_RISK, ESCALATION_SUSPENSION}
        )

    risk_block = performance_state == DECISION_RISK_VIOLATION or risk_status == "RISK_VIOLATION"
    if any(reason.startswith("risk_threshold") or reason.startswith("risk_status:") for reason in blocked_reasons):
        risk_block = True
    if any(reason == DEMO_PHASE_MORE_EVIDENCE_REQUIRED for reason in blocked_reasons):
        missing_evidence = True

    is_degrading = performance_state == DECISION_DEGRADING
    is_improving = performance_state == DECISION_IMPROVING
    is_stable = performance_state == DECISION_STABLE
    is_insufficient = performance_state == DECISION_INSUFFICIENT

    if is_improving or is_stable:
        escalation_level = ESCALATION_NO_ESCALATION
        recommended_action = ACTION_CONTINUE
        operator_review_required = False
        escalation_completed = True
        next_safe_action = ACTION_MONITOR
        if missing_evidence:
            escalation_level = ESCALATION_WARNING
            recommended_action = ACTION_REVIEW
            operator_review_required = False
            escalation_completed = False
            next_safe_action = ACTION_MONITOR
    elif is_degrading:
        escalation_level = ESCALATION_WARNING
        recommended_action = ACTION_REVIEW
        operator_review_required = False
        escalation_completed = False
        next_safe_action = ACTION_MONITOR
    elif risk_block or has_unsafe_evidence or missing_evidence or is_insufficient:
        escalation_level = ESCALATION_RISK
        if repeated_risk_violations >= RISK_REPETITION_THRESHOLD or performance_state == DECISION_RISK_VIOLATION and repeated_risk_violations >= 1:
            escalation_level = ESCALATION_SUSPENSION
            recommended_action = ACTION_SUSPEND
            next_safe_action = ACTION_SUSPEND
        else:
            recommended_action = ACTION_REVIEW if is_insufficient else ACTION_REDUCE
            next_safe_action = ACTION_REVIEW
        operator_review_required = True
        escalation_completed = False
    else:
        escalation_level = ESCALATION_WARNING
        recommended_action = ACTION_REVIEW
        operator_review_required = False
        escalation_completed = False
        next_safe_action = ACTION_MONITOR

    return {
        "escalation_completed": bool(escalation_completed),
        "escalation_level": escalation_level,
        "performance_state": performance_state,
        "risk_status": risk_status,
        "recommended_action": recommended_action,
        "operator_review_required": bool(operator_review_required),
        "blocked_reasons": blocked_reasons,
        "next_safe_action": next_safe_action,
        "safety": _safe_payload(safety),
        "mode": MODE,
    }
