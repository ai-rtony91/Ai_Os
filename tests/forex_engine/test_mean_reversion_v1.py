"""Tests for MEAN_REVERSION_V1."""
from __future__ import annotations

import importlib.util
import inspect
from pathlib import Path

from automation.forex_engine.strategy_evaluation_harness import evaluate_strategy

MODULE_PATH = Path(__file__).resolve().parents[2] / "automation" / "forex_engine" / "strategies" / "mean_reversion_v1.py"


def _load_strategy():
    spec = importlib.util.spec_from_file_location("mean_reversion_v1", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


strategy = _load_strategy()


def _build(**overrides):
    payload = {
        "symbol": "EURUSD",
        "session_name": "NewYork",
        "timeframe": "M15",
        "moving_average": 1.1,
        "current_price": 1.095,
        "deviation_percent": 0.25,
        "risk_percent": 1.0,
    }
    payload.update(overrides)
    return strategy.generate_mean_reversion_candidates(**payload)


def test_bullish_mean_reversion_generates_long_candidate():
    result = _build(current_price=1.095)
    assert result["candidate_count"] == 1
    assert result["blocked_reasons"] == []
    assert result["evidence"]["signal"] == "BULLISH_MEAN_REVERSION"
    candidate = result["candidates"][0]
    assert candidate["direction"] == "buy"
    assert candidate["entry"] == 1.095
    assert candidate["stop"] == 1.09
    assert candidate["target"] == 1.1
    assert candidate["realized_pl"] > 0

    evaluation = evaluate_strategy("MEAN_REVERSION_V1", "v1", result["candidates"])
    assert evaluation["total_trades"] == 1
    assert "insufficient_sample_size" in evaluation["blocked_reasons"]


def test_bearish_mean_reversion_generates_short_candidate():
    result = _build(current_price=1.105)
    assert result["candidate_count"] == 1
    assert result["blocked_reasons"] == []
    assert result["evidence"]["signal"] == "BEARISH_MEAN_REVERSION"
    candidate = result["candidates"][0]
    assert candidate["direction"] == "sell"
    assert candidate["entry"] == 1.105
    assert candidate["stop"] == 1.11
    assert candidate["target"] == 1.1
    assert candidate["realized_pl"] > 0


def test_no_trade_condition_returns_no_candidate():
    result = _build(current_price=1.101)
    assert result["candidate_count"] == 0
    assert result["candidates"] == []
    assert result["evidence"]["signal"] == "NO_TRADE"
    assert result["blocked_reasons"] == ["within_acceptable_deviation"]
    assert result["next_safe_action"] == "continue_waiting_for_mean_reversion_setup"


def test_malformed_input_blocks_candidate_generation():
    result = _build(moving_average="bad", current_price=1.095, deviation_percent=0, risk_percent=0)
    assert result["candidate_count"] == 0
    assert "invalid_price_input" in result["blocked_reasons"]
    assert "invalid_deviation_percent" in result["blocked_reasons"]
    assert "invalid_risk_percent" in result["blocked_reasons"]
    assert result["next_safe_action"] == "wait_for_valid_mean_reversion_input"


def test_deterministic_output():
    first = _build(current_price=1.095)
    second = _build(current_price=1.095)
    assert first == second


def test_safety_source_scan():
    source = inspect.getsource(strategy)
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

    safety = _build()["safety"]
    assert safety["paper_only"] is True
    assert safety["broker_access"] is False
    assert safety["credentials_access"] is False
    assert safety["network_access"] is False
    assert safety["live_trading_active"] is False
    assert safety["demo_execution_active"] is False
    assert safety["capital_allocation_modified"] is False
    assert safety["broker_execution_allowed"] is False
    assert safety["short_selling_requires_broker_policy_review"] is True
    assert safety["hedging_fifo_policy_review_required"] is True
    assert safety["margin_policy_review_required"] is True
