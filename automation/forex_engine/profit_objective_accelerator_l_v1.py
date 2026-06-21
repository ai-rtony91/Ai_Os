"""Profitability objective accelerator for governed forex paper/demo readiness."""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

MODE = "FOREX_PROFIT_OBJECTIVE_ACCELERATION_L_V1"

PROMOTION_STATUS_PROFIT_OBJECTIVE_READY = "PROFIT_OBJECTIVE_READY"
PROMOTION_STATUS_CONTINUE_PAPER_VALIDATION = "CONTINUE_PAPER_VALIDATION"
PROMOTION_STATUS_REJECT_NEGATIVE_EXPECTANCY = "REJECT_NEGATIVE_EXPECTANCY"
PROMOTION_STATUS_REJECT_LOW_PROFIT_FACTOR = "REJECT_LOW_PROFIT_FACTOR"
PROMOTION_STATUS_REJECT_EXCESSIVE_DRAWDOWN = "REJECT_EXCESSIVE_DRAWDOWN"
PROMOTION_STATUS_REJECT_INSUFFICIENT_SAMPLE = "REJECT_INSUFFICIENT_SAMPLE"
PROMOTION_STATUS_REJECT_DIRECTION_UNSUPPORTED = "REJECT_DIRECTION_UNSUPPORTED"

DEFAULT_THRESHOLDS: Mapping[str, float] = {
    "minimum_sample_size": 20,
    "minimum_expectancy": 0.0,
    "minimum_profit_factor": 1.25,
    "maximum_drawdown_pct": 10.0,
}

SUPPORTED_DIRECTIONS = {"LONG", "SHORT"}


def _safety() -> dict[str, bool]:
    return {
        "paper_only": True,
        "broker_connected": False,
        "credentials_used": False,
        "network_used": False,
        "order_execution": False,
        "demo_trading": False,
        "live_trading": False,
    }


