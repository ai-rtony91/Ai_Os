"""Tests for market-regime evaluation harness."""
from __future__ import annotations

import inspect

from automation.forex_engine import market_regime_evaluation_harness as harness


PROFITABLE = [200.0, -100.0, 150.0, -50.0, 125.0, 75.0]
PROFITABLE_ALT = [180.0, -80.0, 140.0, -60.0, 120.0, 60.0]
LOSING = [-100.0, -50.0, 25.0, -75.0, -25.0]


def test_profitable_trending_strategy_identifies_best_regime():
    result = harness.evaluate_market_regimes(
        "Trend Follower",
        "v1",
        trade_outcomes={"TRENDING": PROFITABLE, "RANGING": PROFITABLE_ALT},
    )
    assert result["strategy_name"] == "Trend Follower"
    assert result["strategy_version"] == "v1"
    assert result["promotion_status"] == "DEMO_REVIEW_CANDIDATE"
    assert result["demo_candidate"] is True
    assert "TRENDING" in result["best_regimes"]
    assert result["worst_regimes"] == []
    assert result["aggregate_expectancy"] > 0
    assert result["aggregate_profit_factor"] > 1.2


def test_profitable_ranging_strategy_identifies_ranging_regime():
    result = harness.evaluate_market_regimes(
        "Range Reversion",
        "v2",
        trade_outcomes={"RANGING": [220.0, -80.0, 150.0, -50.0, 120.0, 60.0], "LOW_VOLATILITY": PROFITABLE_ALT},
    )
    assert result["promotion_status"] == "DEMO_REVIEW_CANDIDATE"
    assert result["demo_candidate"] is True
    assert result["best_regimes"][0] == "RANGING"
    assert all(item["regime_name"] in {"RANGING", "LOW_VOLATILITY"} for item in result["regime_results"])


def test_mixed_regime_strategy_blocks_promotion_and_identifies_worst_regime():
    result = harness.evaluate_market_regimes(
        "Mixed Regime",
        "v1",
        trade_outcomes={"TRENDING": PROFITABLE, "RANGING": LOSING},
    )
    assert result["demo_candidate"] is False
    assert result["promotion_status"] == "REJECTED"
    assert "TRENDING" in result["best_regimes"]
    assert "RANGING" in result["worst_regimes"]
    assert "negative_expectancy" in result["blocked_reasons"]


def test_negative_expectancy_strategy_rejects():
    result = harness.evaluate_market_regimes(
        "Bad Everywhere",
        "v1",
        trade_outcomes={"TRENDING": LOSING, "NEWS_DRIVEN": [-80.0, -40.0, 20.0, -60.0, -30.0]},
    )
    assert result["aggregate_expectancy"] < 0
    assert result["promotion_status"] == "REJECTED"
    assert result["demo_candidate"] is False
    assert "negative_aggregate_expectancy" in result["blocked_reasons"]
    assert result["best_regimes"] == []


def test_deterministic_output():
    outcomes = {"TRENDING": PROFITABLE, "RANGING": PROFITABLE_ALT}
    first = harness.evaluate_market_regimes("Deterministic Regime", "v1", trade_outcomes=outcomes)
    second = harness.evaluate_market_regimes("Deterministic Regime", "v1", trade_outcomes=outcomes)
    assert first == second


def test_safety_source_scan():
    source = inspect.getsource(harness)
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

    safety = harness.evaluate_market_regimes("Safety Regime", "v1", trade_outcomes={"TRENDING": PROFITABLE})["safety"]
    assert safety["paper_only"] is True
    assert safety["broker_access"] is False
    assert safety["credentials_access"] is False
    assert safety["network_access"] is False
    assert safety["live_trading_active"] is False
    assert safety["demo_execution_active"] is False
    assert safety["capital_allocation_modified"] is False
