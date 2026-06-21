"""Demo validation result aggregator for paper-only deterministic decision output."""
from __future__ import annotations

from typing import Any
from collections.abc import Mapping, Sequence

from automation.forex_engine.demo_validation_scorecard import run_demo_validation_scorecard
from automation.forex_engine.portfolio_promotion_decision_engine import (
    DECISION_DEMO_REVIEW_CANDIDATE as PROMOTION_CANDIDATE,
)

MODE = "DEMO_VALIDATION_RESULT_AGGREGATOR"
RECOMMENDATION_DEMO_VALIDATION_PASSED = "DEMO_VALIDATION_PASSED"
RECOMMENDATION_DEMO_VALIDATION_FAILED = "DEMO_VALIDATION_FAILED"
RECOMMENDATION_MORE_EVIDENCE_REQUIRED = "MORE_EVIDENCE_REQUIRED"


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
        "demo_validation_result_aggregator_only": True,
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


def _run_scorecard(*, demo_review_result: Mapping[str, Any] | None = None, **kwargs: Any) -> dict[str, Any]:
    return run_demo_validation_scorecard(demo_review_result=demo_review_result, **kwargs)


def run_demo_validation_result_aggregator(
    *,
    demo_review_result: Mapping[str, Any] | None = None,
    scorecard_result: Mapping[str, Any] | None = None,
    evidence_batches: Any = None,
    competition_batches: Any = None,
    strategy_batches: Any = None,
    minimum_batches: int = 3,
    winner_consistency_threshold: float = 0.67,
) -> dict[str, Any]:
    if scorecard_result is None:
        scorecard = _run_scorecard(
            demo_review_result=demo_review_result,
            evidence_batches=evidence_batches,
            competition_batches=competition_batches,
            strategy_batches=strategy_batches,
            minimum_batches=minimum_batches,
            winner_consistency_threshold=winner_consistency_threshold,
        )
    else:
        scorecard = dict(scorecard_result)

    if demo_review_result is None:
        demo_review_result = dict(scorecard.get("review_result", {}))
    else:
        demo_review_result = dict(demo_review_result)

    blocked_reasons = []
    stable_winner = dict(demo_review_result.get("stable_winner", scorecard.get("stable_winner", {})))
    portfolio_promotion_status = str(demo_review_result.get("portfolio_promotion_status", scorecard.get("portfolio_promotion_status", "")))
    demo_review_ready = bool(demo_review_result.get("demo_review_ready", False))
    scorecard_passed = bool(scorecard.get("scorecard_passed", False))
    scorecard_completed = bool(scorecard.get("scorecard_completed", False))
    demo_validation_score = float(scorecard.get("demo_validation_score", 0.0))
    scorecard_reasons = _as_list(scorecard.get("blocked_reasons", []))

    safety_scan = _safety()
    source_safety = scorecard.get("safety", {})
    safety = dict(safety_scan)
    if isinstance(source_safety, Mapping):
        for key, value in source_safety.items():
            safety[str(key)] = bool(value)

    if not _safe(safety):
        blocked_reasons.append("safety_violation_detected")

    if not demo_review_result:
        blocked_reasons.append("missing_demo_review_result")
        next_safe_action = "provide_demo_review_result"
    elif not demo_review_ready:
        blocked_reasons.append("demo_review_not_ready")
        next_safe_action = "complete_demo_review_readiness"
    elif portfolio_promotion_status != PROMOTION_CANDIDATE:
        blocked_reasons.append(f"portfolio_promotion_status_not_candidate:{portfolio_promotion_status or 'UNKNOWN'}")
        next_safe_action = "collect_more_evidence_for_portfolio_promotion"
    elif not scorecard_completed:
        blocked_reasons.append("scorecard_not_completed")
        next_safe_action = "complete_scorecard"
    elif not scorecard_passed:
        blocked_reasons.append("scorecard_failed")
        next_safe_action = "fix_scorecard_blockers"
    elif not stable_winner:
        blocked_reasons.append("missing_stable_winner")
        next_safe_action = "collect_more_evidence_until_stable_winner"
    elif demo_validation_score <= 0:
        blocked_reasons.append("non_positive_demo_validation_score")
        next_safe_action = "improve_demo_validation_performance"
    else:
        next_safe_action = "approve_demo_validation_for_paper_operator"

    blocked_reasons.extend([str(reason) for reason in scorecard_reasons if reason])
    blocked_reasons = list(dict.fromkeys(str(reason) for reason in blocked_reasons if reason))

    demo_validation_passed = (
        demo_review_ready
        and scorecard_completed
        and scorecard_passed
        and bool(stable_winner)
        and demo_validation_score > 0
        and portfolio_promotion_status == PROMOTION_CANDIDATE
        and _safe(safety)
    )

    if not blocked_reasons:
        promotion_recommendation = RECOMMENDATION_DEMO_VALIDATION_PASSED
    elif "scorecard_failed" in blocked_reasons:
        promotion_recommendation = RECOMMENDATION_DEMO_VALIDATION_FAILED
    elif any(
        reason.startswith("missing")
        or reason.startswith("demo_review_not_ready")
        or reason.startswith("portfolio_promotion_status")
        for reason in blocked_reasons
    ):
        promotion_recommendation = RECOMMENDATION_MORE_EVIDENCE_REQUIRED
    else:
        promotion_recommendation = RECOMMENDATION_DEMO_VALIDATION_FAILED

    if demo_validation_passed:
        promotion_recommendation = RECOMMENDATION_DEMO_VALIDATION_PASSED

    return {
        "aggregation_completed": True,
        "demo_validation_passed": bool(demo_validation_passed),
        "demo_review_ready": bool(demo_review_ready),
        "scorecard_passed": bool(scorecard_passed),
        "stable_winner": stable_winner,
        "portfolio_promotion_status": portfolio_promotion_status,
        "demo_validation_score": float(demo_validation_score),
        "promotion_recommendation": promotion_recommendation,
        "blocked_reasons": blocked_reasons,
        "next_safe_action": next_safe_action,
        "safety": safety,
        **{key: value for key, value in {"_mode": MODE}.items()},
        "mode": MODE,
    }