def _safe_float(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not isinstance(number, float) or number == float("inf") or number == float("-inf"):
        if number != float("inf") and number != float("-inf"):
            return float(number)
        return None
    return number


def _safe_float_or_zero(value: Any) -> float:
    parsed = _safe_float(value)
    return parsed if parsed is not None else 0.0


def _safe_direction(direction: str) -> str:
    return str(direction).strip().upper()


def _consecutive_counts(pnls: Sequence[float]) -> tuple[int, int]:
    longest_win = 0
    longest_loss = 0
    current_win = 0
    current_loss = 0
    for pnl in pnls:
        if pnl > 0:
            current_win += 1
            current_loss = 0
            longest_win = max(longest_win, current_win)
        elif pnl < 0:
            current_loss += 1
            current_win = 0
            longest_loss = max(longest_loss, current_loss)
        else:
            current_win = 0
            current_loss = 0
    return longest_win, longest_loss


def _max_drawdown_pct(pnls: Sequence[float], starting_balance: float = 10000.0) -> float:
    if not pnls:
        return 0.0
    equity = float(starting_balance)
    peak = equity
    max_drawdown_fraction = 0.0
    for pnl in pnls:
        equity += pnl
        if equity > peak:
            peak = equity
        if peak > 0:
            drawdown_fraction = (peak - equity) / peak
            if drawdown_fraction > max_drawdown_fraction:
                max_drawdown_fraction = drawdown_fraction
    return round(max_drawdown_fraction * 100.0, 8)


def _profit_factor(pnls: Sequence[float]) -> float:
    gross_profit = sum(pnl for pnl in pnls if pnl > 0)
    gross_loss = -sum(pnl for pnl in pnls if pnl < 0)
    if gross_loss == 0.0:
        return 999.0 if gross_profit > 0 else 0.0
    return round(gross_profit / gross_loss, 8)


def _expectancy(pnls: Sequence[float]) -> float:
    if not pnls:
        return 0.0
    return round(sum(pnls) / len(pnls), 8)


def _win_rate(pnls: Sequence[float]) -> float:
    if not pnls:
        return 0.0
    winners = len([pnl for pnl in pnls if pnl > 0])
    return round(winners / len(pnls), 8)


@dataclass(frozen=True)
class _CandidateSpec:
    strategy_id: str
    candidate_id: str
    direction: str
    trade_pnl_list: Sequence[float]


def _normalize_candidate(candidate: Mapping[str, Any]) -> _CandidateSpec:
    return _CandidateSpec(
        strategy_id=str(candidate.get("strategy_id", "")).strip(),
        candidate_id=str(candidate.get("candidate_id", "")).strip(),
        direction=_safe_direction(candidate.get("direction", "")),
        trade_pnl_list=[
            _safe_float_or_zero(pnl)
            for pnl in candidate.get("trade_pnl_list", [])
            if _safe_float(pnl) is not None
        ],
    )


def evaluate_profitability_candidate(
    *,
    strategy_id: str,
    candidate_id: str,
    direction: str,
    trade_pnl_list: Sequence[float],
    thresholds: Mapping[str, float] | None = None,
    starting_balance: float = 10000.0,
) -> dict[str, Any]:
    normalized = {
        "strategy_id": str(strategy_id).strip(),
        "candidate_id": str(candidate_id).strip(),
        "direction": _safe_direction(direction),
        "trade_pnl_list": [
            _safe_float_or_zero(pnl)
            for pnl in trade_pnl_list
            if _safe_float(pnl) is not None
        ],
    }
    pnls = [float(pnl) for pnl in normalized["trade_pnl_list"]]
    config = dict(DEFAULT_THRESHOLDS)
    if thresholds:
        config.update(thresholds)

    blocked_reasons: list[str] = []
    if not normalized["strategy_id"]:
        blocked_reasons.append("missing_strategy_id")
    if not normalized["candidate_id"]:
        blocked_reasons.append("missing_candidate_id")
    if normalized["direction"] not in SUPPORTED_DIRECTIONS:
        return {
            "strategy_id": normalized["strategy_id"],
            "candidate_id": normalized["candidate_id"],
            "direction": normalized["direction"],
            "trade_pnl_list": pnls,
            "win_rate": 0.0,
            "expectancy": 0.0,
            "profit_factor": 0.0,
            "max_drawdown": 0.0,
            "consecutive_wins": 0,
            "consecutive_losses": 0,
            "promotion_status": PROMOTION_STATUS_REJECT_DIRECTION_UNSUPPORTED,
            "blocked_reasons": ["unsupported_direction"],
            "blocked": True,
            "safety": _safety(),
            "mode": MODE,
        }

    sample_size = len(pnls)
    expectancy = _expectancy(pnls)
    profit_factor = _profit_factor(pnls)
    max_drawdown = _max_drawdown_pct(pnls, starting_balance=starting_balance)
    consecutive_wins, consecutive_losses = _consecutive_counts(pnls)

    if sample_size < config["minimum_sample_size"]:
        blocked_reasons.append("insufficient_sample")
    if expectancy <= config["minimum_expectancy"]:
        blocked_reasons.append("negative_expectancy")
    if profit_factor < config["minimum_profit_factor"]:
        blocked_reasons.append("low_profit_factor")
    if max_drawdown > config["maximum_drawdown_pct"]:
        blocked_reasons.append("excessive_drawdown")

    if not blocked_reasons:
        promotion_status = PROMOTION_STATUS_PROFIT_OBJECTIVE_READY
        blocked = False
    else:
        blocked = True
        if "insufficient_sample" in blocked_reasons:
            promotion_status = PROMOTION_STATUS_REJECT_INSUFFICIENT_SAMPLE
        elif "negative_expectancy" in blocked_reasons:
            promotion_status = PROMOTION_STATUS_REJECT_NEGATIVE_EXPECTANCY
        elif "low_profit_factor" in blocked_reasons:
            promotion_status = PROMOTION_STATUS_REJECT_LOW_PROFIT_FACTOR
        elif "excessive_drawdown" in blocked_reasons:
            promotion_status = PROMOTION_STATUS_REJECT_EXCESSIVE_DRAWDOWN
        else:
            promotion_status = PROMOTION_STATUS_CONTINUE_PAPER_VALIDATION

    return {
        "strategy_id": normalized["strategy_id"],
        "candidate_id": normalized["candidate_id"],
        "direction": normalized["direction"],
        "trade_pnl_list": pnls,
        "win_rate": _win_rate(pnls),
        "expectancy": expectancy,
        "profit_factor": profit_factor,
        "max_drawdown": max_drawdown,
        "consecutive_wins": consecutive_wins,
        "consecutive_losses": consecutive_losses,
        "sample_size": sample_size,
        "promotion_status": promotion_status,
        "blocked": blocked,
        "blocked_reasons": blocked_reasons,
        "next_safe_action": (
            "advance_governed_paper_demo_intent"
            if not blocked
            else PROMOTION_STATUS_CONTINUE_PAPER_VALIDATION
        ),
        "safety": _safety(),
        "mode": MODE,
    }


def rank_candidates(
    *,
    candidate_evals: list[dict[str, Any]],
) -> dict[str, Any]:
    ranked_candidates: list[dict[str, Any]] = []
    for candidate in candidate_evals:
        if not isinstance(candidate, Mapping):
            ranked_candidates.append(
                {
                    "strategy_id": "",
                    "candidate_id": "",
                    "direction": "",
                    "promotion_status": PROMOTION_STATUS_CONTINUE_PAPER_VALIDATION,
                    "blocked_reasons": ["malformed_candidate"],
                    "expected_key": "",
                    "score": 0.0,
                    "safe": False,
                }
            )
            continue
        normalized = evaluate_profitability_candidate(
            strategy_id=str(candidate.get("strategy_id", "")),
            candidate_id=str(candidate.get("candidate_id", "")),
            direction=str(candidate.get("direction", "")),
            trade_pnl_list=candidate.get("trade_pnl_list", []),
            thresholds=candidate.get("thresholds"),
        )
        normalized["safe"] = normalized["promotion_status"] == PROMOTION_STATUS_PROFIT_OBJECTIVE_READY
        normalized["score"] = (
            (normalized["expectancy"] * 1000.0)
            + (normalized["profit_factor"] * 100.0)
            - (normalized["max_drawdown"] * 10.0)
            + (normalized["win_rate"] * 100.0)
        )
        ranked_candidates.append(normalized)

    def _sort_key(item: Mapping[str, Any]):
        return (
            0 if item.get("safe") else 1,
            -item.get("expectancy", 0.0),
            -item.get("profit_factor", 0.0),
            item.get("max_drawdown", 0.0),
            -item.get("consecutive_wins", 0),
            item.get("consecutive_losses", 0),
            item.get("direction", ""),
            item.get("strategy_id", ""),
            item.get("candidate_id", ""),
            item.get("score", 0.0),
        )

    ranked = sorted(ranked_candidates, key=_sort_key)
    top = ranked[0] if ranked else {}
    ready_set = [item for item in ranked if item.get("safe")]
    if not ranked:
        best_candidate = {}
        next_status = PROMOTION_STATUS_CONTINUE_PAPER_VALIDATION
    elif ready_set:
        best_candidate = ready_set[0]
        next_status = PROMOTION_STATUS_PROFIT_OBJECTIVE_READY
    else:
        best_candidate = ranked[0]
        next_status = best_candidate.get("promotion_status", PROMOTION_STATUS_CONTINUE_PAPER_VALIDATION)

    # Both directions must be representable for complete directional readiness.
    long_present = any(item.get("direction") == "LONG" for item in ranked_candidates)
    short_present = any(item.get("direction") == "SHORT" for item in ranked_candidates)
    directionally_balanced = long_present and short_present

    return {
        "ranked_candidates": ranked,
        "best_candidate": best_candidate,
        "promotion_status": next_status,
        "candidates_ready_for_promotion": ready_set,
        "directionally_balanced": directionally_balanced,
        "next_safe_action": (
            "select_best_candidate_for_governed_paper_or_demo"
            if ready_set
            else "continue_paper_validation_and_collect_more_evidence"
        ),
        "directional_readiness": {
            "supports_long": long_present,
            "supports_short": short_present,
            "both_supported": directionally_balanced,
        },
        "safety": _safety(),
        "mode": MODE,
    }


def evaluate_candidate_pool(
    *,
    candidates: Sequence[Mapping[str, Any]],
    thresholds: Mapping[str, float] | None = None,
) -> dict[str, Any]:
    evaluated = [
        {
            **evaluate_profitability_candidate(
                strategy_id=c.get("strategy_id", ""),
                candidate_id=c.get("candidate_id", ""),
                direction=c.get("direction", ""),
                trade_pnl_list=c.get("trade_pnl_list", []),
                thresholds=thresholds,
            ),
            "strategy_identity": f"{c.get('strategy_id', '')}:{c.get('candidate_id', '')}",
        }
        for c in candidates
        if isinstance(c, Mapping)
    ]
    ranked_payload = rank_candidates(candidate_evals=[{
        "strategy_id": item["strategy_id"],
        "candidate_id": item["candidate_id"],
        "direction": item["direction"],
        "trade_pnl_list": item["trade_pnl_list"],
        "thresholds": thresholds,
    } for item in evaluated])

    return {
        "candidate_results": evaluated,
        "ranked_payload": ranked_payload,
        "best_candidate": ranked_payload.get("best_candidate", {}),
        "promotion_status": ranked_payload.get("promotion_status", PROMOTION_STATUS_CONTINUE_PAPER_VALIDATION),
        "directional_readiness": ranked_payload.get("directional_readiness", {}),
        "safety": _safety(),
        "mode": MODE,
    }
