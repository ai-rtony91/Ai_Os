"""Paper-only demo-phase evidence tracker."""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from automation.forex_engine.governed_demo_advancement_gate import (
    DECISION_DEMO_ADVANCEMENT_APPROVED,
    run_governed_demo_advancement_gate,
)

MODE = "DEMO_PHASE_EVIDENCE_TRACKER"
DEMO_PHASE_NOT_STARTED = "DEMO_PHASE_NOT_STARTED"
DEMO_PHASE_TRACKING = "DEMO_PHASE_TRACKING"
DEMO_PHASE_MORE_EVIDENCE_REQUIRED = "DEMO_PHASE_MORE_EVIDENCE_REQUIRED"
DEMO_PHASE_VALIDATION_PASSED = "DEMO_PHASE_VALIDATION_PASSED"
DEMO_PHASE_VALIDATION_FAILED = "DEMO_PHASE_VALIDATION_FAILED"
DEMO_PHASE_BLOCKED = "DEMO_PHASE_BLOCKED"

ALLOWED_DIRECTIONS = {"BUY", "SELL"}
ALLOWED_OUTCOMES = {"WIN", "LOSS", "BREAKEVEN"}
MIN_VALID_EVENTS_FOR_VALIDATION = 3


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
        "demo_phase_evidence_tracker_only": True,
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
    for key in (
        "broker_access",
        "credentials_access",
        "network_access",
        "live_trading_active",
        "demo_execution_active",
        "capital_allocation_modified",
    ):
        if _to_bool(safety.get(key)) is True:
            return False
    return True


def _as_list(value: Any) -> list[Any]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [item for item in value]


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float))


def _validate_event(event: Mapping[str, Any], index: int) -> tuple[bool, dict[str, Any], list[str]]:
    reasons: list[str] = []
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

    event_dict = event if isinstance(event, Mapping) else {}
    if not event_dict:
        reasons.append(f"malformed_evidence_event:{index}:not_mapping")
        return False, {}, reasons

    for field in required_fields:
        if field not in event_dict:
            reasons.append(f"malformed_evidence_event:{index}:missing_{field}")

    if reasons:
        return False, {}, reasons

    timestamp = str(event_dict["timestamp"])
    strategy_name = str(event_dict["strategy_name"])
    strategy_version = str(event_dict["strategy_version"])
    symbol = str(event_dict["symbol"])
    direction = str(event_dict["direction"]).strip().upper()
    outcome = str(event_dict["outcome"]).strip().upper()
    realized_pl = event_dict["realized_pl"]
    risk_amount = event_dict["risk_amount"]
    max_drawdown = event_dict["max_drawdown"]
    spread_cost = event_dict["spread_cost"]
    slippage = event_dict["slippage"]
    latency_ms = event_dict["latency_ms"]

    if not timestamp:
        reasons.append(f"malformed_evidence_event:{index}:empty_timestamp")
    if not strategy_name:
        reasons.append(f"malformed_evidence_event:{index}:empty_strategy_name")
    if not strategy_version:
        reasons.append(f"malformed_evidence_event:{index}:empty_strategy_version")
    if not symbol:
        reasons.append(f"malformed_evidence_event:{index}:empty_symbol")
    if direction not in ALLOWED_DIRECTIONS:
        reasons.append(f"malformed_evidence_event:{index}:invalid_direction")
    if outcome not in ALLOWED_OUTCOMES:
        reasons.append(f"malformed_evidence_event:{index}:invalid_outcome")

    for numeric_field in (
        "realized_pl",
        "risk_amount",
        "max_drawdown",
        "spread_cost",
        "slippage",
        "latency_ms",
    ):
        value = event_dict[numeric_field]
        if not _is_number(value):
            reasons.append(f"malformed_evidence_event:{index}:invalid_{numeric_field}")

    if reasons:
        return False, {}, reasons

    if risk_amount < 0:
        reasons.append(f"unsafe_evidence:{index}:negative_risk")
    if spread_cost < 0:
        reasons.append(f"unsafe_evidence:{index}:negative_spread_cost")
    if slippage < 0:
        reasons.append(f"unsafe_evidence:{index}:negative_slippage")
    if max_drawdown < 0:
        reasons.append(f"unsafe_evidence:{index}:negative_drawdown")
    if latency_ms < 0:
        reasons.append(f"unsafe_evidence:{index}:negative_latency")

    safe_threshold = 4000
    if latency_ms > safe_threshold:
        reasons.append(f"unsafe_evidence:{index}:high_latency")
    if slippage > 20:
        reasons.append(f"unsafe_evidence:{index}:excessive_slippage")
    if spread_cost > 25:
        reasons.append(f"unsafe_evidence:{index}:excessive_spread")

    if any(reason.startswith("unsafe_evidence") for reason in reasons):
        return False, {}, reasons

    cleaned = {
        "timestamp": timestamp,
        "strategy_name": strategy_name,
        "strategy_version": strategy_version,
        "symbol": symbol,
        "direction": direction,
        "realized_pl": float(realized_pl),
        "risk_amount": float(risk_amount),
        "max_drawdown": float(max_drawdown),
        "spread_cost": float(spread_cost),
        "slippage": float(slippage),
        "latency_ms": float(latency_ms),
        "outcome": outcome,
    }
    return True, cleaned, []


