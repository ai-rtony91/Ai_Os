"""Live-candidate readiness spine for paper/demo governance chain."""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from automation.forex_engine.demo_validation_result_aggregator import (
    run_demo_validation_result_aggregator,
)
from automation.forex_engine.demo_phase_evidence_tracker import (
    DEMO_PHASE_TRACKING,
    DEMO_PHASE_VALIDATION_FAILED,
    DEMO_PHASE_VALIDATION_PASSED,
)
from automation.forex_engine.demo_phase_operator_review_packet import (
    DECISION_APPROVE_CONTINUE_DEMO_PHASE,
    run_demo_phase_operator_review_packet,
)
from automation.forex_engine.demo_phase_risk_escalation_engine import (
    ESCALATION_RISK,
    ESCALATION_SUSPENSION,
    run_demo_phase_risk_escalation_engine,
)
from automation.forex_engine.demo_phase_performance_monitor import (
    DECISION_IMPROVING,
    DECISION_STABLE,
    DECISION_DEGRADING,
)

MODE = "LIVE_CANDIDATE_READINESS_SPINE"
LIVE_CANDIDATE_REVIEW_READY = "LIVE_CANDIDATE_REVIEW_READY"
LIVE_CANDIDATE_MORE_DEMO_EVIDENCE_REQUIRED = "LIVE_CANDIDATE_MORE_DEMO_EVIDENCE_REQUIRED"
LIVE_CANDIDATE_BLOCKED = "LIVE_CANDIDATE_BLOCKED"
LIVE_CANDIDATE_REJECTED = "LIVE_CANDIDATE_REJECTED"


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


def _safety() -> dict[str, Any]:
    return {
        "paper_only": True,
        "demo_review_only": True,
        "live_trading_authorized": False,
        "demo_execution_active": False,
        "broker_access": False,
        "credentials_access": False,
        "network_access": False,
        "order_execution_enabled": False,
        "capital_allocation_modified": False,
        "operator_approval_required": True,
    }


def _safe(value: Any) -> bool:
    safety = value if isinstance(value, Mapping) else {}
    if not isinstance(safety, Mapping):
        return False
    if _to_bool(safety.get("paper_only")) is False:
        return False
    blocked_flags = (
        "live_trading_authorized",
        "demo_execution_active",
        "broker_access",
        "credentials_access",
        "network_access",
        "order_execution_enabled",
        "capital_allocation_modified",
    )
    for key in blocked_flags:
        if _to_bool(safety.get(key)) is True:
            return False
    return True


def _safe_payload(value: Any) -> dict[str, bool]:
    if isinstance(value, Mapping):
        return {str(key): bool(v) for key, v in value.items()}
    return {}


def _unsafe_reasons(reasons: Any) -> bool:
    for reason in reasons:
        reason_str = str(reason)
        if "unsafe" in reason_str:
            return True
        if "safety_violation" in reason_str:
            return True
    return False


