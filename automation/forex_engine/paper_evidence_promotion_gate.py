"""Paper evidence promotion gate for demo-validation candidacy."""
from __future__ import annotations

from typing import Any, Mapping

DECISION_PAPER_CONTINUE = "PAPER_CONTINUE"
DECISION_MORE_EVIDENCE_REQUIRED = "MORE_EVIDENCE_REQUIRED"
DECISION_DEMO_CANDIDATE = "DEMO_CANDIDATE"
DECISION_REJECTED = "REJECTED"

_BLOCK_REASON_ORDER = (
    "missing_profitability_evidence",
    "missing_evidence",
    "evidence_quality_failed",
    "risk_quality_failed",
    "insufficient_sample_size",
    "negative_expectancy",
    "negative_expectancy_r",
    "profit_factor_below_threshold",
    "excessive_drawdown",
)


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    return default


def _ordered_unique(reasons: list[str]) -> list[str]:
    seen: set[str] = set()
    unique = [reason for reason in reasons if not (reason in seen or seen.add(reason))]
    return sorted(unique, key=lambda reason: _BLOCK_REASON_ORDER.index(reason) if reason in _BLOCK_REASON_ORDER else len(_BLOCK_REASON_ORDER))


def _safety() -> dict[str, bool]:
    return {
        "paper_only": True,
        "demo_review_only": True,
        "live_trading_allowed": False,
        "broker_execution_allowed": False,
        "credentials_allowed": False,
        "network_access_allowed": False,
        "capital_allocation_modified": False,
        "real_orders_allowed": False,
    }


def evaluate_paper_evidence_promotion(
    profitability_result: Mapping[str, Any] | None,
    limits: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Decide whether paper profitability evidence can become a demo candidate."""
    caps = {
        "minimum_profit_factor": 1.2,
        "maximum_drawdown": 500.0,
        "minimum_expectancy_per_trade": 0.0,
        "minimum_expectancy_r": 0.0,
        **dict(limits or {}),
    }
    if not isinstance(profitability_result, Mapping):
        blocked_reasons = ["missing_profitability_evidence"]
        return {
            "allowed": False,
            "decision": DECISION_MORE_EVIDENCE_REQUIRED,
            "promotion_status": DECISION_MORE_EVIDENCE_REQUIRED,
            "blocked_reasons": blocked_reasons,
            "promotion_reasons": [],
            "next_safe_action": "continue_paper_trading_collect_more_evidence",
            "demo_candidate": False,
            "requires_more_evidence": True,
            "rejected": False,
            "safety": _safety(),
        }

    existing_reasons = [str(reason) for reason in profitability_result.get("blocked_reasons", []) if reason]
    blocked_reasons: list[str] = list(existing_reasons)

    profitability_ready = _safe_bool(profitability_result.get("profitability_ready"))
    sample_size_met = _safe_bool(profitability_result.get("sample_size_met"))
    risk_quality_passed = _safe_bool(profitability_result.get("risk_quality_passed"))
    evidence_quality_passed = _safe_bool(profitability_result.get("evidence_quality_passed"))
    expectancy_per_trade = _safe_float(profitability_result.get("expectancy_per_trade"))
    expectancy_r = _safe_float(profitability_result.get("expectancy_r"))
    profit_factor = _safe_float(profitability_result.get("profit_factor"))
    max_drawdown = _safe_float(profitability_result.get("max_drawdown"))

    if "missing_ledger_evidence" in existing_reasons or "missing_replay_evidence" in existing_reasons:
        blocked_reasons.append("missing_evidence")
    if not evidence_quality_passed:
        blocked_reasons.append("evidence_quality_failed")
    if not risk_quality_passed:
        blocked_reasons.append("risk_quality_failed")
    if not sample_size_met:
        blocked_reasons.append("insufficient_sample_size")
    if expectancy_per_trade <= _safe_float(caps["minimum_expectancy_per_trade"]):
        blocked_reasons.append("negative_expectancy")
    if expectancy_r <= _safe_float(caps["minimum_expectancy_r"]):
        blocked_reasons.append("negative_expectancy_r")
    if profit_factor < _safe_float(caps["minimum_profit_factor"]):
        blocked_reasons.append("profit_factor_below_threshold")
    if max_drawdown > _safe_float(caps["maximum_drawdown"]):
        blocked_reasons.append("excessive_drawdown")

    blocked_reasons = _ordered_unique(blocked_reasons)
    demo_candidate = (
        profitability_ready
        and sample_size_met
        and risk_quality_passed
        and evidence_quality_passed
        and expectancy_per_trade > _safe_float(caps["minimum_expectancy_per_trade"])
        and expectancy_r > _safe_float(caps["minimum_expectancy_r"])
        and profit_factor >= _safe_float(caps["minimum_profit_factor"])
        and max_drawdown <= _safe_float(caps["maximum_drawdown"])
        and not blocked_reasons
    )

    rejection_reasons = {"negative_expectancy", "negative_expectancy_r", "profit_factor_below_threshold", "excessive_drawdown", "risk_quality_failed"}
    rejected = any(reason in rejection_reasons for reason in blocked_reasons) and not any(
        reason in {"insufficient_sample_size", "missing_evidence", "missing_profitability_evidence"} for reason in blocked_reasons
    )
    requires_more_evidence = not demo_candidate and not rejected
    decision = DECISION_DEMO_CANDIDATE if demo_candidate else DECISION_REJECTED if rejected else DECISION_MORE_EVIDENCE_REQUIRED
    if not demo_candidate and not blocked_reasons:
        decision = DECISION_PAPER_CONTINUE
        requires_more_evidence = True

    promotion_reasons = []
    if demo_candidate:
        promotion_reasons = [
            "positive_expectancy",
            "acceptable_drawdown",
            "acceptable_profit_factor",
            "sample_size_met",
            "evidence_quality_passed",
            "risk_quality_passed",
        ]

    return {
        "allowed": demo_candidate,
        "decision": decision,
        "promotion_status": decision,
        "blocked_reasons": blocked_reasons,
        "promotion_reasons": promotion_reasons,
        "next_safe_action": "review_for_demo_validation" if demo_candidate else "continue_paper_trading_collect_more_evidence" if requires_more_evidence else "reject_strategy_or_rework_edge",
        "demo_candidate": demo_candidate,
        "requires_more_evidence": requires_more_evidence,
        "rejected": rejected,
        "safety": _safety(),
    }
