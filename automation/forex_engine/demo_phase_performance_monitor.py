"""Demo-phase performance monitor for paper-only evidence review."""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from automation.forex_engine.demo_phase_evidence_tracker import (
    DEMO_PHASE_VALIDATION_FAILED,
    DEMO_PHASE_VALIDATION_PASSED,
    run_demo_phase_evidence_tracker,
)

MODE = "DEMO_PHASE_PERFORMANCE_MONITOR"
DECISION_PERFORMANCE_IMPROVING = "IMPROVING"
DECISION_PERFORMANCE_DEGRADING = "DEGRADING"
DECISION_PERFORMANCE_STABLE = "STABLE"
DECISION_IMPROVING = DECISION_PERFORMANCE_IMPROVING
DECISION_DEGRADING = DECISION_PERFORMANCE_DEGRADING
DECISION_STABLE = DECISION_PERFORMANCE_STABLE
DECISION_RISK_VIOLATION = "RISK_VIOLATION"
DECISION_INSUFFICIENT = "INSUFFICIENT_EVIDENCE"
TREND_STABLE = "STABLE"
TREND_IMPROVING = "IMPROVING"
TREND_DEGRADING = "DEGRADING"

MIN_EVENTS_FOR_TREND = 6
MAX_ACCEPTABLE_DRAWDOWN = 2.5
MAX_ACCEPTABLE_RISK = 50.0
TREND_EPSILON = 0.15

ALLOWED_DIRECTIONS = {"BUY", "SELL"}
ALLOWED_OUTCOMES = {"WIN", "LOSS", "BREAKEVEN"}


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
        "demo_phase_performance_monitor_only": True,
        "broker_access": False,
        "credentials_access": False,
        "network_access": False,
        "live_trading_active": False,
        "demo_execution_active": False,
        "capital_allocation_modified": False,
    }


def _safe(value: Any) -> bool:
    safety = value if isinstance(value, Mapping) else {}
    if not isinstance(safety, Mapping):
        return False
    if _to_bool(safety.get("paper_only")) is False:
        return False
    blocked_keys = (
        "broker_access",
        "credentials_access",
        "network_access",
        "live_trading_active",
        "demo_execution_active",
        "capital_allocation_modified",
    )
    for key in blocked_keys:
        if _to_bool(safety.get(key)) is True:
            return False
    return True


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float))


def _safe_payload(value: Any) -> dict[str, bool]:
    if isinstance(value, Mapping):
        return {str(key): bool(v) for key, v in value.items()}
    return {}


def _validation_blockers_from_event(event: Mapping[str, Any], index: int) -> tuple[list[str], list[str]]:
    hard_blockers: list[str] = []
    risk_blockers: list[str] = []
    required_fields = (
        "timestamp",
        "strategy_name",
        "strategy_version",
        "symbol",
        "direction",
        "realized_pl",
        "risk_amount",
        "max_drawdown",
        "spread_cost",
        "slippage",
        "latency_ms",
        "outcome",
    )
    for field in required_fields:
        if field not in event:
            hard_blockers.append(f"malformed_evidence_event:{index}:missing_{field}")

    if not hard_blockers:
        direction = str(event["direction"]).strip().upper()
        outcome = str(event["outcome"]).strip().upper()
        if direction not in ALLOWED_DIRECTIONS:
            hard_blockers.append(f"malformed_evidence_event:{index}:invalid_direction")
        if outcome not in ALLOWED_OUTCOMES:
            hard_blockers.append(f"malformed_evidence_event:{index}:invalid_outcome")

        for numeric_field in ("realized_pl", "risk_amount", "max_drawdown", "spread_cost", "slippage", "latency_ms"):
            if not _is_number(event.get(numeric_field, None)):
                hard_blockers.append(f"malformed_evidence_event:{index}:invalid_{numeric_field}")

    if not hard_blockers:
        if event["risk_amount"] < 0:
            hard_blockers.append(f"unsafe_evidence:{index}:negative_risk")
        if event["spread_cost"] < 0:
            hard_blockers.append(f"unsafe_evidence:{index}:negative_spread")
        if event["slippage"] < 0:
            hard_blockers.append(f"unsafe_evidence:{index}:negative_slippage")
        if event["max_drawdown"] < 0:
            hard_blockers.append(f"unsafe_evidence:{index}:negative_drawdown")
        if event["latency_ms"] < 0:
            hard_blockers.append(f"unsafe_evidence:{index}:negative_latency")

        if event["latency_ms"] > 4000:
            hard_blockers.append(f"unsafe_evidence:{index}:high_latency")
        if event["slippage"] > 20:
            hard_blockers.append(f"unsafe_evidence:{index}:excessive_slippage")
        if event["spread_cost"] > 25:
            hard_blockers.append(f"unsafe_evidence:{index}:excessive_spread")

        if event["max_drawdown"] > MAX_ACCEPTABLE_DRAWDOWN:
            risk_blockers.append(f"risk_threshold:{index}:excessive_drawdown:{event['max_drawdown']}")
        if event["risk_amount"] > MAX_ACCEPTABLE_RISK:
            risk_blockers.append(f"risk_threshold:{index}:excessive_risk:{event['risk_amount']}")

    return hard_blockers, risk_blockers


