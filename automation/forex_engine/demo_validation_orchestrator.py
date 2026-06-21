"""Paper-only demo validation orchestrator."""
from __future__ import annotations

from typing import Any
from collections.abc import Mapping

from automation.forex_engine.demo_review_readiness_engine import (
    DECISION_DEMO_REVIEW_CANDIDATE,
    run_demo_review_readiness_engine,
)

MODE = "DEMO_VALIDATION_ORCHESTRATOR"


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
        "demo_validation_orchestrator_only": True,
        "broker_access": False,
        "credentials_access": False,
        "network_access": False,
        "live_trading_active": False,
        "demo_execution_active": False,
        "capital_allocation_modified": False,
    }


def _safe_execution_flags(flags: Any) -> bool:
    safety = flags if isinstance(flags, Mapping) else {}
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


def _has_unsafe_winner_evidence(strategy: Any) -> bool:
    if not isinstance(strategy, Mapping):
        return True
    if any("unsafe" in str(item).lower() for item in strategy.get("blocked_reasons", [])):
        return True
    if any("negative" in str(item).lower() for item in strategy.get("blocked_reasons", [])):
        return True
    return not _safe_execution_flags(strategy.get("safety"))


def _build_validation_plan(stable_winner: Mapping[str, Any], consistency: float) -> dict[str, Any]:
    strategy_name = str(stable_winner.get("strategy_name", "UNSET"))
    strategy_version = str(stable_winner.get("strategy_version", "UNKNOWN"))

    return {
        "strategy_name": strategy_name,
        "strategy_version": strategy_version,
        "validation_stage": "PAPER_DEMO_VALIDATION",
        "required_observations": [
            "paper_trade_execution_quality",
            "slippage_and_spread_review",
            "drawdown_stability_review",
            "winner_consistency_retest",
        ],
        "required_trade_count": 30,
        "required_evidence_fields": [
            "strategy_name",
            "strategy_version",
            "winner_consistency_rate",
            "blocked_reasons",
            "safety",
        ],
        "risk_controls_required": [
            "paper_only",
            "safety_gates",
            "winner_consistency_threshold",
            "operator_approval_required",
        ],
        "operator_approval_required": True,
        "broker_connection_required_later": False,
        "credentials_required_later": False,
        "demo_execution_active": False,
        "winner_consistency_rate": float(consistency),
        "safe_to_run": bool(_safe_execution_flags(stable_winner.get("safety"))),
    }


def run_demo_validation_orchestrator(
    *,
    demo_review_result: Mapping[str, Any] | None = None,
    evidence_batches: Any = None,
    competition_batches: Any = None,
    strategy_batches: Any = None,
    minimum_batches: int = 3,
    winner_consistency_threshold: float = 0.67,
) -> dict[str, Any]:
    if demo_review_result is None:
        demo_review_result = run_demo_review_readiness_engine(
            evidence_batches=evidence_batches,
            competition_batches=competition_batches,
            strategy_batches=strategy_batches,
            minimum_batches=minimum_batches,
            winner_consistency_threshold=winner_consistency_threshold,
        )

    review = dict(demo_review_result)
    demo_review_ready = bool(review.get("demo_review_ready", False))
    stable_winner = dict(review.get("stable_winner", {}))
    blocked_reasons = list(review.get("blocked_reasons", []))
    winner_consistency_rate = float(review.get("winner_consistency_rate", 0.0))
    next_safe_action = str(review.get("next_safe_action", "collect_more_evidence"))

    if not demo_review_ready:
        blocked_reasons.append("demo_review_not_ready")

    if not stable_winner:
        blocked_reasons.append("missing_stable_winner")

    if _has_unsafe_winner_evidence(stable_winner):
        blocked_reasons.append("unsafe_or_negative_winner_evidence")

    if review.get("portfolio_promotion_status") != DECISION_DEMO_REVIEW_CANDIDATE:
        blocked_reasons.append("demo_review_status_not_candidate")

    for reason in ("broker_access", "credentials_access", "network_access", "live_trading_active", "demo_execution_active", "capital_allocation_modified"):
        if _to_bool(review.get("safety", {}).get(reason)) is True:
            blocked_reasons.append(f"safety_flag_{reason}_enabled")

    blocked_reasons = list(dict.fromkeys(str(reason) for reason in blocked_reasons if reason))

    demo_validation_ready = (
        bool(stable_winner)
        and demo_review_ready
        and not blocked_reasons
        and review.get("portfolio_promotion_status") == DECISION_DEMO_REVIEW_CANDIDATE
    )
    validation_plan = _build_validation_plan(stable_winner, winner_consistency_rate) if demo_validation_ready else {
        "strategy_name": str(stable_winner.get("strategy_name", "UNSET")),
        "strategy_version": str(stable_winner.get("strategy_version", "UNKNOWN")),
        "validation_stage": "PAPER_DEMO_VALIDATION",
        "required_observations": [
            "resolve_demo_readiness_blockers_first",
        ],
        "required_trade_count": 0,
        "required_evidence_fields": [
            "strategy_name",
            "strategy_version",
            "blocked_reasons",
            "safety",
        ],
        "risk_controls_required": [
            "paper_only",
            "safety_gates",
            "operator_approval_required",
        ],
        "operator_approval_required": True,
        "broker_connection_required_later": False,
        "credentials_required_later": False,
        "demo_execution_active": False,
        "winner_consistency_rate": winner_consistency_rate,
        "safe_to_run": False,
    }

    if demo_validation_ready:
        next_safe_action = "run_paper_demo_validation_cycle"
    elif "demo_review_not_ready" in blocked_reasons:
        next_safe_action = "complete_demo_review_readiness"
    elif "unsafe_or_negative_winner_evidence" in blocked_reasons:
        next_safe_action = "fix_unsafe_winner_evidence_before_validation"
    elif "missing_stable_winner" in blocked_reasons:
        next_safe_action = "collect_more_evidence_until_stable_winner"
    else:
        next_safe_action = "resolve_demo_validation_blockers"

    if not demo_validation_ready and _to_bool(review.get("readiness_completed")) is not False:
        next_safe_action = str(next_safe_action)

    return {
        "orchestration_completed": bool(review.get("readiness_completed", False) or blocked_reasons),
        "demo_validation_ready": bool(demo_validation_ready),
        "demo_review_ready": bool(demo_review_ready),
        "validation_plan": dict(validation_plan),
        "stable_winner": stable_winner,
        "blocked_reasons": blocked_reasons,
        "next_safe_action": next_safe_action,
        "safety": _safety(),
        "mode": MODE,
    }
