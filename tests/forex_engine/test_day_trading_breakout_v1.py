"""Tests for DAY_TRADING_BREAKOUT_V1."""
from __future__ import annotations

import inspect
import importlib.util
from pathlib import Path

from automation.forex_engine.strategy_evaluation_harness import evaluate_strategy

MODULE_PATH = Path(__file__).resolve().parents[2] / "automation" / "forex_engine" / "strategies" / "day_trading_breakout_v1.py"


def _load_strategy():
    spec = importlib.util.spec_from_file_location("day_trading_breakout_v1", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


strategy = _load_strategy()


def _build(**overrides):
    payload = {
        "symbol": "EURUSD",
        "session_name": "London",
        "timeframe": "M15",
        "high_price": 1.105,
        "low_price": 1.1,
        "current_price": 1.106,
        "risk_percent": 1.0,
    }
    payload.update(overrides)
    return strategy.generate_day_trading_breakout_candidates(**payload)


def test_bullish_breakout_generates_long_candidate():
    result = _build(current_price=1.106)
    assert result["candidate_count"] == 1
    assert result["blocked_reasons"] == []
    assert result["evidence"]["signal"] == "BULLISH_BREAKOUT"
    candidate = result["candidates"][0]
    assert candidate["direction"] == "buy"
    assert candidate["entry"] == 1.106
    assert candidate["stop"] == 1.1
    assert candidate["target"] == 1.111
    assert candidate["realized_pl"] > 0

    evaluation = evaluate_strategy("DAY_TRADING_BREAKOUT_V1", "v1", result["candidates"])
    assert evaluation["total_trades"] == 1
    assert "insufficient_sample_size" in evaluation["blocked_reasons"]


def test_bearish_breakout_generates_short_candidate():
    result = _build(current_price=1.099)
    assert result["candidate_count"] == 1
    assert result["blocked_reasons"] == []
    assert result["evidence"]["signal"] == "BEARISH_BREAKDOWN"
    candidate = result["candidates"][0]
    assert candidate["direction"] == "sell"
    assert candidate["entry"] == 1.099
    assert candidate["stop"] == 1.105
    assert candidate["target"] == 1.094
    assert candidate["realized_pl"] > 0


def test_no_breakout_returns_no_candidate():
    result = _build(current_price=1.103)
    assert result["candidate_count"] == 0
    assert result["candidates"] == []
    assert result["evidence"]["signal"] == "NO_BREAKOUT"
    assert result["blocked_reasons"] == ["no_breakout"]
    assert result["next_safe_action"] == "continue_waiting_for_breakout"


def test_malformed_input_blocks_candidate_generation():
    result = _build(high_price="bad", low_price=1.1, current_price=1.106, risk_percent=0)
    assert result["candidate_count"] == 0
    assert "invalid_price_input" in result["blocked_reasons"]
    assert "invalid_risk_percent" in result["blocked_reasons"]
    assert result["next_safe_action"] == "wait_for_valid_breakout_input"


def test_deterministic_output():
    first = _build(current_price=1.106)
    second = _build(current_price=1.106)
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