def _clean_events(raw_events: Sequence[Any]) -> tuple[list[dict[str, Any]], list[str]]:
    events: list[dict[str, Any]] = []
    blocked_reasons: list[str] = []
    for index, event in enumerate(raw_events):
        if not isinstance(event, Mapping):
            blocked_reasons.append(f"malformed_evidence_event:{index}:not_mapping")
            continue
        hard_blockers, risk_blockers = _validation_blockers_from_event(event, index)
        if hard_blockers:
            blocked_reasons.extend(hard_blockers)
            continue
        blocked_reasons.extend(risk_blockers)
        events.append(
            {
                "timestamp": str(event["timestamp"]),
                "strategy_name": str(event["strategy_name"]),
                "strategy_version": str(event["strategy_version"]),
                "symbol": str(event["symbol"]),
                "direction": str(event["direction"]).strip().upper(),
                "outcome": str(event["outcome"]).strip().upper(),
                "realized_pl": float(event["realized_pl"]),
                "risk_amount": float(event["risk_amount"]),
                "max_drawdown": float(event["max_drawdown"]),
                "spread_cost": float(event["spread_cost"]),
                "slippage": float(event["slippage"]),
                "latency_ms": float(event["latency_ms"]),
            }
        )
    return events, blocked_reasons


def _expectancy(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    return round(sum(values) / len(values), 6)


def _drawdown_level(events: Sequence[Mapping[str, Any]]) -> float:
    if not events:
        return 0.0
    return round(sum(float(event["max_drawdown"]) for event in events) / len(events), 6)


def _consistency(events: Sequence[Mapping[str, Any]]) -> float:
    if not events:
        return 0.0
    wins = sum(1 for event in events if event["outcome"] == "WIN")
    return round(wins / len(events), 4)


def _trend(previous: float, current: float, epsilon: float = TREND_EPSILON) -> str:
    delta = current - previous
    if delta > epsilon:
        return TREND_IMPROVING
    if delta < -epsilon:
        return TREND_DEGRADING
    return TREND_STABLE


def _classify_performance_state(
    *,
    expectancy_delta: float,
    drawdown_delta: float,
    consistency_delta: float,
) -> str:
    if expectancy_delta <= -TREND_EPSILON or consistency_delta <= -TREND_EPSILON or drawdown_delta >= TREND_EPSILON:
        return DECISION_DEGRADING
    if (
        expectancy_delta >= TREND_EPSILON
        and drawdown_delta <= TREND_EPSILON
        and consistency_delta >= -TREND_EPSILON
    ):
        return DECISION_IMPROVING
    return DECISION_STABLE


def run_demo_phase_performance_monitor(
    *,
    evidence_events: Any = None,
    tracker_result: Mapping[str, Any] | None = None,
    safe_context: Mapping[str, Any] | None = None,
    validation_aggregator_result: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    safety = _safety()
    if isinstance(safe_context, Mapping):
        for key, value in safe_context.items():
            safety[str(key)] = bool(value)

    raw_events = _as_list(evidence_events)
    validated_events, validation_reasons = _clean_events(raw_events)

    blocked_reasons: list[str] = list(dict.fromkeys(str(reason) for reason in validation_reasons if reason))
    risk_violations = [reason for reason in blocked_reasons if reason.startswith("risk_threshold")]

    if tracker_result is None:
        tracker = run_demo_phase_evidence_tracker(
            evidence_events=raw_events,
            advancement_result={
                "demo_advancement_approved": True,
                "promotion_recommendation": "DEMO_ADVANCEMENT_APPROVED",
                "safety": safety,
            },
        )
        if isinstance(tracker, Mapping):
            blocked_reasons.extend(str(reason) for reason in tracker.get("blocked_reasons", []))
    else:
        blocked_reasons.extend(str(reason) for reason in tracker_result.get("blocked_reasons", []))

    if validation_aggregator_result is not None:
        blocked_reasons.extend(str(reason) for reason in validation_aggregator_result.get("blocked_reasons", []))
    if not _safe(safety):
        blocked_reasons.append("safety_violation_detected")

    blocked_reasons = list(dict.fromkeys(str(reason) for reason in blocked_reasons if reason))

    if not _safe(safety) or not validated_events or len(validated_events) < MIN_EVENTS_FOR_TREND:
        blocked_reasons.append("insufficient_evidence")
        return {
            "monitor_completed": False,
            "performance_state": DECISION_INSUFFICIENT,
            "expectancy_trend": TREND_STABLE,
            "drawdown_trend": TREND_STABLE,
            "consistency_trend": TREND_STABLE,
            "risk_status": "RISK_UNCONFIRMED",
            "blocked_reasons": blocked_reasons,
            "next_safe_action": "collect_more_demo_phase_performance_evidence",
            "safety": _safe_payload(safety),
            "mode": MODE,
        }

    if any("unsafe_evidence" in reason for reason in blocked_reasons):
        blocked_reasons.append("evidence_quality_issues")

    midpoint = max(1, len(validated_events) // 2)
    early_events = validated_events[:midpoint]
    late_events = validated_events[midpoint:]

    early_expectancy = _expectancy([float(event["realized_pl"]) for event in early_events])
    late_expectancy = _expectancy([float(event["realized_pl"]) for event in late_events])
    early_drawdown = _drawdown_level(early_events)
    late_drawdown = _drawdown_level(late_events)
    early_consistency = _consistency(early_events)
    late_consistency = _consistency(late_events)

    expectancy_delta = late_expectancy - early_expectancy
    drawdown_delta = late_drawdown - early_drawdown
    consistency_delta = late_consistency - early_consistency

    expectancy_trend = _trend(early_expectancy, late_expectancy)
    if drawdown_delta > TREND_EPSILON:
        drawdown_trend = TREND_DEGRADING
    elif drawdown_delta < -TREND_EPSILON:
        drawdown_trend = TREND_IMPROVING
    else:
        drawdown_trend = TREND_STABLE
    consistency_trend = _trend(early_consistency, late_consistency)

    if risk_violations:
        performance_state = DECISION_RISK_VIOLATION
        risk_status = "RISK_VIOLATION"
        next_safe_action = "reduce_risk_and_drawdown_exposure"
    else:
        performance_state = _classify_performance_state(
            expectancy_delta=expectancy_delta,
            drawdown_delta=drawdown_delta,
            consistency_delta=consistency_delta,
        )
        risk_status = "RISK_OK"
        if performance_state == DECISION_DEGRADING:
            next_safe_action = "pause_and_refine_strategy_parameters"
        elif performance_state == DECISION_IMPROVING:
            next_safe_action = "continue_collecting_evidence"
        else:
            next_safe_action = "monitor_continuously"

    if tracker_result is not None and tracker_result.get("demo_phase_status") in {
        DEMO_PHASE_VALIDATION_FAILED,
        "",
    }:
        blocked_reasons.append("demo_tracking_not_started")

    if any(reason.startswith("risk_threshold") for reason in blocked_reasons) and performance_state != DECISION_RISK_VIOLATION:
        risk_status = "RISK_VIOLATION"
        performance_state = DECISION_RISK_VIOLATION
        next_safe_action = "reduce_risk_and_drawdown_exposure"

    monitor_completed = performance_state in {DECISION_IMPROVING, DECISION_STABLE, DECISION_DEGRADING}

    return {
        "monitor_completed": bool(monitor_completed),
        "performance_state": performance_state,
        "expectancy_trend": expectancy_trend,
        "drawdown_trend": drawdown_trend,
        "consistency_trend": consistency_trend,
        "risk_status": risk_status,
        "blocked_reasons": blocked_reasons,
        "next_safe_action": next_safe_action,
        "safety": _safe_payload(safety),
        "mode": MODE,
    }