def _event_score(event: Mapping[str, Any]) -> float:
    realized = float(event["realized_pl"])
    spread = float(event["spread_cost"])
    slippage = float(event["slippage"])
    risk = float(event["risk_amount"])
    drawdown = float(event["max_drawdown"])
    latency = float(event["latency_ms"])
    outcome = str(event["outcome"])

    outcome_bonus = 1.0 if outcome == "WIN" else (-1.0 if outcome == "LOSS" else 0.0)
    risk_penalty = min(risk / 10.0, 2.0)
    drawdown_penalty = min(drawdown / 5.0, 4.0)
    return round(realized - spread - slippage - risk_penalty - drawdown_penalty - latency / 1000.0 + outcome_bonus, 6)


def run_demo_phase_evidence_tracker(
    *,
    advancement_result: Mapping[str, Any] | None = None,
    demo_advancement_result: Mapping[str, Any] | None = None,
    demo_advancement_payload: Mapping[str, Any] | None = None,
    evidence_events: Any = None,
    demo_validation_result: Mapping[str, Any] | None = None,
    safe_context: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    if advancement_result is None:
        if demo_advancement_result is not None:
            advancement_result = dict(demo_advancement_result)
        elif demo_advancement_payload is not None:
            advancement_result = dict(demo_advancement_payload)
        else:
            advancement_result = run_governed_demo_advancement_gate(demo_validation_result=demo_validation_result)

    source = dict(advancement_result)

    blocked_reasons: list[str] = []
    safety = _safety()
    if isinstance(safe_context, Mapping):
        for key, value in safe_context.items():
            safety[str(key)] = bool(value)

    if not _safe(safety):
        blocked_reasons.append("safety_violation_detected")

    advancement_decision = str(source.get("promotion_recommendation", ""))
    demo_advancement_approved = bool(source.get("demo_advancement_approved", False))

    if advancement_decision and advancement_decision != DECISION_DEMO_ADVANCEMENT_APPROVED:
        blocked_reasons.append(f"governed_advancement_blocked:{advancement_decision or 'UNKNOWN'}")

    if not demo_advancement_approved:
        blocked_reasons.append("governed_advancement_not_approved")

    events = _as_list(evidence_events)
    validated_events: list[dict[str, Any]] = []
    malformed_reasons: list[str] = []
    invalid_events = 0

    for index, event in enumerate(events):
        if not isinstance(event, Mapping):
            invalid_events += 1
            malformed_reasons.append(f"malformed_evidence_event:{index}:not_mapping")
            continue
        valid, cleaned, reasons = _validate_event(event, index)
        if valid:
            validated_events.append(cleaned)
        else:
            invalid_events += 1
            malformed_reasons.extend(reasons)

    blocked_reasons.extend(malformed_reasons)
    blocked_reasons = list(dict.fromkeys(str(reason) for reason in blocked_reasons if reason))

    demo_phase_active = bool(demo_advancement_approved and not blocked_reasons)
    evidence_events_count = len(events)
    validated_events_count = len(validated_events)

    if validated_events_count > 0:
        raw_scores = [_event_score(event) for event in validated_events]
        current_demo_score = round(sum(raw_scores) / validated_events_count, 3)
    else:
        current_demo_score = 0.0

    if not demo_advancement_approved:
        demo_phase_status = DEMO_PHASE_NOT_STARTED
        next_safe_action = "advance_through_governed_demo_approval"
        demo_phase_active = False
    elif blocked_reasons and any(reason.startswith("safety_violation_detected") for reason in blocked_reasons):
        demo_phase_status = DEMO_PHASE_BLOCKED
        next_safe_action = "restore_paper_only_safety"
        demo_phase_active = False
    elif blocked_reasons and any("malformed_evidence_event" in reason or reason.startswith("unsafe_evidence") for reason in blocked_reasons):
        demo_phase_status = DEMO_PHASE_MORE_EVIDENCE_REQUIRED
        next_safe_action = "correct_and_resubmit_evidence_events"
        demo_phase_active = False
    elif validated_events_count == 0:
        demo_phase_status = DEMO_PHASE_TRACKING
        next_safe_action = "collect_demo_phase_evidence"
    elif validated_events_count < MIN_VALID_EVENTS_FOR_VALIDATION:
        demo_phase_status = DEMO_PHASE_TRACKING
        next_safe_action = "collect_more_demo_phase_events"
    elif current_demo_score > 1.0:
        demo_phase_status = DEMO_PHASE_VALIDATION_PASSED
        next_safe_action = "forward_to_governed_demo_review"
    else:
        demo_phase_status = DEMO_PHASE_VALIDATION_FAILED
        next_safe_action = "investigate_demo_phase_evidence_quality"

    return {
        "tracking_completed": bool(demo_advancement_approved),
        "demo_phase_active": bool(demo_phase_active),
        "evidence_events_count": int(evidence_events_count),
        "validated_events_count": int(validated_events_count),
        "invalid_events_count": int(invalid_events),
        "current_demo_score": float(current_demo_score),
        "demo_phase_status": demo_phase_status,
        "blocked_reasons": blocked_reasons,
        "next_safe_action": next_safe_action,
        "safety": safety,
        "mode": MODE,
    }
