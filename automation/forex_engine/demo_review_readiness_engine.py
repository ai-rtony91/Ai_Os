"""Canonical paper-only demo-review readiness engine."""
from __future__ import annotations

from typing import Any
from collections.abc import Mapping

from automation.forex_engine.portfolio_promotion_decision_engine import (
    DEFAULT_MIN_BATCHES,
    DEFAULT_MIN_WINNER_CONSISTENCY,
    run_portfolio_promotion_decision_engine,
)
from automation.forex_engine.portfolio_promotion_decision_engine import (
    DECISION_DEMO_REVIEW_CANDIDATE,
    DECISION_MORE_EVIDENCE_REQUIRED,
    DECISION_PAPER_CONTINUE,
    DECISION_REJECTED,
)
from automation.forex_engine.portfolio_evidence_accumulation_runner import (
    run_portfolio_evidence_accumulation_runner,
)

MODE = "DEMO_REVIEW_READINESS_ENGINE_ONLY"


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
        "demo_review_readiness_engine_only": True,
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


def _has_blocked_evidence(strategy: Mapping[str, Any] | None) -> bool:
    if not isinstance(strategy, Mapping):
        return True
    reasons = strategy.get("blocked_reasons", [])
    if any("negative" in str(item).lower() for item in reasons):
        return True
    if any("unsafe" in str(item).lower() for item in reasons):
        return True
    return not _safe(strategy.get("safety"))


def run_demo_review_readiness_engine(
    *,
    promotion_result: Mapping[str, Any] | None = None,
    accumulation_result: Mapping[str, Any] | None = None,
    evidence_batches: Any = None,
    competition_batches: Any = None,
    strategy_batches: Any = None,
    minimum_batches: int = DEFAULT_MIN_BATCHES,
    winner_consistency_threshold: float = DEFAULT_MIN_WINNER_CONSISTENCY,
) -> dict[str, Any]:
    if promotion_result is None:
        if accumulation_result is None:
            accumulation_result = run_portfolio_evidence_accumulation_runner(
                evidence_batches=evidence_batches,
                competition_batches=competition_batches,
                strategy_batches=strategy_batches,
                minimum_batches=minimum_batches,
                winner_consistency_threshold=winner_consistency_threshold,
            )
        promotion_result = run_portfolio_promotion_decision_engine(
            accumulation_result=accumulation_result,
            minimum_batches=minimum_batches,
            winner_consistency_threshold=winner_consistency_threshold,
        )

    result = dict(promotion_result)
    portfolio_promotion_status = str(result.get("portfolio_promotion_status", ""))
    stable_winner = dict(result.get("stable_winner", {}))
    winner_consistency_rate = float(result.get("winner_consistency_rate", 0.0))
    blocked_reasons = list(result.get("blocked_reasons", []))
    readiness_reasons: list[str] = []
    next_safe_action = str(result.get("next_safe_action", "collect_more_evidence"))

    if not stable_winner:
        blocked_reasons.append("missing_stable_winner")
    if portfolio_promotion_status != DECISION_DEMO_REVIEW_CANDIDATE:
        blocked_reasons.append(f"promotion_status_not_demo_ready:{portfolio_promotion_status or 'UNKNOWN'}")
    if winner_consistency_rate < float(winner_consistency_threshold):
        blocked_reasons.append("winner_consistency_below_threshold")
    if _has_blocked_evidence(stable_winner):
        blocked_reasons.append("unsafe_or_negative_winner_evidence")

    # Remove duplicate blockers while preserving order.
    blocked_reasons = list(dict.fromkeys(str(reason) for reason in blocked_reasons if reason))

    demo_review_ready = (
        portfolio_promotion_status == DECISION_DEMO_REVIEW_CANDIDATE
        and bool(stable_winner)
        and winner_consistency_rate >= float(winner_consistency_threshold)
        and not blocked_reasons
    )

    if demo_review_ready:
        readiness_reasons.append("ready_for_demo_review")
        next_safe_action = "submit_demo_review_packet"
    else:
        if portfolio_promotion_status == DECISION_REJECTED:
            next_safe_action = "address_rejection_reasons"
            readiness_reasons.append("portfolio_rejected")
        elif portfolio_promotion_status == DECISION_MORE_EVIDENCE_REQUIRED or portfolio_promotion_status == DECISION_PAPER_CONTINUE:
            next_safe_action = "collect_more_evidence"
            readiness_reasons.append("collect_more_evidence_before_demo")
        elif blocked_reasons:
            readiness_reasons.append("blocked_by_governance")
        else:
            readiness_reasons.append("generic_not_ready")

    decision_completed = bool(
        result.get("decision_completed", False)
        or bool(stable_winner)
        or demo_review_ready
        or blocked_reasons
    )

    return {
        "readiness_completed": bool(decision_completed),
        "demo_review_ready": bool(demo_review_ready),
        "portfolio_promotion_status": portfolio_promotion_status,
        "stable_winner": stable_winner,
        "readiness_reasons": readiness_reasons,
        "blocked_reasons": blocked_reasons,
        "next_safe_action": next_safe_action,
        "safety": _safety(),
    }
