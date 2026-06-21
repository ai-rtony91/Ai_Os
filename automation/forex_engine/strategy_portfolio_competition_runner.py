"""Canonical paper-only strategy portfolio competition runner."""
from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any
from collections.abc import Mapping

from automation.forex_engine.strategy_evaluation_harness import evaluate_strategy
from automation.forex_engine.market_regime_evaluation_harness import evaluate_market_regimes
from automation.forex_engine.walkforward_validation_harness import validate_walkforward_strategy
from automation.forex_engine.strategy_portfolio_ranking_engine import rank_strategies

MODE = "STRATEGY_PORTFOLIO_COMPETITION_RUNNER_ONLY"


def _safety() -> dict[str, bool]:
    return {
        "paper_only": True,
        "portfolio_competition_runner_only": True,
        "broker_access": False,
        "credentials_access": False,
        "network_access": False,
        "live_trading_active": False,
        "demo_execution_active": False,
        "capital_allocation_modified": False,
    }


def _load_strategy_module(module_path: str):
    path = Path(module_path)
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _metric(value: Any, *, default: float = 0.0) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    return parsed


def _to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"true", "1", "yes"}
    return bool(value)


def _safe(value: Any) -> bool:
    safety = value if isinstance(value, Mapping) else {}
    for key in ("broker_access", "credentials_access", "network_access", "live_trading_active", "demo_execution_active", "capital_allocation_modified"):
        if _to_bool(safety.get(key)):
            return False
    return bool(safety.get("paper_only", False))


def _candidate_from_payload(spec: Mapping[str, Any]) -> list[dict[str, Any]]:
    if isinstance(spec.get("candidates"), list):
        return [dict(candidate) for candidate in spec["candidates"] if isinstance(candidate, Mapping)]

    module_path = str(spec.get("strategy_module_path", ""))
    strategy_name = str(spec.get("strategy_name", "")).strip()
    if module_path:
        module = _load_strategy_module(module_path)
        if strategy_name == "DAY_TRADING_BREAKOUT_V1":
            payload = dict(spec.get("strategy_kwargs", {}))
            return list(module.generate_day_trading_breakout_candidates(**payload).get("candidates", []))
        if strategy_name == "MEAN_REVERSION_V1":
            payload = dict(spec.get("strategy_kwargs", {}))
            return list(module.generate_mean_reversion_candidates(**payload).get("candidates", []))
    return []


def _result_from_evaluation(evaluation: Mapping[str, Any]) -> tuple[float, float, float]:
    profitability = evaluation.get("profitability_result", {})
    return (
        _metric(profitability.get("expectancy_r", 0.0)),
        _metric(profitability.get("profit_factor", 0.0)),
        _metric(profitability.get("max_drawdown", 0.0)),
    )


def _run_walkforward(spec: Mapping[str, Any], eval_name: str, eval_version: str) -> dict[str, Any] | None:
    windows = spec.get("walkforward_windows")
    if windows is None and spec.get("window_trade_outcomes") is None:
        return None
    return validate_walkforward_strategy(
        strategy_name=eval_name,
        strategy_version=eval_version,
        validation_windows=spec.get("validation_windows"),
        window_trade_outcomes=spec.get("window_trade_outcomes"),
    )


def _run_market_regimes(spec: Mapping[str, Any], eval_name: str, eval_version: str) -> dict[str, Any] | None:
    market_regimes = spec.get("market_regime_trade_outcomes")
    regime_name = spec.get("regime_name")
    if market_regimes is None and regime_name is None:
        return None
    return evaluate_market_regimes(
        strategy_name=eval_name,
        strategy_version=eval_version,
        regime_name=regime_name,
        trade_outcomes=market_regimes,
    )


