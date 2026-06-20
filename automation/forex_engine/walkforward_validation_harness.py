"""Walk-forward validation harness for repeatable paper strategy evidence."""
from __future__ import annotations

import math
from typing import Any, Mapping

from automation.forex_engine.strategy_evaluation_harness import evaluate_strategy

MODE = "WALKFORWARD_VALIDATION_HARNESS_ONLY"


def _safety() -> dict[str, bool]:
    return {
        "paper_only": True,
        "walkforward_validation_only": True,
        "broker_access": False,
        "credential_access": False,
        "network_access": False,
        "live_trading_active": False,
        "demo_execution_active": False,
        "capital_allocation_modified": False,
    }


def _finite_float(value: Any, default: float = 0.0) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return default
    return round(result, 8) if math.isfinite(result) else default


def _as_windows(window_trade_outcomes: Any) -> list[list[Any]]:
    if not isinstance(window_trade_outcomes, list):
        return []
    windows: list[list[Any]] = []
    for window in window_trade_outcomes:
        if isinstance(window, list):
            windows.append(window)
        else:
            windows.append([window])
    return windows


def _window_candidates(window: list[Any], window_number: int) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for index, outcome in enumerate(window, start=1):
        if isinstance(outcome, Mapping):
            candidate = dict(outcome)
            if "trade_id" not in candidate:
                candidate["trade_id"] = f"wf-{window_number:02d}-trade-{index:04d}"
            candidates.append(candidate)
        else:
            candidates.append(
                {
                    "trade_id": f"wf-{window_number:02d}-trade-{index:04d}",
                    "symbol": "EURUSD",
                    "direction": "buy",
                    "entry": 1.1,
                    "stop": 1.09,
                    "target": 1.12,
                    "risk_percent": 1.0,
                    "spread": 0.0001,
                    "realized_pl": outcome,
                    "timestamp": "2026-01-01T00:00:00Z",
                }
            )
    return candidates


def _ordered_unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result


def _window_passed(window_result: Mapping[str, Any]) -> bool:
    profitability = window_result.get("profitability_result") if isinstance(window_result.get("profitability_result"), Mapping) else {}
    return (
        bool(window_result.get("demo_candidate"))
        and _finite_float(profitability.get("expectancy_per_trade")) > 0
        and bool(profitability.get("evidence_quality_passed"))
        and bool(profitability.get("risk_quality_passed"))
    )


def _aggregate_metrics(window_results: list[dict[str, Any]]) -> dict[str, float | int]:
    total_trades = 0
    total_pnl = 0.0
    gross_profit = 0.0
    gross_loss = 0.0
    max_drawdown = 0.0
    for result in window_results:
        profitability = result.get("profitability_result", {})
        metrics = profitability.get("metrics", {}) if isinstance(profitability, Mapping) and isinstance(profitability.get("metrics"), Mapping) else {}
        trades = int(metrics.get("total_trades", result.get("total_trades", 0)) or 0)
        total_trades += trades
        total_pnl = round(total_pnl + (_finite_float(profitability.get("expectancy_per_trade")) * trades), 8)
        gross_profit = round(gross_profit + _finite_float(metrics.get("gross_profit")), 8)
        gross_loss = round(gross_loss + _finite_float(metrics.get("gross_loss")), 8)
        max_drawdown = max(max_drawdown, _finite_float(profitability.get("max_drawdown")))
    return {
        "total_trades": total_trades,
        "aggregate_expectancy": round(total_pnl / total_trades, 8) if total_trades else 0.0,
        "aggregate_profit_factor": round(gross_profit / gross_loss, 8) if gross_loss > 0 else (999.0 if gross_profit > 0 else 0.0),
        "aggregate_drawdown": round(max_drawdown, 8),
    }