def run_live_candidate_readiness_spine(
    *,
    demo_validation_result: Mapping[str, Any] | None = None,
    scorecard_result: Mapping[str, Any] | None = None,
    aggregator_result: Mapping[str, Any] | None = None,
    tracker_result: Mapping[str, Any] | None = None,
    monitor_result: Mapping[str, Any] | None = None,
    safe_context: Mapping[str, Any] | None = None,
    evidence_events: Any = None,
    operator_packet: Mapping[str, Any] | None = None,
    escalation_history: Any = None,
    repeated_risk_violation_count: int | None = None,
) -> dict[str, Any]:
    safety = _safety()
    if isinstance(safe_context, Mapping):
        for key, value in safe_context.items():
            safety[str(key)] = bool(value)

    if aggregator_result is None:
        if isinstance(demo_validation_result, Mapping) and "demo_validation_passed" in demo_validation_result:
            aggregator_result = dict(demo_validation_result)
        else:
            aggregator_result = run_demo_validation_result_aggregator(
                demo_review_result=demo_validation_result,
                scorecard_result=scorecard_result,
            )
    else:
        aggregator_result = dict(aggregator_result)

    if tracker_result is None:
        tracker_status = DEMO_PHASE_TRACKING
        tracker_blockers: list[str] = []
    else:
        tracker_status = str(tracker_result.get("demo_phase_status", DEMO_PHASE_TRACKING))
        tracker_blockers = [str(reason) for reason in tracker_result.get("blocked_reasons", [])]

    if operator_packet is None:
        operator_packet = run_demo_phase_operator_review_packet(
            monitor_result=monitor_result,
            tracker_result=tracker_result,
            evidence_events=evidence_events,
            safe_context=safety,
            escalation_history=escalation_history,
            repeated_risk_violation_count=repeated_risk_violation_count,
        )
    else:
        operator_packet = dict(operator_packet)

    escalation = run_demo_phase_risk_escalation_engine(
        monitor_result=monitor_result,
        evidence_events=evidence_events,
        safe_context=safety,
        escalation_history=escalation_history,
        tracker_result=tracker_result,
        repeated_risk_violation_count=repeated_risk_violation_count,
    )

    demo_validation_passed = bool(aggregator_result.get("demo_validation_passed", False))
    stable_winner = dict(aggregator_result.get("stable_winner", {}))
    performance_state = str(escalation.get("performance_state", ""))
    risk_status = str(escalation.get("risk_status", ""))
    operator_decision = str(operator_packet.get("recommended_operator_decision", ""))

    blocked_reasons: list[str] = []
    readiness_reasons: list[str] = []
    safe_boundary_ok = _safe(safety)

    if _unsafe_reasons(operator_packet.get("blocked_reasons", [])) or _unsafe_reasons(tracker_blockers):
        blocked_reasons.append("unsafe_evidence")
    if not _safe(safety):
        blocked_reasons.append("demo_boundary_breached")
        if _to_bool(safety.get("live_trading_authorized")) is True:
            blocked_reasons.append("live_execution_forbidden")
        if _to_bool(safety.get("broker_access")) is True:
            blocked_reasons.append("broker_access_forbidden")
        if _to_bool(safety.get("credentials_access")) is True:
            blocked_reasons.append("credential_access_forbidden")
        if _to_bool(safety.get("network_access")) is True:
            blocked_reasons.append("network_access_forbidden")
    if not demo_validation_passed:
        blocked_reasons.append("demo_validation_not_passed")
    if not stable_winner:
        blocked_reasons.append("missing_stable_winner")

    demo_phase_status = str(tracker_status)
    if demo_phase_status == DEMO_PHASE_VALIDATION_PASSED:
        readiness_reasons.append("demo_phase_evidence_validated")
    elif demo_phase_status == DEMO_PHASE_TRACKING:
        readiness_reasons.append("demo_phase_tracking")
    else:
        blocked_reasons.append("demo_phase_not_validated")

    if performance_state in {DECISION_IMPROVING, DECISION_STABLE}:
        readiness_reasons.append("performance_state_acceptable")
    else:
        blocked_reasons.append("performance_degrading")

    if risk_status != "RISK_VIOLATION" and escalation.get("escalation_level", "") != ESCALATION_SUSPENSION:
        readiness_reasons.append("risk_status_acceptable")
    else:
        blocked_reasons.append("risk_violation_present")

    if operator_decision == DECISION_APPROVE_CONTINUE_DEMO_PHASE:
        readiness_reasons.append("operator_review_approved")
    elif operator_decision:
        blocked_reasons.append("operator_review_not_approved")
    else:
        blocked_reasons.append("operator_review_missing")

    if _to_bool(safety.get("operator_approval_required")) is not False:
        readiness_reasons.append("operator_approval_required")
        operator_approval_required = True
    else:
        blocked_reasons.append("operator_review_not_approved")
        operator_approval_required = False

    blocked_reasons = list(dict.fromkeys(str(reason) for reason in blocked_reasons if reason))

    if not operator_packet.get("operator_review_required", True) and operator_decision != DECISION_APPROVE_CONTINUE_DEMO_PHASE:
        blocked_reasons.append("operator_review_not_approved")

    if (
        not blocked_reasons
        and
        performance_state in {DECISION_IMPROVING, DECISION_STABLE}
        and risk_status != "RISK_VIOLATION"
        and escalation.get("escalation_level", "") != ESCALATION_SUSPENSION
        and operator_decision == DECISION_APPROVE_CONTINUE_DEMO_PHASE
        and demo_validation_passed
        and stable_winner
        and demo_phase_status == "DEMO_PHASE_VALIDATION_PASSED"
    ):
        live_candidate_status = LIVE_CANDIDATE_REVIEW_READY
    elif (
        demo_phase_status == "DEMO_PHASE_TRACKING"
        and demo_validation_passed
        and stable_winner
        and operator_decision == DECISION_APPROVE_CONTINUE_DEMO_PHASE
        and performance_state in {DECISION_IMPROVING, DECISION_STABLE}
        and risk_status != "RISK_VIOLATION"
    ):
        live_candidate_status = LIVE_CANDIDATE_MORE_DEMO_EVIDENCE_REQUIRED
    elif "missing_stable_winner" in blocked_reasons or "demo_validation_not_passed" in blocked_reasons:
        live_candidate_status = LIVE_CANDIDATE_REJECTED
    elif any(reason in blocked_reasons for reason in ("performance_degrading", "risk_violation_present", "operator_review_not_approved", "unsafe_evidence")):
        live_candidate_status = LIVE_CANDIDATE_BLOCKED
    else:
        live_candidate_status = LIVE_CANDIDATE_MORE_DEMO_EVIDENCE_REQUIRED

    readiness_completed = live_candidate_status in {LIVE_CANDIDATE_REVIEW_READY, LIVE_CANDIDATE_BLOCKED, LIVE_CANDIDATE_REJECTED, LIVE_CANDIDATE_MORE_DEMO_EVIDENCE_REQUIRED}

    return {
        "readiness_completed": bool(readiness_completed),
        "live_candidate_review_ready": live_candidate_status == LIVE_CANDIDATE_REVIEW_READY,
        "live_candidate_status": live_candidate_status,
        "demo_validation_passed": bool(demo_validation_passed),
        "demo_phase_status": demo_phase_status,
        "performance_state": performance_state,
        "risk_status": risk_status,
        "operator_decision": operator_decision,
        "stable_winner": stable_winner,
        "readiness_reasons": readiness_reasons,
        "blocked_reasons": blocked_reasons,
        "next_safe_action": str(operator_packet.get("next_safe_action", "")) or str(escalation.get("next_safe_action", "")),
        "operator_approval_required": bool(operator_approval_required),
        "safety": _safe_payload(safety),
        "mode": MODE,
    }
