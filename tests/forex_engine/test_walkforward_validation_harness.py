"""Tests for walk-forward validation harness."""
from __future__ import annotations

import inspect

from automation.forex_engine import walkforward_validation_harness as harness


def test_profitable_multi_window_strategy_becomes_demo_review_candidate():
    result = harness.validate_walkforward_strategy(
        "Repeatable Alpha",
        "v1",
        validation_windows=2,
        window_trade_outcomes=[
            [200.0, -100.0, 150.0, -50.0, 125.0, 75.0],
            [180.0, -80.0, 140.0, -60.0, 120.0, 60.0],
        ],
    )
    assert result["windows_evaluated"] == 2
    assert result["passing_windows"] == 2
    assert result["failing_windows"] == 0
    assert result["promotion_status"] == "DEMO_REVIEW_CANDIDATE"
    assert result["demo_candidate"] is True
    assert result["blocked_reasons"] == []
    assert result["aggregate_expectancy"] > 0
    assert result["aggregate_profit_factor"] > 1.2


def test_mixed_window_strategy_blocks_promotion():
    result = harness.validate_walkforward_strategy(
        "Mixed Alpha",
        "v1",
        validation_windows=2,
        window_trade_outcomes=[
            [200.0, -100.0, 150.0, -50.0, 125.0, 75.0],
            [-100.0, -50.0, 25.0, -75.0, -25.0],
        ],
    )
    assert result["windows_evaluated"] == 2
    assert result["passing_windows"] == 1
    assert result["failing_windows"] == 1
    assert result["demo_candidate"] is False
    assert "insufficient_passing_windows" in result["blocked_reasons"]
    assert "negative_window_expectancy" in result["blocked_reasons"]


def test_negative_aggregate_expectancy_rejects_strategy():
    result = harness.validate_walkforward_strategy(
        "Negative Aggregate",
        "v1",
        validation_windows=2,
        window_trade_outcomes=[
            [-100.0, -50.0, 25.0, -75.0, -25.0],
            [-80.0, -40.0, 20.0, -60.0, -30.0],
        ],
    )
    assert result["aggregate_expectancy"] < 0
    assert result["promotion_status"] == "REJECTED"
    assert "negative_aggregate_expectancy" in result["blocked_reasons"]


def test_insufficient_windows_requires_more_evidence():
    result = harness.validate_walkforward_strategy(
        "Single Window Alpha",
        "v1",
        validation_windows=1,
        window_trade_outcomes=[[200.0, -100.0, 150.0, -50.0, 125.0, 75.0]],
    )
    assert result["windows_evaluated"] == 1
    assert result["passing_windows"] == 1
    assert result["promotion_status"] == "MORE_EVIDENCE_REQUIRED"
    assert result["demo_candidate"] is False
    assert "insufficient_windows" in result["blocked_reasons"]


def test_excessive_drawdown_blocks_promotion():
    result = harness.validate_walkforward_strategy(
        "Drawdown Alpha",
        "v1",
        validation_windows=2,
        window_trade_outcomes=[
            [300.0, -900.0, 400.0, 300.0, 200.0],
            [200.0, -100.0, 150.0, -50.0, 125.0, 75.0],
        ],
    )
    assert result["aggregate_drawdown"] == 900.0
    assert result["promotion_status"] == "REJECTED"
    assert result["demo_candidate"] is False
    assert "excessive_drawdown" in result["blocked_reasons"]


def test_deterministic_output():
    windows = [
        [200.0, -100.0, 150.0, -50.0, 125.0, 75.0],
        [180.0, -80.0, 140.0, -60.0, 120.0, 60.0],
    ]
    first = harness.validate_walkforward_strategy("Deterministic WF", "v1", 2, windows)
    second = harness.validate_walkforward_strategy("Deterministic WF", "v1", 2, windows)
    assert first == second


def test_safety_boundary_source_scan():
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

    safety = harness.validate_walkforward_strategy("Safety WF", "v1", 0, [])["safety"]
    assert safety["paper_only"] is True
    assert safety["broker_access"] is False
    assert safety["credential_access"] is False
    assert safety["network_access"] is False
    assert safety["live_trading_active"] is False
    assert safety["demo_execution_active"] is False
    assert safety["capital_allocation_modified"] is False