def validate_walkforward_strategy(
    strategy_name: str,
    strategy_version: str = "v1",
    validation_windows: int | list[Any] | None = None,
    window_trade_outcomes: list[Any] | None = None,
    *,
    minimum_windows: int = 2,
    maximum_drawdown: float = 500.0,
) -> dict[str, Any]:
    """Evaluate strategy repeatability across sequential paper evidence windows."""
    windows = _as_windows(window_trade_outcomes)
    if isinstance(validation_windows, int) and validation_windows > len(windows):
        windows.extend([[] for _ in range(validation_windows - len(windows))])

    window_results: list[dict[str, Any]] = []
    blocked_reasons: list[str] = []
    for index, window in enumerate(windows, start=1):
        window_result = evaluate_strategy(
            strategy_name,
            strategy_version,
            _window_candidates(window, index),
            session_id=f"walkforward-{strategy_name.lower().replace(' ', '-')}-{strategy_version.lower()}-w{index:02d}",
        )
        window_result = {"window_number": index, **window_result, "window_passed": _window_passed(window_result)}
        window_results.append(window_result)
        blocked_reasons.extend(str(reason) for reason in window_result.get("blocked_reasons", []))
        profitability = window_result.get("profitability_result") if isinstance(window_result.get("profitability_result"), Mapping) else {}
        if not bool(profitability.get("evidence_quality_passed")):
            blocked_reasons.append("evidence_quality_failed")
        if not bool(profitability.get("risk_quality_passed")):
            blocked_reasons.append("risk_quality_failed")
        if _finite_float(profitability.get("expectancy_per_trade")) <= 0:
            blocked_reasons.append("negative_window_expectancy")

    windows_evaluated = len(window_results)
    passing_windows = sum(1 for result in window_results if result["window_passed"])
    failing_windows = windows_evaluated - passing_windows
    aggregates = _aggregate_metrics(window_results)

    if windows_evaluated < int(minimum_windows):
        blocked_reasons.append("insufficient_windows")
    if passing_windows < int(minimum_windows):
        blocked_reasons.append("insufficient_passing_windows")
    if aggregates["aggregate_expectancy"] <= 0:
        blocked_reasons.append("negative_aggregate_expectancy")
    if aggregates["aggregate_drawdown"] > _finite_float(maximum_drawdown):
        blocked_reasons.append("excessive_drawdown")

    blocked_reasons = _ordered_unique(blocked_reasons)
    demo_candidate = (
        windows_evaluated >= int(minimum_windows)
        and passing_windows == windows_evaluated
        and aggregates["aggregate_expectancy"] > 0
        and aggregates["aggregate_drawdown"] <= _finite_float(maximum_drawdown)
        and not blocked_reasons
    )
    if demo_candidate:
        promotion_status = "DEMO_REVIEW_CANDIDATE"
        next_safe_action = "review_for_demo_validation"
    elif any(
        reason in blocked_reasons
        for reason in {
            "negative_aggregate_expectancy",
            "excessive_drawdown",
            "evidence_quality_failed",
            "risk_quality_failed",
        }
    ):
        promotion_status = "REJECTED"
        next_safe_action = "reject_strategy_or_rework_edge"
    elif "insufficient_windows" in blocked_reasons or "insufficient_sample_size" in blocked_reasons or "insufficient_passing_windows" in blocked_reasons:
        promotion_status = "MORE_EVIDENCE_REQUIRED"
        next_safe_action = "continue_paper_trading_collect_more_evidence"
    elif not blocked_reasons:
        promotion_status = "PAPER_CONTINUE"
        next_safe_action = "continue_paper_trading_collect_more_evidence"
    else:
        promotion_status = "REJECTED"
        next_safe_action = "reject_strategy_or_rework_edge"

    return {
        "strategy_name": str(strategy_name or "").strip(),
        "strategy_version": str(strategy_version or "").strip(),
        "windows_evaluated": windows_evaluated,
        "passing_windows": passing_windows,
        "failing_windows": failing_windows,
        "window_results": window_results,
        "aggregate_expectancy": aggregates["aggregate_expectancy"],
        "aggregate_profit_factor": aggregates["aggregate_profit_factor"],
        "aggregate_drawdown": aggregates["aggregate_drawdown"],
        "promotion_status": promotion_status,
        "demo_candidate": demo_candidate,
        "blocked_reasons": blocked_reasons,
        "next_safe_action": next_safe_action,
        "safety": _safety(),
        "mode": MODE,
    }
