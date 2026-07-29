"""Accumulate paper-only profitability evidence into a candidate promotion gate.

The accumulator consumes already-sanitized, in-memory period summaries.  It
does not read files, contact a broker, or authorize demo/live execution.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any


MODE = "PAPER_STATISTICAL_EVIDENCE_ACCUMULATION_ONLY"
PACKET_ID = "AIOS_FOREX_PROFIT_LOOP_ACCELERATION_GATE_V1"
READY = "PAPER_STATISTICAL_EVIDENCE_READY_FOR_OWNER_REVIEW"
ACCUMULATING = "PAPER_STATISTICAL_EVIDENCE_ACCUMULATING"
BLOCKED_INVALID = "PAPER_STATISTICAL_EVIDENCE_BLOCKED_INVALID"

DEFAULT_THRESHOLDS = {
    "minimum_periods": 3,
    "minimum_consecutive_profitable_periods": 3,
    "minimum_total_trades": 30,
    "minimum_profit_factor": 1.2,
    "minimum_expectancy_r": 0.0,
    "maximum_drawdown_r": 6.0,
    "minimum_walk_forward_folds": 3,
    "minimum_out_of_sample_folds": 3,
}

NUMERIC_FIELDS = (
    "closed_trades",
    "net_pnl_after_costs",
    "expectancy_r",
    "profit_factor",
    "max_drawdown_r",
    "walk_forward_folds",
    "out_of_sample_folds",
)


def _number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def _thresholds(overrides: Mapping[str, Any] | None) -> tuple[dict[str, float], list[str]]:
    values = dict(DEFAULT_THRESHOLDS)
    errors: list[str] = []
    for name, value in dict(overrides or {}).items():
        if name not in values:
            errors.append(f"unknown_threshold:{name}")
            continue
        parsed = _number(value)
        if parsed is None or parsed < 0:
            errors.append(f"invalid_threshold:{name}")
            continue
        values[name] = parsed
    return values, errors


def _safety() -> dict[str, bool]:
    return {
        "paper_only": True,
        "owner_review_required": True,
        "demo_execution_allowed": False,
        "live_execution_allowed": False,
        "broker_action_allowed": False,
        "credential_access_allowed": False,
        "automatic_candidate_promotion_allowed": False,
    }


def _blocked(errors: list[str], thresholds: Mapping[str, float]) -> dict[str, Any]:
    return {
        "packet_id": PACKET_ID,
        "mode": MODE,
        "classification": BLOCKED_INVALID,
        "ready": False,
        "candidate_id": None,
        "blockers": list(dict.fromkeys(errors)),
        "metrics": {},
        "thresholds": dict(thresholds),
        "next_safe_action": "repair_sanitized_paper_period_evidence",
        "safety": _safety(),
    }


def evaluate_paper_statistical_evidence(
    candidate_id: str,
    periods: Sequence[Mapping[str, Any]] | None,
    thresholds: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Evaluate accumulated after-cost paper evidence for owner review."""
    limits, errors = _thresholds(thresholds)
    if not isinstance(candidate_id, str) or not candidate_id.strip():
        errors.append("missing_candidate_id")
    if not isinstance(periods, Sequence) or isinstance(periods, (str, bytes)):
        errors.append("invalid_periods")
        return _blocked(errors, limits)

    normalized: list[dict[str, float]] = []
    period_ids: set[str] = set()
    for index, period in enumerate(periods):
        if not isinstance(period, Mapping):
            errors.append(f"invalid_period:{index}")
            continue
        period_id = period.get("period_id")
        if not isinstance(period_id, str) or not period_id.strip():
            errors.append(f"missing_period_id:{index}")
        elif period_id in period_ids:
            errors.append(f"duplicate_period_id:{period_id}")
        else:
            period_ids.add(period_id)
        values: dict[str, float] = {}
        for field in NUMERIC_FIELDS:
            parsed = _number(period.get(field))
            if parsed is None:
                errors.append(f"invalid_numeric_field:{index}:{field}")
            else:
                values[field] = parsed
        if period.get("paper_only") is not True:
            errors.append(f"paper_only_not_confirmed:{index}")
        if period.get("sanitized") is not True:
            errors.append(f"sanitized_not_confirmed:{index}")
        if len(values) == len(NUMERIC_FIELDS):
            normalized.append(values)

    if errors:
        return _blocked(errors, limits)

    total_trades = sum(period["closed_trades"] for period in normalized)
    total_net_pnl = sum(period["net_pnl_after_costs"] for period in normalized)
    weighted_expectancy = (
        sum(period["expectancy_r"] * period["closed_trades"] for period in normalized)
        / total_trades
        if total_trades > 0
        else 0.0
    )
    weighted_profit_factor = (
        sum(period["profit_factor"] * period["closed_trades"] for period in normalized)
        / total_trades
        if total_trades > 0
        else 0.0
    )
    consecutive_profitable = 0
    for period in reversed(normalized):
        if period["net_pnl_after_costs"] > 0 and period["expectancy_r"] > 0:
            consecutive_profitable += 1
        else:
            break

    blockers: list[str] = []
    checks = (
        (len(normalized) >= limits["minimum_periods"], "insufficient_periods"),
        (consecutive_profitable >= limits["minimum_consecutive_profitable_periods"], "insufficient_consecutive_profitable_periods"),
        (total_trades >= limits["minimum_total_trades"], "insufficient_total_trades"),
        (total_net_pnl > 0, "net_pnl_after_costs_not_positive"),
        (weighted_expectancy > limits["minimum_expectancy_r"], "expectancy_not_above_threshold"),
        (weighted_profit_factor >= limits["minimum_profit_factor"], "profit_factor_below_threshold"),
        (all(period["max_drawdown_r"] <= limits["maximum_drawdown_r"] for period in normalized), "drawdown_above_threshold"),
        (all(period["walk_forward_folds"] >= limits["minimum_walk_forward_folds"] for period in normalized), "insufficient_walk_forward_folds"),
        (all(period["out_of_sample_folds"] >= limits["minimum_out_of_sample_folds"] for period in normalized), "insufficient_out_of_sample_folds"),
    )
    blockers.extend(reason for passed, reason in checks if not passed)
    ready = not blockers
    return {
        "packet_id": PACKET_ID,
        "mode": MODE,
        "classification": READY if ready else ACCUMULATING,
        "ready": ready,
        "candidate_id": candidate_id.strip(),
        "blockers": blockers,
        "metrics": {
            "period_count": len(normalized),
            "consecutive_profitable_periods": consecutive_profitable,
            "total_trades": total_trades,
            "total_net_pnl_after_costs": round(total_net_pnl, 8),
            "weighted_expectancy_r": round(weighted_expectancy, 8),
            "weighted_profit_factor": round(weighted_profit_factor, 8),
            "maximum_observed_drawdown_r": max((period["max_drawdown_r"] for period in normalized), default=0.0),
        },
        "thresholds": limits,
        "next_safe_action": "owner_review_candidate_evidence" if ready else "continue_paper_evidence_accumulation",
        "safety": _safety(),
    }


def select_next_candidate_for_owner_review(results: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Select deterministically among ready results without authorizing execution."""
    ready = [result for result in results if result.get("ready") is True]
    ranked = sorted(
        ready,
        key=lambda result: (
            -float(result.get("metrics", {}).get("weighted_expectancy_r", 0.0)),
            -float(result.get("metrics", {}).get("total_net_pnl_after_costs", 0.0)),
            str(result.get("candidate_id", "")),
        ),
    )
    selected = ranked[0].get("candidate_id") if ranked else None
    return {
        "selected_candidate_id": selected,
        "owner_review_ready": selected is not None,
        "execution_allowed": False,
        "next_safe_action": "owner_review_candidate_evidence" if selected else "continue_paper_evidence_accumulation",
    }
