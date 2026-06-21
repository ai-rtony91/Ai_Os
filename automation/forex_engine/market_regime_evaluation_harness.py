"""Market-regime evaluation harness for paper strategy evidence."""
from __future__ import annotations

import math
from typing import Any, Mapping

from automation.forex_engine.strategy_evaluation_harness import evaluate_strategy

MODE = "MARKET_REGIME_EVALUATION_HARNESS_ONLY"
SUPPORTED_REGIMES = {"TRENDING", "RANGING", "HIGH_VOLATILITY", "LOW_VOLATILITY", "NEWS_DRIVEN"}


def _safety() -> dict[str, bool]:
    return {
        "paper_only": True,
        "market_regime_evaluation_only": True,
        "broker_access": False,
        "credentials_access": False,
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


def _normalize_regime_name(value: Any) -> str:
    return str(value or "").strip().upper()


def _ordered_unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result


def _candidate_from_outcome(outcome: Any, regime_name: str, index: int) -> dict[str, Any]:
    if isinstance(outcome, Mapping):
        candidate = dict(outcome)
        candidate.setdefault("trade_id", f"{regime_name.lower()}-trade-{index:04d}")
        return candidate
    return {
        "trade_id": f"{regime_name.lower()}-trade-{index:04d}",
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


def _regime_inputs(regime_name: Any = None, trade_outcomes: Any = None) -> list[dict[str, Any]]:
    if isinstance(trade_outcomes, Mapping):
        return [
            {"regime_name": _normalize_regime_name(name), "trade_outcomes": list(outcomes if isinstance(outcomes, list) else [outcomes])}
            for name, outcomes in trade_outcomes.items()
        ]
    if isinstance(trade_outcomes, list) and all(isinstance(item, Mapping) and "regime_name" in item for item in trade_outcomes):
        return [
            {
                "regime_name": _normalize_regime_name(item.get("regime_name")),
                "trade_outcomes": list(item.get("trade_outcomes", item.get("outcomes", [])) or []),
            }
            for item in trade_outcomes
        ]
    if regime_name is not None:
        return [{"regime_name": _normalize_regime_name(regime_name), "trade_outcomes": list(trade_outcomes or [])}]
    return []


def _aggregate_metrics(regime_results: list[dict[str, Any]]) -> dict[str, float | int]:
    total_trades = 0
    total_pnl = 0.0
    gross_profit = 0.0
    gross_loss = 0.0
    for result in regime_results:
        profitability = result.get("profitability_result", {})
        metrics = profitability.get("metrics", {}) if isinstance(profitability, Mapping) and isinstance(profitability.get("metrics"), Mapping) else {}
        trades = int(metrics.get("total_trades", result.get("total_trades", 0)) or 0)
        total_trades += trades
        total_pnl = round(total_pnl + (_finite_float(result.get("expectancy_per_trade")) * trades), 8)
        gross_profit = round(gross_profit + _finite_float(metrics.get("gross_profit")), 8)
        gross_loss = round(gross_loss + _finite_float(metrics.get("gross_loss")), 8)
    return {
        "total_trades": total_trades,
        "aggregate_expectancy": round(total_pnl / total_trades, 8) if total_trades else 0.0,
        "aggregate_profit_factor": round(gross_profit / gross_loss, 8) if gross_loss > 0 else (999.0 if gross_profit > 0 else 0.0),
    }


def evaluate_market_regimes(
    strategy_name: str,
    strategy_version: str = "v1",
    regime_name: str | None = None,
    trade_outcomes: Any = None,
) -> dict[str, Any]:
    """Evaluate deterministic strategy evidence by supported market regime."""
    inputs = _regime_inputs(regime_name, trade_outcomes)
    regime_results: list[dict[str, Any]] = []
    blocked_reasons: list[str] = []

    for item in inputs:
        regime = item["regime_name"]
        outcomes = item["trade_outcomes"]
        if regime not in SUPPORTED_REGIMES:
            blocked_reasons.append("unsupported_regime")
            continue
        candidates = [_candidate_from_outcome(outcome, regime, index) for index, outcome in enumerate(outcomes, start=1)]
        result = evaluate_strategy(
            strategy_name,
            strategy_version,
            candidates,
            session_id=f"market-regime-{strategy_name.lower().replace(' ', '-')}-{strategy_version.lower()}-{regime.lower()}",
        )
        profitability = result.get("profitability_result") if isinstance(result.get("profitability_result"), Mapping) else {}
        promotion = result.get("promotion_result") if isinstance(result.get("promotion_result"), Mapping) else {}
        expectation = _finite_float(profitability.get("expectancy_per_trade"))
        regime_result = {
            "regime_name": regime,
            "total_trades": result.get("total_trades", 0),
            "expectancy_per_trade": expectation,
            "profit_factor": _finite_float(profitability.get("profit_factor")),
            "max_drawdown": _finite_float(profitability.get("max_drawdown")),
            "promotion_status": result.get("promotion_status", ""),
            "demo_candidate": bool(result.get("demo_candidate")),
            "profitable": expectation > 0 and bool(profitability.get("evidence_quality_passed")) and bool(profitability.get("risk_quality_passed")),
            "blocked_reasons": list(result.get("blocked_reasons", [])),
            "next_safe_action": result.get("next_safe_action", ""),
            "profitability_result": profitability,
            "promotion_result": promotion,
        }
        regime_results.append(regime_result)
        blocked_reasons.extend(str(reason) for reason in regime_result["blocked_reasons"])
        if not bool(profitability.get("evidence_quality_passed")):
            blocked_reasons.append("evidence_quality_failed")
        if not bool(profitability.get("risk_quality_passed")):
            blocked_reasons.append("risk_quality_failed")

    aggregates = _aggregate_metrics(regime_results)
    best_regimes = [result["regime_name"] for result in sorted(regime_results, key=lambda result: result["expectancy_per_trade"], reverse=True) if result["profitable"]]
    worst_regimes = [result["regime_name"] for result in sorted(regime_results, key=lambda result: result["expectancy_per_trade"]) if not result["profitable"]]

    if len(regime_results) < 2:
        blocked_reasons.append("insufficient_regimes")
    if not best_regimes:
        blocked_reasons.append("no_profitable_regimes")
    if aggregates["aggregate_expectancy"] <= 0:
        blocked_reasons.append("negative_aggregate_expectancy")

    blocked_reasons = _ordered_unique(blocked_reasons)
    demo_candidate = len(regime_results) >= 2 and aggregates["aggregate_expectancy"] > 0 and bool(best_regimes) and not blocked_reasons
    if demo_candidate:
        promotion_status = "DEMO_REVIEW_CANDIDATE"
        next_safe_action = "review_for_demo_validation"
    elif "insufficient_regimes" in blocked_reasons or "insufficient_sample_size" in blocked_reasons:
        promotion_status = "MORE_EVIDENCE_REQUIRED"
        next_safe_action = "continue_paper_trading_collect_more_evidence"
    else:
        promotion_status = "REJECTED"
        next_safe_action = "reject_strategy_or_rework_edge"

    return {
        "strategy_name": str(strategy_name or "").strip(),
        "strategy_version": str(strategy_version or "").strip(),
        "regime_results": regime_results,
        "best_regimes": best_regimes,
        "worst_regimes": worst_regimes,
        "aggregate_expectancy": aggregates["aggregate_expectancy"],
        "aggregate_profit_factor": aggregates["aggregate_profit_factor"],
        "promotion_status": promotion_status,
        "demo_candidate": demo_candidate,
        "blocked_reasons": blocked_reasons,
        "next_safe_action": next_safe_action,
        "safety": _safety(),
        "mode": MODE,
    }
