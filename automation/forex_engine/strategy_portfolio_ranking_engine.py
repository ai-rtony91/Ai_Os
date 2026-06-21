"""Canonical deterministic portfolio-ranking engine for paper-only strategy outputs."""
from __future__ import annotations

import math
from typing import Any
from collections.abc import Mapping

MODE = "STRATEGY_PORTFOLIO_RANKING_ENGINE_ONLY"
EXPECTANCY_BUCKET = 0.05


def _safety() -> dict[str, bool]:
    return {
        "paper_only": True,
        "strategy_ranking_only": True,
        "broker_access": False,
        "credentials_access": False,
        "network_access": False,
        "live_trading_active": False,
        "demo_execution_active": False,
        "capital_allocation_modified": False,
    }


def _finite_float(value: Any) -> tuple[float, bool]:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0, False
    if not math.isfinite(number):
        return 0.0, False
    return round(number, 8), True


def _boolish(value: Any) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lower = value.strip().lower()
        if lower in {"true", "1", "yes"}:
            return True
        if lower in {"false", "0", "no"}:
            return False
    return None


def _extract_metric(value: Any) -> tuple[float, bool]:
    return _finite_float(value)


def _safe_flag(strategy: Mapping[str, Any]) -> bool:
    safety = strategy.get("safety") if isinstance(strategy.get("safety"), Mapping) else {}
    if safety is None:
        safety = {}

    if _boolish(safety.get("paper_only")) is False:
        return False
    blocked = False
    for key in (
        "broker_access",
        "credentials_access",
        "network_access",
        "live_trading_active",
        "demo_execution_active",
        "capital_allocation_modified",
    ):
        bool_value = _boolish(safety.get(key))
        if bool_value is True:
            blocked = True
    return not blocked


def _read_list(source: Any) -> list[str]:
    if not isinstance(source, list):
        return []
    return [str(item) for item in source if isinstance(item, str) and item]


def _expectancy(value: Mapping[str, Any], reasons: list[str]) -> tuple[float, bool]:
    if "expectancy" in value:
        return _extract_metric(value.get("expectancy"))
    return 0.0, False


def _profit_factor(value: Mapping[str, Any]) -> tuple[float, bool]:
    if "profit_factor" in value:
        return _extract_metric(value.get("profit_factor"))
    profitability_result = value.get("profitability_result") if isinstance(value.get("profitability_result"), Mapping) else {}
    if not profitability_result:
        return 0.0, False
    return _extract_metric(profitability_result.get("profit_factor"))


def _drawdown(value: Mapping[str, Any]) -> tuple[float, bool]:
    if "max_drawdown" in value:
        return _extract_metric(value.get("max_drawdown"))
    return 0.0, False


def _failed_quality_flags(value: Mapping[str, Any]) -> list[str]:
    failures: list[str] = []
    evidence_quality = None
    risk_quality = None
    if "evidence_quality_passed" in value:
        evidence_quality = _boolish(value.get("evidence_quality_passed"))
    elif "profitability_result" in value:
        nested = value["profitability_result"]
        evidence_quality = _boolish(nested.get("evidence_quality_passed")) if isinstance(nested, Mapping) else None

    if evidence_quality is False:
        failures.append("failed_evidence_quality")

    if "risk_quality_passed" in value:
        risk_quality = _boolish(value.get("risk_quality_passed"))
    elif "profitability_result" in value:
        nested = value["profitability_result"]
        risk_quality = _boolish(nested.get("risk_quality_passed")) if isinstance(nested, Mapping) else None

    if risk_quality is False:
        failures.append("failed_risk_quality")

    return failures


