"""Deterministic demo validation scorecard."""
from __future__ import annotations

from typing import Any
from collections.abc import Mapping, Sequence

from automation.forex_engine.demo_validation_orchestrator import (
    run_demo_validation_orchestrator,
)

DECISION_SCORE = "DEMO_VALIDATION_SCORECARD_EVALUATED"

MODE = "DEMO_VALIDATION_SCORECARD_ENGINE_ONLY"
DECISION_SCORECARD_PASSED = "DEMO_VALIDATION_SCORECARD_PASSED"
DECISION_SCORECARD_FAILED = "DEMO_VALIDATION_SCORECARD_FAILED"
MINIMUM_DEMO_VALIDATION_SCORE = 0.0


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
        "demo_validation_scorecard_only": True,
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


def _safe_payload(payload: Any) -> dict[str, Any]:
    if isinstance(payload, Mapping):
        return {str(key): value for key, value in payload.items()}
    return {}


def _normalized_reasons(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [str(item) for item in value if str(item)]


def _compute_demo_validation_score(
    *,
    demo_review_ready: bool,
    portfolio_promotion_status: str,
    stable_winner: Mapping[str, Any],
    winner_consistency_rate: float,
    blocked_reasons: list[str],
    safety: Mapping[str, Any],
) -> tuple[float, list[str]]:
    reasons = list(blocked_reasons)
    consistency = float(winner_consistency_rate)
    score = 100.0 * max(0.0, min(consistency, 1.0))
    if demo_review_ready:
        score += 10.0
    if portfolio_promotion_status:
        score += 10.0
    if stable_winner:
        score += 15.0
    if _safe(safety):
        score += 5.0
    for reason in blocked_reasons:
        lower = reason.lower()
        if "insufficient" in lower:
            score -= 20.0
        if "unsafe" in lower or "blocked" in lower or "safety" in lower:
            score -= 12.5
    score = round(score, 3)
    return score, reasons


def run_demo_validation_scorecard(
    *,
    demo_review_result: Mapping[str, Any] | None = None,
    orchestrator_result: Mapping[str, Any] | None = None,
    scorecard_input: Mapping[str, Any] | None = None,
    evidence_batches: Any = None,
    competition_batches: Any = None,
    strategy_batches: Any = None,
    minimum_batches: int = 3,
    winner_consistency_threshold: float = 0.67,
) -> dict[str, Any]:
    if scorecard_input is not None:
        review = dict(scorecard_input)
    elif orchestrator_result is not None:
        review = dict(orchestrator_result)
    elif demo_review_result is not None:
        review = {
            "orchestration_completed": bool(demo_review_result),
            "demo_review_ready": bool(demo_review_result.get("demo_review_ready", False)),
            "portfolio_promotion_status": str(demo_review_result.get("portfolio_promotion_status", "")),
            "stable_winner": dict(demo_review_result.get("stable_winner", {})),
            "winner_consistency_rate": float(demo_review_result.get("winner_consistency_rate", 0.0)),
            "blocked_reasons": _normalized_reasons(demo_review_result.get("blocked_reasons")),
            "safety": dict(demo_review_result.get("safety", {})),
            "next_safe_action": str(demo_review_result.get("next_safe_action", "collect_more_evidence")),
            "mode": demo_review_result.get("mode", ""),
            "aggregation_completed": True,
        }
    else:
        orchestrator = run_demo_validation_orchestrator(
            evidence_batches=evidence_batches,
            competition_batches=competition_batches,
            strategy_batches=strategy_batches,
            minimum_batches=minimum_batches,
            winner_consistency_threshold=winner_consistency_threshold,
        )
        review = dict(orchestrator)

    demo_review_ready = bool(review.get("demo_review_ready", False))
    portfolio_promotion_status = str(review.get("portfolio_promotion_status", ""))
    stable_winner = dict(review.get("stable_winner", {}))
    winner_consistency_rate = float(review.get("winner_consistency_rate", review.get("winner_consistency", 0.0)))
    blocked_reasons = _normalized_reasons(review.get("blocked_reasons"))
    safety = _safe_payload(review.get("safety", {}))

    if not _safe(safety):
        blocked_reasons.append("safety_violation_detected")

    blocked_reasons = list(dict.fromkeys(str(reason) for reason in blocked_reasons if reason))

    demo_validation_score, blocked_reasons = _compute_demo_validation_score(
        demo_review_ready=demo_review_ready,
        portfolio_promotion_status=portfolio_promotion_status,
        stable_winner=stable_winner,
        winner_consistency_rate=winner_consistency_rate,
        blocked_reasons=blocked_reasons,
        safety=safety,
    )

    scorecard_passed = (
        bool(stable_winner)
        and demo_review_ready
        and demo_validation_score > MINIMUM_DEMO_VALIDATION_SCORE
        and portfolio_promotion_status == "PORTFOLIO_DEMO_REVIEW_CANDIDATE"
        and _safe(safety)
    )

    if scorecard_passed:
        blocked_reasons = [reason for reason in blocked_reasons if reason != "safety_violation_detected"]
        decision = DECISION_SCORECARD_PASSED
        next_safe_action = "proceed_to_demo_validation_aggregation"
    else:
        decision = DECISION_SCORECARD_FAILED
        if not stable_winner:
            next_safe_action = "collect_more_evidence_until_stable_winner"
        elif not demo_review_ready:
            next_safe_action = "complete_demo_review_readiness"
        elif portfolio_promotion_status != "PORTFOLIO_DEMO_REVIEW_CANDIDATE":
            next_safe_action = "resolve_promotion_recommendation_first"
        elif demo_validation_score <= MINIMUM_DEMO_VALIDATION_SCORE:
            next_safe_action = "rebuild_demo_validation_scorecard_with_evidence"
        else:
            next_safe_action = "resolve_demo_validation_blockers"

    scorecard_decision = (
        DECISION_SCORE
    )

    return {
        "scorecard_completed": bool(stable_winner) or bool(review.get("orchestration_completed", False)) or bool(review),
        "demo_validation_score": float(demo_validation_score),
        "scorecard_passed": bool(scorecard_passed),
        "scorecard_recommendation": str(scorecard_decision),
        "stable_winner": stable_winner,
        "portfolio_promotion_status": portfolio_promotion_status,
        "portfolio_promotion_status_is_candidate": portfolio_promotion_status
        == "PORTFOLIO_DEMO_REVIEW_CANDIDATE",
        "demo_review_ready": demo_review_ready,
        "winner_consistency_rate": float(winner_consistency_rate),
        "decision": decision,
        "blocked_reasons": blocked_reasons,
        "next_safe_action": next_safe_action,
        "safety": _safety() if not safety else {**_safety(), **{str(k): bool(v) for k, v in safety.items()}},
        "mode": MODE,
    }