def _build_strategy_payload(spec: Mapping[str, Any], index: int) -> dict[str, Any]:
    strategy_name = str(spec.get("strategy_name", "")).strip()
    strategy_version = str(spec.get("strategy_version", "v1")).strip()
    safety = spec.get("safety", {}) if isinstance(spec.get("safety"), Mapping) else {}
    blocked_reasons = list(spec.get("blocked_reasons", [])) if isinstance(spec.get("blocked_reasons"), list) else []
    candidates = _candidate_from_payload(spec)
    evaluation = evaluate_strategy(strategy_name, strategy_version, candidates, session_id=f"competition-runner-{index:03d}")
    expectation, profit_factor, max_drawdown = _result_from_evaluation(evaluation)

    walkforward = _run_walkforward(spec, strategy_name, strategy_version)
    regime = _run_market_regimes(spec, strategy_name, strategy_version)
    if walkforward is not None:
        blocked_reasons.extend(list(walkforward.get("blocked_reasons", [])))
        expectation = _metric(walkforward.get("aggregate_expectancy", expectation))
        profit_factor = _metric(walkforward.get("aggregate_profit_factor", profit_factor))
        max_drawdown = _metric(walkforward.get("aggregate_drawdown", max_drawdown))
    if regime is not None:
        blocked_reasons.extend(list(regime.get("blocked_reasons", [])))

    supported_regimes = list(spec.get("supported_regimes", []))
    if regime is not None:
        supported_regimes.extend(list(regime.get("best_regimes", [])))
    if not supported_regimes and isinstance(evaluation.get("evidence_references"), Mapping):
        supported_regimes.extend(evaluation["evidence_references"].get("workflow_evidence_references", {}).keys())

    merged_blocked = list(dict.fromkeys([str(reason) for reason in blocked_reasons + list(evaluation.get("blocked_reasons", [])) if reason]))
    merged_safety = dict(safety)
    merged_safety.setdefault("paper_only", bool(evaluation.get("safety", {}).get("paper_only", True)))
    if not _safe(merged_safety):
        merged_safety["paper_only"] = True

    merged_blocked.extend(["unsafe_strategy"] if not _safe(merged_safety) else [])
    merged_blocked.extend(["negative_expectancy"] if expectation < 0 else [])

    return {
        "strategy_name": strategy_name,
        "strategy_version": strategy_version,
        "promotion_status": str(evaluation.get("promotion_status", "")),
        "demo_candidate": bool(evaluation.get("demo_candidate", False)),
        "expectancy": expectation,
        "profit_factor": profit_factor,
        "max_drawdown": max_drawdown,
        "win_rate": _metric(
            evaluation.get("profitability_result", {}).get("metrics", {}).get("win_rate", 0.0)
            if isinstance(evaluation.get("profitability_result"), Mapping)
            else 0.0
        ),
        "supported_regimes": supported_regimes,
        "blocked_reasons": list(dict.fromkeys(merged_blocked)),
        "safety": merged_safety,
        "next_safe_action": str(evaluation.get("next_safe_action", "collect_more_strategy_evidence")),
        "evidence_quality_passed": bool(
            (evaluation.get("profitability_result", {}).get("evidence_quality_passed") if isinstance(evaluation.get("profitability_result"), Mapping) else False)
        ),
        "risk_quality_passed": bool(
            (evaluation.get("profitability_result", {}).get("risk_quality_passed") if isinstance(evaluation.get("profitability_result"), Mapping) else False)
        ),
        "walkforward": walkforward,
        "market_regimes": regime,
        "mode": MODE,
    }


def run_strategy_portfolio_competition(*, strategy_competitors: list[dict[str, Any]] | tuple[Any, ...] | None = None) -> dict[str, Any]:
    competitors = list(strategy_competitors or [])
    competitor_payloads: list[dict[str, Any]] = []

    for index, entry in enumerate(competitors):
        if not isinstance(entry, Mapping):
            competitor_payloads.append(
                {
                    "strategy_name": "",
                    "strategy_version": "",
                    "promotion_status": "",
                    "demo_candidate": False,
                    "expectancy": 0.0,
                    "profit_factor": 0.0,
                    "max_drawdown": 0.0,
                    "win_rate": 0.0,
                    "supported_regimes": [],
                    "blocked_reasons": ["malformed_strategy_payload"],
                    "safety": {
                        "paper_only": True,
                        "broker_access": False,
                        "credentials_access": False,
                        "network_access": False,
                        "live_trading_active": False,
                        "demo_execution_active": False,
                        "capital_allocation_modified": False,
                    },
                    "risk_quality_passed": False,
                    "evidence_quality_passed": False,
                }
            )
            continue
        competitor_payloads.append(_build_strategy_payload(dict(entry), index))

    ranking = rank_strategies(strategy_results=competitor_payloads)
    ranked = list(ranking["ranked_strategies"])
    winner = {}
    if ranked and ranking["portfolio_ready"]:
        winner = ranked[0]
    portfolio_ready = bool(winner)

    blocked_reasons = list(dict.fromkeys(ranking["blocked_reasons"] + [reason for item in ranked for reason in item.get("blocked_reasons", []) if reason]))
    if winner and winner.get("blocked_reasons"):
        blocked_reasons.append("winner_has_blocked_reasons")
        winner = {}
        portfolio_ready = False

    return {
        "competition_completed": bool(competitors),
        "strategies_competed": competitor_payloads,
        "ranked_strategies": ranked,
        "winner": winner,
        "rejected_strategies": ranking["rejected_strategies"],
        "blocked_strategies": ranking["blocked_strategies"],
        "portfolio_ready": portfolio_ready,
        "blocked_reasons": blocked_reasons,
        "next_safe_action": ranking["next_safe_action"],
        "safety": _safety(),
        "mode": MODE,
    }

