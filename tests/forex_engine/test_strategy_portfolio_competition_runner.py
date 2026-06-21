"""Tests for strategy portfolio competition runner."""
from __future__ import annotations

import importlib.util
import inspect
from pathlib import Path

from automation.forex_engine.strategy_portfolio_competition_runner import run_strategy_portfolio_competition

BASE_PATH = Path(__file__).resolve().parents[2] / "automation" / "forex_engine" / "strategies"


def _load_strategy_module(name: str):
    module_path = BASE_PATH / name
    spec = importlib.util.spec_from_file_location(module_path.stem, module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


_breakout = _load_strategy_module("day_trading_breakout_v1.py")
_reversion = _load_strategy_module("mean_reversion_v1.py")


def _safe_candidate_payload():
    return {"paper_only": True, "broker_access": False, "credentials_access": False, "network_access": False, "live_trading_active": False}


def _build_strategy_payload(strategy_module, strategy_name: str, candidates):
    return {
        "strategy_name": strategy_name,
        "strategy_version": "v1",
        "safety": _safe_candidate_payload(),
        "candidates": candidates,
    }


def _repeat_candidate(candidate: dict[str, object], count: int):
    return [dict(candidate | {"trade_id": f"trade-{index:04d}"}) for index in range(1, count + 1)]


def test_breakout_beats_mean_reversion():
    breakout_candidate = _breakout.generate_day_trading_breakout_candidates(
        symbol="EURUSD",
        session_name="London",
        timeframe="M15",
        high_price=1.105,
        low_price=1.100,
        current_price=1.106,
        risk_percent=2.0,
    )["candidates"][0]
    mean_candidate = _reversion.generate_mean_reversion_candidates(
        symbol="EURUSD",
        session_name="London",
        timeframe="M15",
        moving_average=1.1,
        current_price=1.09,
        deviation_percent=0.5,
        risk_percent=1.0,
    )["candidates"][0]
    mean_candidate["realized_pl"] = 10.0

    result = run_strategy_portfolio_competition(
        strategy_competitors=[
            _build_strategy_payload("day_trading_breakout_v1.py", "DAY_TRADING_BREAKOUT_V1", _repeat_candidate(breakout_candidate, 20)),
            _build_strategy_payload("mean_reversion_v1.py", "MEAN_REVERSION_V1", _repeat_candidate(mean_candidate, 20)),
        ]
    )
    assert result["competition_completed"] is True
    assert result["portfolio_ready"] is True
    assert result["winner"]["strategy_name"] == "DAY_TRADING_BREAKOUT_V1"


def test_mean_reversion_beats_breakout():
    breakout_candidate = _breakout.generate_day_trading_breakout_candidates(
        symbol="EURUSD",
        session_name="London",
        timeframe="M15",
        high_price=1.105,
        low_price=1.100,
        current_price=1.106,
        risk_percent=2.0,
    )["candidates"][0]
    breakout_candidate["realized_pl"] = 25.0

    mean_candidate = _reversion.generate_mean_reversion_candidates(
        symbol="EURUSD",
        session_name="London",
        timeframe="M15",
        moving_average=1.1,
        current_price=1.09,
        deviation_percent=0.5,
        risk_percent=1.0,
    )["candidates"][0]

    result = run_strategy_portfolio_competition(
        strategy_competitors=[
            _build_strategy_payload("day_trading_breakout_v1.py", "DAY_TRADING_BREAKOUT_V1", _repeat_candidate(breakout_candidate, 20)),
            _build_strategy_payload("mean_reversion_v1.py", "MEAN_REVERSION_V1", _repeat_candidate(mean_candidate, 20)),
        ]
    )
    assert result["competition_completed"] is True
    assert result["portfolio_ready"] is True
    assert result["winner"]["strategy_name"] == "MEAN_REVERSION_V1"


def test_both_rejected():
    losing_breakout = _breakout.generate_day_trading_breakout_candidates(
        symbol="EURUSD",
        session_name="London",
        timeframe="M15",
        high_price=1.105,
        low_price=1.100,
        current_price=1.106,
        risk_percent=1.0,
    )["candidates"][0]
    losing_mean = _reversion.generate_mean_reversion_candidates(
        symbol="EURUSD",
        session_name="London",
        timeframe="M15",
        moving_average=1.1,
        current_price=1.09,
        deviation_percent=0.5,
        risk_percent=1.0,
    )["candidates"][0]
    losing_breakout["realized_pl"] = -150.0
    losing_mean["realized_pl"] = -75.0

    result = run_strategy_portfolio_competition(
        strategy_competitors=[
            _build_strategy_payload("day_trading_breakout_v1.py", "DAY_TRADING_BREAKOUT_V1", _repeat_candidate(losing_breakout, 20)),
            _build_strategy_payload("mean_reversion_v1.py", "MEAN_REVERSION_V1", _repeat_candidate(losing_mean, 20)),
        ]
    )
    assert result["portfolio_ready"] is False
    assert result["winner"] == {}
    assert result["rejected_strategies"] and len(result["rejected_strategies"]) >= 2

def test_unsafe_strategy_rejected():
    safe_breakout = _breakout.generate_day_trading_breakout_candidates(
        symbol="EURUSD",
        session_name="London",
        timeframe="M15",
        high_price=1.105,
        low_price=1.100,
        current_price=1.106,
        risk_percent=1.0,
    )["candidates"][0]
    safe_payload = _build_strategy_payload("day_trading_breakout_v1.py", "DAY_TRADING_BREAKOUT_V1", [safe_breakout])
    unsafe_payload = _build_strategy_payload(
        "mean_reversion_v1.py",
        "MEAN_REVERSION_V1",
        _reversion.generate_mean_reversion_candidates(
            symbol="EURUSD",
            session_name="London",
            timeframe="M15",
            moving_average=1.1,
            current_price=1.09,
            deviation_percent=0.5,
            risk_percent=1.0,
        )["candidates"],
    )
    unsafe_payload["safety"]["broker_access"] = True

    unsafe_payload["candidates"] = _repeat_candidate(unsafe_payload["candidates"][0], 20)
    safe_payload["candidates"] = _repeat_candidate(safe_payload["candidates"][0], 20)
    result = run_strategy_portfolio_competition(strategy_competitors=[unsafe_payload, safe_payload])
    assert result["winner"]["strategy_name"] == "DAY_TRADING_BREAKOUT_V1"
    assert any(item["strategy_name"] == "MEAN_REVERSION_V1" and "unsafe_strategy" in item["blocked_reasons"] for item in result["rejected_strategies"])


def test_deterministic_output():
    breakout_candidate = _breakout.generate_day_trading_breakout_candidates(
        symbol="EURUSD",
        session_name="London",
        timeframe="M15",
        high_price=1.105,
        low_price=1.100,
        current_price=1.106,
        risk_percent=1.0,
    )["candidates"][0]
    mean_candidate = _reversion.generate_mean_reversion_candidates(
        symbol="EURUSD",
        session_name="London",
        timeframe="M15",
        moving_average=1.1,
        current_price=1.09,
        deviation_percent=0.5,
        risk_percent=1.0,
    )["candidates"][0]
    first = run_strategy_portfolio_competition(
        strategy_competitors=[
            _build_strategy_payload("day_trading_breakout_v1.py", "DAY_TRADING_BREAKOUT_V1", _repeat_candidate(breakout_candidate, 20)),
            _build_strategy_payload("mean_reversion_v1.py", "MEAN_REVERSION_V1", _repeat_candidate(mean_candidate, 20)),
        ]
    )
    second = run_strategy_portfolio_competition(
        strategy_competitors=[
            _build_strategy_payload("day_trading_breakout_v1.py", "DAY_TRADING_BREAKOUT_V1", _repeat_candidate(breakout_candidate, 20)),
            _build_strategy_payload("mean_reversion_v1.py", "MEAN_REVERSION_V1", _repeat_candidate(mean_candidate, 20)),
        ]
    )
    assert first == second


def test_safety_source_scan():
    source = inspect.getsource(__import__("automation.forex_engine.strategy_portfolio_competition_runner", fromlist=["*"]))
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

    safety = run_strategy_portfolio_competition(strategy_competitors=[])["safety"]
    assert safety["paper_only"] is True
    assert safety["broker_access"] is False
    assert safety["credentials_access"] is False
    assert safety["network_access"] is False
    assert safety["live_trading_active"] is False
    assert safety["demo_execution_active"] is False
    assert safety["capital_allocation_modified"] is False
