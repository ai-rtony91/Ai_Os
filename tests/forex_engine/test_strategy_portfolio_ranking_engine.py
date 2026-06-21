"""Tests for strategy portfolio ranking engine."""
from __future__ import annotations

import inspect
import importlib.util
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[2] / "automation" / "forex_engine" / "strategy_portfolio_ranking_engine.py"


def _load_engine():
    spec = importlib.util.spec_from_file_location("strategy_portfolio_ranking_engine", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


engine = _load_engine()


def _sample_inputs():
    return [
        {
            "strategy_name": "DAY_TRADING_BREAKOUT_V1",
            "strategy_version": "v1",
            "promotion_status": "DEMO_REVIEW_CANDIDATE",
            "demo_candidate": True,
            "expectancy": 1.2,
            "profit_factor": 1.9,
            "max_drawdown": 0.22,
            "win_rate": 0.58,
            "supported_regimes": ["trend", "mean_reversion"],
            "blocked_reasons": [],
            "safety": {
                "paper_only": True,
                "broker_access": False,
                "credentials_access": False,
                "network_access": False,
                "live_trading_active": False,
                "demo_execution_active": False,
                "capital_allocation_modified": False,
            },
        },
        {
            "strategy_name": "MEAN_REVERSION_V1",
            "strategy_version": "v1",
            "promotion_status": "DEMO_REVIEW_CANDIDATE",
            "demo_candidate": True,
            "expectancy": 1.7,
            "profit_factor": 1.6,
            "max_drawdown": 0.30,
            "win_rate": 0.64,
            "supported_regimes": ["mean_reversion"],
            "blocked_reasons": [],
            "safety": {
                "paper_only": True,
                "broker_access": False,
                "credentials_access": False,
                "network_access": False,
                "live_trading_active": False,
                "demo_execution_active": False,
                "capital_allocation_modified": False,
            },
        },
    ]


def test_rank_profitable_strategies():
    result = engine.rank_strategies(strategy_results=_sample_inputs())
    assert result["portfolio_ready"] is True
    assert len(result["ranked_strategies"]) == 2
    assert result["blocked_strategies"] == []
    assert result["rejected_strategies"] == []
    assert result["top_strategy"]["strategy_name"] == "MEAN_REVERSION_V1"
    assert result["ranked_strategies"][0]["strategy_name"] == "MEAN_REVERSION_V1"
    assert result["ranked_strategies"][1]["strategy_name"] == "DAY_TRADING_BREAKOUT_V1"


def test_reject_negative_expectancy_strategy():
    results = _sample_inputs()
    results.append(
        {
            "strategy_name": "BAD_MEAN_REVERSION_V1",
            "strategy_version": "v1",
            "expectancy": -0.2,
            "profit_factor": 2.2,
            "max_drawdown": 0.40,
            "safety": {"paper_only": True},
        }
    )
    result = engine.rank_strategies(strategy_results=results)
    names = {item["strategy_name"] for item in result["rejected_strategies"]}
    assert "BAD_MEAN_REVERSION_V1" in names
    assert result["portfolio_ready"] is True
    assert result["top_strategy"]["strategy_name"] == "MEAN_REVERSION_V1"


def test_reject_blocked_strategy():
    results = _sample_inputs()
    results[1]["blocked_reasons"] = ["evidence_quality_failed"]
    results.append(
        {
            "strategy_name": "MEAN_REVERSION_V1",
            "strategy_version": "v1",
            "expectancy": 3.0,
            "profit_factor": 4.0,
            "max_drawdown": 0.20,
        }
    )
    result = engine.rank_strategies(strategy_results=results)
    assert result["top_strategy"]["expectancy"] == 3.0
    assert result["top_strategy"]["strategy_name"] == "MEAN_REVERSION_V1"
    assert any(item["expectancy"] == 1.7 and "evidence_quality_failed" in item["blocked_reasons"] for item in result["rejected_strategies"])


def test_prefer_lower_drawdown_when_expectancy_is_close():
    results = _sample_inputs()
    results[0]["expectancy"] = 1.20
    results[0]["max_drawdown"] = 0.12
    results[1]["expectancy"] = 1.21
    results[1]["max_drawdown"] = 0.25
    result = engine.rank_strategies(strategy_results=results)
    assert result["ranked_strategies"][0]["strategy_name"] == "DAY_TRADING_BREAKOUT_V1"


def test_prefer_broader_regime_coverage_when_metrics_are_close():
    results = [
        {
            "strategy_name": "STRAT_A",
            "strategy_version": "v1",
            "expectancy": 1.31,
            "profit_factor": 1.5,
            "max_drawdown": 0.20,
            "supported_regimes": ["trend"],
            "safety": {"paper_only": True},
        },
        {
            "strategy_name": "STRAT_B",
            "strategy_version": "v1",
            "expectancy": 1.32,
            "profit_factor": 1.5,
            "max_drawdown": 0.20,
            "supported_regimes": ["trend", "range", "news"],
            "safety": {"paper_only": True},
        },
    ]
    result = engine.rank_strategies(strategy_results=results)
    assert result["ranked_strategies"][0]["strategy_name"] == "STRAT_B"


def test_deterministic_output():
    result_a = engine.rank_strategies(strategy_results=_sample_inputs())
    result_b = engine.rank_strategies(strategy_results=_sample_inputs())
    assert result_a == result_b


def test_malformed_input_blocks_candidate():
    result = engine.rank_strategies(strategy_results=[None, {"bad": "value"}])
    assert len(result["ranked_strategies"]) == 0
    assert len(result["rejected_strategies"]) >= 1
    assert len(result["blocked_strategies"]) == 1
    assert not result["portfolio_ready"]
    assert "no_rankable_strategies" in result["blocked_reasons"]
    assert result["blocked_strategies"][0]["blocked_reasons"] == ["malformed_strategy_result"]


def test_safety_source_scan():
    source = inspect.getsource(engine)
    forbidden = (
        "import requests",
        "from requests",
        "import urllib",
        "from urllib",
        "import subprocess",
        "from subprocess",
        "import socket",
        "from socket",
        "open(",
        "write_text",
        "write_bytes",
        "os.environ",
        "getenv(",
        "broker_sdk",
        "oanda",
    )
    for token in forbidden:
        assert token not in source

    safety = engine._safety()
    assert safety["paper_only"] is True
    assert safety["broker_access"] is False
    assert safety["credentials_access"] is False
    assert safety["network_access"] is False
    assert safety["live_trading_active"] is False
    assert safety["demo_execution_active"] is False
    assert safety["capital_allocation_modified"] is False
