"""Canonical paper-only portfolio promotion decision engine."""
from __future__ import annotations

from typing import Any
from collections.abc import Mapping

from automation.forex_engine.portfolio_evidence_accumulation_runner import (
    DEFAULT_MIN_BATCHES,
    DEFAULT_MIN_WINNER_CONSISTENCY,
    run_portfolio_evidence_accumulation_runner,
)

MODE = "PORTFOLIO_PROMOTION_DECISION_ENGINE_ONLY"

DECISION_PAPER_CONTINUE = "PORTFOLIO_PAPER_CONTINUE"
DECISION_MORE_EVIDENCE_REQUIRED = "PORTFOLIO_MORE_EVIDENCE_REQUIRED"
DECISION_DEMO_REVIEW_CANDIDATE = "PORTFOLIO_DEMO_REVIEW_CANDIDATE"
DECISION_REJECTED = "PORTFOLIO_REJECTED"


def _safety() -> dict[str, bool]:
    return {
        "paper_only": True,
        "portfolio_promotion_decision_engine_only": True,
        "broker_access": False,
        "credentials_access": False,
        "network_access": False,
        "live_trading_active": False,
        "demo_execution_active": False,
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


def _has_blocked_evidence(strategy: Mapping[str, Any] | None) -> bool:
    if not isinstance(strategy, Mapping):
        return True
    blocked = strategy.get("blocked_reasons", [])
    if any("negative" in str(reason) for reason in blocked):
        return True
    if any("unsafe" in str(reason) for reason in blocked):
        return True
    return not _safe(strategy.get("safety"))


def run_portfolio_promotion_decision_engine(
    *,
    accumulation_result: Mapping[str, Any] | None = None,
    evidence_batches: Any = None,
    competition_batches: Any = None,
    strategy_batches: Any = None,
    minimum_batches: int = DEFAULT_MIN_BATCHES,
    winner_consistency_threshold: float = DEFAULT_MIN_WINNER_CONSISTENCY,
) -> dict[str, Any]:
    if accumulation_result is None:
        accumulation = run_portfolio_evidence_accumulation_runner(
            evidence_batches=evidence_batches,
            competition_batches=competition_batches,
            strategy_batches=strategy_batches,
            minimum_batches=minimum_batches,
            winner_consistency_threshold=winner_consistency_threshold,
        )
    else:
        accumulation = dict(accumulation_result)

    stable_winner = dict(accumulation.get("stable_winner", {}))
    winner_consistency_rate = float(accumulation.get("winner_consistency_rate", 0.0))
    blocked_reasons = list(accumulation.get("blocked_reasons", []))
    next_safe_action = str(accumulation.get("next_safe_action", "collect_more_evidence"))
    promotion_reasons: list[str] = []

    no_safe_winner = not bool(stable_winner)
    if no_safe_winner:
        blocked_reasons.append("no_safe_winner")

    winner_blocked = _has_blocked_evidence(stable_winner)
    accumulation_ready = bool(accumulation.get("portfolio_ready", False))
    has_blocked_flags = any(
        reason in blocked_reasons
        for reason in (
            "winner_consistency_below_threshold",
            "insufficient_batches",
            "all_batches_failed",
            "no_stable_winner",
            "no_safe_strategies_remain",
        )
    )

    if no_safe_winner:
        portfolio_promotion_status = DECISION_REJECTED
        next_safe_action = "remove_unsafe_candidates_and_retry"
        promotion_reasons.append("no_safe_winner")
    elif not blocked_reasons:
        if winner_blocked:
            portfolio_promotion_status = DECISION_REJECTED
            next_safe_action = "resolve_blocked_winner"
            promotion_reasons.append("unsafe_or_negative_evidence")
        elif accumulation_ready and winner_consistency_rate >= float(winner_consistency_threshold):
            portfolio_promotion_status = DECISION_DEMO_REVIEW_CANDIDATE
            next_safe_action = "run_demo_readiness_review"
            promotion_reasons.append("winner_is_stable_and_safe")
        elif winner_consistency_rate >= float(winner_consistency_threshold):
            portfolio_promotion_status = DECISION_PAPER_CONTINUE
            next_safe_action = "collect_more_evidence_or_transition_to_paper_monitor"
            promotion_reasons.append("stable_winner_but_portfolio_not_ready")
        else:
            portfolio_promotion_status = DECISION_MORE_EVIDENCE_REQUIRED
            next_safe_action = "collect_additional_evidence_batches"
    else:
        if has_blocked_flags:
            portfolio_promotion_status = DECISION_MORE_EVIDENCE_REQUIRED
            next_safe_action = "collect_additional_evidence_batches"
            if winner_consistency_rate >= float(winner_consistency_threshold):
                promotion_reasons.append("winner_consistency_blocked_by_accumulation")
        elif winner_blocked:
            portfolio_promotion_status = DECISION_REJECTED
            next_safe_action = "resolve_blocked_evidence"
            promotion_reasons.append("unsafe_or_negative_evidence")
        else:
            portfolio_promotion_status = DECISION_MORE_EVIDENCE_REQUIRED
            promotion_reasons.append("blocked_reasons_present")

    if stable_winner and winner_blocked:
        portfolio_promotion_status = DECISION_REJECTED
        promotion_reasons.append("winner_is_blocked")
    if portfolio_promotion_status == DECISION_DEMO_REVIEW_CANDIDATE and not stable_winner:
        portfolio_promotion_status = DECISION_REJECTED

    blocked_reasons = list(dict.fromkeys(str(reason) for reason in blocked_reasons if reason))
    promotion_reasons = list(dict.fromkeys(promotion_reasons))

    return {
        "decision_completed": bool(stable_winner and accumulation.get("accumulation_completed", False)),
        "portfolio_promotion_status": portfolio_promotion_status,
        "demo_review_candidate": bool(portfolio_promotion_status == DECISION_DEMO_REVIEW_CANDIDATE),
        "stable_winner": stable_winner,
        "winner_consistency_rate": winner_consistency_rate,
        "blocked_reasons": blocked_reasons,
        "promotion_reasons": promotion_reasons,
        "next_safe_action": next_safe_action,
        "safety": _safety(),
    }
