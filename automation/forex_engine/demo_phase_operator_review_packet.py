"""Operator-review packet builder for demo-phase performance and risk outputs."""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from automation.forex_engine.demo_phase_risk_escalation_engine import (
    ESCALATION_NO_ESCALATION,
    ESCALATION_RISK,
    ESCALATION_SUSPENSION,
    ESCALATION_WARNING,
    run_demo_phase_risk_escalation_engine,
)
from automation.forex_engine.demo_phase_performance_monitor import (
    DECISION_IMPROVING,
    DECISION_STABLE,
)
from automation.forex_engine.demo_phase_evidence_tracker import DEMO_PHASE_VALIDATION_FAILED

MODE = "DEMO_PHASE_OPERATOR_REVIEW_PACKET"
DECISION_APPROVE_CONTINUE_DEMO_PHASE = "APPROVE_CONTINUE_DEMO_PHASE"
DECISION_REQUEST_MORE_EVIDENCE = "REQUEST_MORE_EVIDENCE"
DECISION_SUSPEND_DEMO_PHASE = "SUSPEND_DEMO_PHASE"
DECISION_REJECT_DEMO_ADVANCEMENT = "REJECT_DEMO_ADVANCEMENT"


def _as_list(value: Any) -> list[Any]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [item for item in value]


def _safety() -> dict[str, bool]:
    return {
        "paper_only": True,
        "demo_phase_operator_review_packet_only": True,
        "broker_access": False,
        "credentials_access": False,
        "network_access": False,
        "live_trading_active": False,
        "demo_execution_active": False,
        "demo_activation_active": False,
        "capital_allocation_modified": False,
    }


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


def _safe_payload(value: Any) -> dict[str, bool]:
    if isinstance(value, Mapping):
        return {str(key): bool(v) for key, v in value.items()}
    return {}


def _safe(value: Any) -> bool:
    safety = value if isinstance(value, Mapping) else {}
    if not isinstance(safety, Mapping):
        return False
    if _to_bool(safety.get("paper_only")) is False:
        return False
    for key in (
        "broker_access",
        "credentials_access",
        "network_access",
        "live_trading_active",
        "demo_execution_active",
        "demo_activation_active",
        "capital_allocation_modified",
    ):
        if _to_bool(safety.get(key)) is True:
            return False
    return True


def _has_unsafe_signal(reasons: list[str]) -> bool:
    for reason in reasons:
        if reason.startswith("unsafe_evidence") or reason.startswith("insufficient_safe_boundary"):
            return True
        if reason == DEMO_PHASE_VALIDATION_FAILED:
            return True
    return False


def _missing_evidence(reasons: list[str]) -> bool:
    for reason in reasons:
        if reason in {"missing_performance_result", "insufficient_evidence", "missing_risk_governance"}:
            return True
        if reason.startswith("missing_"):
            return True
        if reason == "insufficient_data":
            return True
    return False


def run_demo_phase_operator_review_packet(
    *,
    monitor_result: Mapping[str, Any] | None = None,
    tracker_result: Mapping[str, Any] | None = None,
    evidence_events: Any = None,
    safe_context: Mapping[str, Any] | None = None,
    escalation_history: Any = None,
    repeated_risk_violation_count: int | None = None,
) -> dict[str, Any]:
    safety = _safety()
    if isinstance(safe_context, Mapping):
        for key, value in safe_context.items():
            safety[str(key)] = bool(value)

    escalation = run_demo_phase_risk_escalation_engine(
        monitor_result=monitor_result,
        evidence_events=evidence_events,
        safe_context=safety,
        tracker_result=tracker_result,
        escalation_history=escalation_history,
        repeated_risk_violation_count=repeated_risk_violation_count,
    )

    blocked_reasons = [str(reason) for reason in escalation.get("blocked_reasons", []) if reason]
    blocked_reasons = list(dict.fromkeys(blocked_reasons))
    performance_state = str(escalation.get("performance_state", "UNKNOWN"))
    escalation_level = str(escalation.get("escalation_level", ESCALATION_WARNING))
    next_safe_action = str(escalation.get("next_safe_action", "collect_more_demo_phase_evidence"))
    review_reasons: list[str] = [f"performance_state:{performance_state}", f"escalation_level:{escalation_level}"]
    review_reasons.extend(blocked_reasons)

    review_reasons = list(dict.fromkeys(review_reasons))

    operator_review_required = False
    unsafe_evidence = _has_unsafe_signal(blocked_reasons)
    missing_evidence = _missing_evidence(blocked_reasons)
    risk_violation = str(escalation.get("performance_state", "")).upper() == "RISK_VIOLATION" or str(
        escalation.get("risk_status", "")
    ).upper() == "RISK_VIOLATION"
    repeated_risk_violations = 0 if repeated_risk_violation_count is None else max(0, int(repeated_risk_violation_count))
    safety_ok = _safe(safety)

    if not safety_ok:
        operator_review_required = True
        recommended_operator_decision = DECISION_REJECT_DEMO_ADVANCEMENT
        review_reasons.append("unsafe_safety_context_detected")
    elif unsafe_evidence:
        operator_review_required = True
        recommended_operator_decision = DECISION_REJECT_DEMO_ADVANCEMENT
        review_reasons.append("unsafe_evidence_detected")
    elif risk_violation and repeated_risk_violations >= 2:
        operator_review_required = True
        recommended_operator_decision = DECISION_SUSPEND_DEMO_PHASE
    elif risk_violation and escalation.get("operator_review_required") is True:
        operator_review_required = True
        recommended_operator_decision = DECISION_REQUEST_MORE_EVIDENCE
    elif missing_evidence:
        operator_review_required = False
        recommended_operator_decision = DECISION_REQUEST_MORE_EVIDENCE
    elif escalation_level == ESCALATION_WARNING or (not escalation_level and not monitor_result):
        operator_review_required = False
        recommended_operator_decision = DECISION_REQUEST_MORE_EVIDENCE
    elif escalation_level in {ESCALATION_NO_ESCALATION, ESCALATION_WARNING} and performance_state in {
        DECISION_IMPROVING,
        DECISION_STABLE,
    }:
        operator_review_required = False
        recommended_operator_decision = DECISION_APPROVE_CONTINUE_DEMO_PHASE
    elif performance_state in {DECISION_IMPROVING, DECISION_STABLE} and escalation_level == ESCALATION_NO_ESCALATION:
        operator_review_required = False
        recommended_operator_decision = DECISION_APPROVE_CONTINUE_DEMO_PHASE
    else:
        operator_review_required = False
        recommended_operator_decision = DECISION_REQUEST_MORE_EVIDENCE

    review_packet_completed = True

    return {
        "review_packet_completed": bool(review_packet_completed),
        "operator_review_required": bool(operator_review_required),
        "recommended_operator_decision": recommended_operator_decision,
        "performance_state": performance_state,
        "escalation_level": escalation_level,
        "review_reasons": review_reasons,
        "blocked_reasons": blocked_reasons,
        "next_safe_action": next_safe_action,
        "safety": _safe_payload(escalation.get("safety", safety)),
        "mode": MODE,
    }
