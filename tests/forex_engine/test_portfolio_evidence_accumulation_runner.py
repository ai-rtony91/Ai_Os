"""Tests for portfolio evidence accumulation runner."""
from __future__ import annotations

import importlib.util
import inspect
from pathlib import Path

from automation.forex_engine.portfolio_evidence_accumulation_runner import (
    run_portfolio_evidence_accumulation_runner,
)

BASE_PATH = Path(__file__).resolve().parents[2] / "automation" / "forex_engine" / "strategies"


def _load_strategy_module(name: str):
    module_path = BASE_PATH / name
    spec = importlib.util.spec_from_file_location(module_path.stem, module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


_breakout = _load_strategy_module("day_trading_breakout_v1.py")
_mean_reversion = _load_strategy_module("mean_reversion_v1.py")


def _safe_candidate_payload():
    return {"paper_only": True, "broker_access": False, "credentials_access": False, "network_access": False, "live_trading_active": False}


def _build_payload(strategy_module, strategy_name: str, candidates):
    return {
        "strategy_name": strategy_name,
        "strategy_version": "v1",
        "safety": _safe_candidate_payload(),
        "candidates": candidates,
    }


def _repeat_candidate(candidate: dict[str, object], count: int):
    return [dict(candidate | {"trade_id": f"trade-{index:04d}"}) for index in range(1, count + 1)]


def _batch_candidates(
    breakout_pl: float = 50.0,
    mean_pl: float = 10.0,
    safe: bool = True,
):
    breakout_candidate = _breakout.generate_day_trading_breakout_candidates(
        symbol="EURUSD",
        session_name="London",
        timeframe="M15",
        high_price=1.105,
        low_price=1.100,
        current_price=1.106,
        risk_percent=2.0,
    )["candidates"][0]

    mean_candidate = _mean_reversion.generate_mean_reversion_candidates(
        symbol="EURUSD",
        session_name="London",
        timeframe="M15",
        moving_average=1.1,
        current_price=1.09,
        deviation_percent=0.5,
        risk_percent=1.0,
    )["candidates"][0]

    breakout_candidate["realized_pl"] = breakout_pl
    mean_candidate["realized_pl"] = mean_pl

    batch = [
        _build_payload(
            "day_trading_breakout_v1.py",
            "DAY_TRADING_BREAKOUT_V1",
            _repeat_candidate(breakout_candidate, 20),
        ),
        _build_payload(
            "mean_reversion_v1.py",
            "MEAN_REVERSION_V1",
            _repeat_candidate(mean_candidate, 20),
        ),
    ]
    if not safe:
        batch[1]["safety"]["broker_access"] = True
    return batch


def test_stable_winner_across_batches():
    result = run_portfolio_evidence_accumulation_runner(
        evidence_batches=[
            {"strategy_competitors": _batch_candidates(60.0, 10.0)},
            {"strategy_competitors": _batch_candidates(65.0, 15.0)},
            {"strategy_competitors": _batch_candidates(55.0, 12.0)},
        ],
        minimum_batches=3,
        winner_consistency_threshold=0.67,
    )
    assert result["accumulation_completed"] is True
    assert result["batches_evaluated"] == 3
    assert result["portfolio_ready"] is True
    assert result["winner_consistency_rate"] == 1.0
    assert result["stable_winner"]["strategy_name"] == "DAY_TRADING_BREAKOUT_V1"


def test_unstable_winners_blocked():
    result = run_portfolio_evidence_accumulation_runner(
        evidence_batches=[
            {"strategy_competitors": _batch_candidates(20.0, 5.0)},
            {"strategy_competitors": _batch_candidates(2.0, 35.0)},
            {"strategy_competitors": _batch_candidates(18.0, 4.0)},
        ],
        minimum_batches=3,
        winner_consistency_threshold=0.8,
    )
    assert result["portfolio_ready"] is False
    assert result["stable_winner"]["strategy_name"] in {"DAY_TRADING_BREAKOUT_V1", "MEAN_REVERSION_V1"}
    assert 0.0 < result["winner_consistency_rate"] < 1.0
    assert result["winner_consistency_rate"] < 0.8
    assert "winner_consistency_below_threshold" in result["blocked_reasons"]


def test_all_batches_rejected():
    result = run_portfolio_evidence_accumulation_runner(
        evidence_batches=[
            {"strategy_competitors": _batch_candidates(-75.0, -20.0)},
            {"strategy_competitors": _batch_candidates(-90.0, -45.0)},
            {"strategy_competitors": _batch_candidates(-60.0, -30.0)},
        ],
        minimum_batches=3,
    )
    assert result["portfolio_ready"] is False
    assert result["stable_winner"] == {}
    assert result["winner_consistency_rate"] == 0.0
    assert "no_stable_winner" in result["blocked_reasons"]
    assert "all_batches_failed" in result["blocked_reasons"]


def test_unsafe_strategy_blocked():
    unsafe_batch = _batch_candidates(18.0, 12.0, safe=False)
    safe_batch = _batch_candidates(40.0, 5.0)
    result = run_portfolio_evidence_accumulation_runner(
        evidence_batches=[
            {"strategy_competitors": [unsafe_batch[1], safe_batch[0]]},
        ],
        minimum_batches=1,
    )
    assert result["accumulation_completed"] is True
    assert result["portfolio_ready"] is True
    assert result["stable_winner"]["strategy_name"] == "DAY_TRADING_BREAKOUT_V1"
    assert not any(
        item.get("winner", {}).get("strategy_name") == "MEAN_REVERSION_V1" and "unsafe_strategy" in item.get("blocked_reasons", [])
        for item in result["competition_results"]
    )


def test_insufficient_batches():
    result = run_portfolio_evidence_accumulation_runner(
        evidence_batches=[{"strategy_competitors": _batch_candidates(30.0, 10.0)}],
        minimum_batches=3,
    )
    assert result["batches_evaluated"] == 1
    assert result["portfolio_ready"] is False
    assert "insufficient_batches" in result["blocked_reasons"]
    assert result["winner_consistency_rate"] == 1.0

def test_deterministic_output():
    batches = [
        {"strategy_competitors": _batch_candidates(35.0, 10.0)},
        {"strategy_competitors": _batch_candidates(28.0, 8.0)},
        {"strategy_competitors": _batch_candidates(42.0, 11.0)},
    ]
    first = run_portfolio_evidence_accumulation_runner(
        evidence_batches=batches,
        minimum_batches=3,
    )
    second = run_portfolio_evidence_accumulation_runner(
        evidence_batches=batches,
        minimum_batches=3,
    )
    assert first == second


def test_safety_source_scan():
    source = inspect.getsource(
        __import__("automation.forex_engine.portfolio_evidence_accumulation_runner", fromlist=["*"])
    )
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

    safety = run_portfolio_evidence_accumulation_runner(evidence_batches=[])["safety"]
    assert safety["paper_only"] is True
    assert safety["broker_access"] is False
    assert safety["credentials_access"] is False
    assert safety["network_access"] is False
    assert safety["live_trading_active"] is False
    assert safety["demo_execution_active"] is False
    assert safety["capital_allocation_modified"] is False