def _norm_result(strategy: Mapping[str, Any], index: int) -> dict[str, Any]:
    name = str(strategy.get("strategy_name", "")).strip()
    version = str(strategy.get("strategy_version", "")).strip()
    safe = _safe_flag(strategy)
    blocked_reasons = _read_list(strategy.get("blocked_reasons"))
    evidence_failures = _failed_quality_flags(strategy)

    expectancy, expectancy_valid = _expectancy(strategy, blocked_reasons)
    profit_factor_value, profit_factor_valid = _profit_factor(strategy)
    drawdown_value, drawdown_valid = _drawdown(strategy)

    if not name or not version:
        blocked_reasons.append("invalid_strategy_identity")
    if not safe:
        blocked_reasons.append("unsafe_strategy")
    if not safe:
        blocked_reasons.append("blocked_by_safety_policy")
    if not expectancy_valid:
        blocked_reasons.append("invalid_expectancy")
    elif expectancy < 0:
        blocked_reasons.append("negative_expectancy")
    if not profit_factor_valid:
        blocked_reasons.append("invalid_profit_factor")
    if not drawdown_valid:
        blocked_reasons.append("invalid_drawdown")

    blocked_reasons.extend(evidence_failures)
    blocked_reasons = list(dict.fromkeys(blocked_reasons))

    return {
        "strategy_name": name,
        "strategy_version": version,
        "promotion_status": str(strategy.get("promotion_status", "")),
        "demo_candidate": bool(strategy.get("demo_candidate", False)),
        "expectancy": expectancy,
        "profit_factor": profit_factor_value,
        "max_drawdown": drawdown_value,
        "win_rate": _extract_metric(strategy.get("win_rate"))[0] if "win_rate" in strategy else 0.0,
        "supported_regimes": list(strategy.get("supported_regimes", [])) if isinstance(strategy.get("supported_regimes"), list) else [],
        "blocked_reasons": blocked_reasons,
        "safety": strategy.get("safety", {}),
        "source_index": index,
        "safe": safe,
        "risk_ok": "failed_risk_quality" not in blocked_reasons,
        "evidence_ok": "failed_evidence_quality" not in blocked_reasons,
        "_ranking_inputs": {
            "expectancy_valid": expectancy_valid,
            "profit_factor_valid": profit_factor_valid,
            "drawdown_valid": drawdown_valid,
        },
    }


def _is_rejected(strategy: Mapping[str, Any]) -> bool:
    if strategy.get("blocked_reasons"):
        return True
    return False


def _expectancy_bucket(value: float) -> float:
    if not math.isfinite(value):
        return -10_000.0
    return round(round(value / EXPECTANCY_BUCKET) * EXPECTANCY_BUCKET, 8)


def _sort_key(candidate: Mapping[str, Any]):
    drawdown = candidate["max_drawdown"]
    coverage = len(candidate["supported_regimes"])
    return (
        -_expectancy_bucket(candidate["expectancy"]),
        -candidate["profit_factor"],
        drawdown,
        -coverage,
        candidate["source_index"],
        candidate["strategy_name"],
    )


def rank_strategies(*, strategy_results: list[dict[str, Any]] | tuple[Any, ...]) -> dict[str, Any]:
    normalized = [_norm_result(dict(item), index) for index, item in enumerate(strategy_results or []) if isinstance(item, Mapping)]
    non_mappings = [item for item in (strategy_results or []) if not isinstance(item, Mapping)]
    for _ in non_mappings:
        normalized.append(
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
                "blocked_reasons": ["malformed_strategy_result"],
                "safety": {},
                "source_index": len(normalized),
                "safe": False,
                "risk_ok": False,
                "evidence_ok": False,
            }
        )

    rejected = [item for item in normalized if _is_rejected(item)]
    ranked = [item for item in normalized if item not in rejected]

    safe_ranked = [item for item in ranked if item["safe"]]
    unsafe_ranked = [item for item in ranked if not item["safe"]]

    def _sorted(items):
        return sorted(items, key=_sort_key)

    safe_ranked = _sorted(safe_ranked)
    unsafe_ranked = _sorted(unsafe_ranked)
    ranked_strategies = safe_ranked + unsafe_ranked

    top_strategy = ranked_strategies[0] if ranked_strategies else {}
    portfolio_ready = bool(ranked_strategies) and bool(top_strategy.get("safe")) and top_strategy["expectancy"] > 0

    blocked_reasons: list[str] = []
    if non_mappings:
        blocked_reasons.append("input_must_be_strategy_results")
    if not ranked_strategies:
        blocked_reasons.append("no_rankable_strategies")
        next_safe_action = "collect_more_strategy_results"
    elif portfolio_ready:
        next_safe_action = "start_portfolio_risk_checks"
    else:
        blocked_reasons.append("top_strategy_not_portfolio_ready")
        next_safe_action = "collect_more_strategy_results"

    if not strategy_results:
        blocked_reasons.append("empty_strategy_results")

    return {
        "ranked_strategies": ranked_strategies,
        "top_strategy": top_strategy,
        "rejected_strategies": rejected,
        "blocked_strategies": [item for item in normalized if not item["safe"]],
        "portfolio_ready": portfolio_ready,
        "blocked_reasons": blocked_reasons,
        "next_safe_action": next_safe_action,
        "safety": _safety(),
        "mode": MODE,
    }
