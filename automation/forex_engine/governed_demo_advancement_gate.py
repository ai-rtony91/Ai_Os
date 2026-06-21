"""Governed demo advancement gate for deterministic paper-only eligibility."""
from __future__ import annotations

from typing import Any
from collections.abc import Mapping, Sequence

from automation.forex_engine.demo_validation_result_aggregator import (
    RECOMMENDATION_DEMO_VALIDATION_PASSED,
    run_demo_validation_result_aggregator,
)

MODE = "GOVERNED_DEMO_ADVANCEMENT_GATE"
DECISION_DEMO_ADVANCEMENT_APPROVED = "DEMO_ADVANCEMENT_APPROVED"
DECISION_MORE_EVIDENCE_REQUIRED = "MORE_EVIDENCE_REQUIRED"
DECISION_DEMO_ADVANCEMENT_BLOCKED = "DEMO_ADVANCEMENT_BLOCKED"


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
        "governed_demo_advancement_gate_only": True,
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


def _normalise_reasons(value: Any) -> list[str]:
    return [str(item) for item in _as_list(value) if str(item)]


def run_governed_demo_advancement_gate(
    *,
    demo_validation_result: Mapping[str, Any] | None = None,
    aggregator_result: Mapping[str, Any] | None = None,
    scorecard_result: Mapping[str, Any] | None = None,
    demo_review_result: Mapping[str, Any] | None = None,
    evidence_batches: Any = None,
    competition_batches: Any = None,
    strategy_batches: Any = None,
    minimum_batches: int = 3,
    winner_consistency_threshold: float = 0.67,
    operator_review_required: bool | None = None,
) -> dict[str, Any]:
    if aggregator_result is None:
        aggregation_input = demo_validation_result
        aggregator_result = run_demo_validation_result_aggregator(
            scorecard_result=scorecard_result,
            demo_review_result=demo_review_result if demo_review_result is not None else None,
            evidence_batches=evidence_batches,
            competition_batches=competition_batches,
            strategy_batches=strategy_batches,
            minimum_batches=minimum_batches,
            winner_consistency_threshold=winner_consistency_threshold,
        )
        if aggregation_input is not None:
            aggregator_result = dict(aggregation_input)

    result = dict(aggregator_result)
    blocked_reasons = _normalise_reasons(result.get("blocked_reasons"))

    demo_validation_passed = bool(result.get("demo_validation_passed", False))
    stable_winner = dict(result.get("stable_winner", {}))
    promotion_recommendation = str(result.get("promotion_recommendation", ""))
    safety = _safety()
    source_safety = result.get("safety", {})
    if isinstance(source_safety, Mapping):
        for key, value in source_safety.items():
            safety[str(key)] = bool(value)

    if operator_review_required is None:
        operator_review_required = _to_bool(result.get("operator_review_required"))
        if operator_review_required is None:
            operator_review_required = True

    if not _safe(safety):
        blocked_reasons.append("safety_violation_detected")

    if not bool(stable_winner):
        blocked_reasons.append("missing_stable_winner")

    if not demo_validation_passed:
        blocked_reasons.append("demo_validation_not_passed")

    if promotion_recommendation != RECOMMENDATION_DEMO_VALIDATION_PASSED:
        blocked_reasons.append(f"promotion_recommendation_not_passed:{promotion_recommendation or 'UNKNOWN'}")

    if operator_review_required is not True:
        blocked_reasons.append("operator_review_required_false")

    blocked_reasons = list(dict.fromkeys(str(reason) for reason in blocked_reasons if reason))

    gate_passed = (
        demo_validation_passed
        and bool(stable_winner)
        and promotion_recommendation == RECOMMENDATION_DEMO_VALIDATION_PASSED
        and _safe(safety)
        and bool(operator_review_required)
        and not blocked_reasons
    )

    if gate_passed:
        decision = DECISION_DEMO_ADVANCEMENT_APPROVED
        next_safe_action = "request_governed_demo_approval"
    elif "missing_stable_winner" in blocked_reasons:
        decision = DECISION_MORE_EVIDENCE_REQUIRED
        next_safe_action = "collect_additional_demo_validation_evidence"
    else:
        decision = DECISION_DEMO_ADVANCEMENT_BLOCKED
        next_safe_action = "resolve_gate_safety_blockers"

    if not blocked_reasons:
        decision = DECISION_DEMO_ADVANCEMENT_APPROVED
        next_safe_action = "request_governed_demo_approval"

    if any(reason.startswith("safety_violation_detected") for reason in blocked_reasons):
        next_safe_action = "restore_paper_only_safety"

    return {
        "gate_completed": bool(result),
        "demo_advancement_approved": bool(gate_passed),
        "demo_validation_passed": bool(demo_validation_passed),
        "stable_winner": stable_winner,
        "promotion_recommendation": decision,
        "approval_reasons": [],
        "blocked_reasons": blocked_reasons,
        "next_safe_action": next_safe_action,
        "operator_review_required": bool(operator_review_required),
        "safety": safety,
        "governance_decision": decision,
        "mode": MODE,
    }
