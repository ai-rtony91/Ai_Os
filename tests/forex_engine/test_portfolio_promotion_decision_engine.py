"""Tests for portfolio promotion decision engine."""
from __future__ import annotations

import importlib.util
import inspect
from pathlib import Path

from automation.forex_engine.portfolio_promotion_decision_engine import run_portfolio_promotion_decision_engine

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


def _safe_payload():
    return {
        "paper_only": True,
        "broker_access": False,
        "credentials_access": False,
        "network_access": False,
        "live_trading_active": False,
        "demo_execution_active": False,
        "capital_allocation_modified": False,
    }


def _build_batch_payload(strategy_name: str, candidate_data: dict[str, object]):
    return {
        "strategy_name": strategy_name,
        "strategy_version": "v1",
        "safety": _safe_payload(),
        "candidates": candidate_data,
    }


def _repeat_candidate(candidate: dict[str, object], count: int):
    return [dict(candidate | {"trade_id": f"trade-{index:04d}"}) for index in range(1, count + 1)]


def _make_batch(breakout_pl: float, mean_pl: float, unsafe: bool = False):
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
        _build_batch_payload("DAY_TRADING_BREAKOUT_V1", _repeat_candidate(breakout_candidate, 20)),
        _build_batch_payload("MEAN_REVERSION_V1", _repeat_candidate(mean_candidate, 20)),
    ]
    if unsafe:
        batch[1]["safety"]["broker_access"] = True
    return batch


def test_demo_review_candidate():
    result = run_portfolio_promotion_decision_engine(
        evidence_batches=[
            {"strategy_competitors": _make_batch(60.0, 10.0)},
            {"strategy_competitors": _make_batch(58.0, 9.0)},
            {"strategy_competitors": _make_batch(65.0, 8.0)},
        ]
    )
    assert result["portfolio_promotion_status"] == "PORTFOLIO_DEMO_REVIEW_CANDIDATE"
    assert result["demo_review_candidate"] is True
    assert result["stable_winner"]["strategy_name"] == "DAY_TRADING_BREAKOUT_V1"


def test_more_evidence_required():
    result = run_portfolio_promotion_decision_engine(evidence_batches=[{"strategy_competitors": _make_batch(35.0, 10.0)}], minimum_batches=3)
    assert result["portfolio_promotion_status"] == "PORTFOLIO_MORE_EVIDENCE_REQUIRED"
    assert result["demo_review_candidate"] is False
    assert "insufficient_batches" in result["blocked_reasons"]


def test_rejected_no_safe_winner():
    result = run_portfolio_promotion_decision_engine(
        evidence_batches=[
            {"strategy_competitors": _make_batch(-75.0, -80.0)},
            {"strategy_competitors": _make_batch(-30.0, -40.0)},
            {"strategy_competitors": _make_batch(-60.0, -90.0)},
        ],
        minimum_batches=3,
    )
    assert result["portfolio_promotion_status"] == "PORTFOLIO_REJECTED"
    assert result["stable_winner"] == {}


def test_rejected_unsafe_evidence():
    unsafe_winner = {
        "portfolio_ready": False,
        "winner_consistency_rate": 1.0,
        "stable_winner": {
            "strategy_name": "DAY_TRADING_BREAKOUT_V1",
            "strategy_version": "v1",
            "blocked_reasons": ["unsafe_strategy"],
            "safety": {
                "paper_only": True,
                "broker_access": True,
                "credentials_access": False,
                "network_access": False,
                "live_trading_active": False,
                "demo_execution_active": False,
                "capital_allocation_modified": False,
            },
        },
        "blocked_reasons": [],
        "competition_results": [],
        "batches_evaluated": 3,
        "accumulation_completed": True,
        "next_safe_action": "collect_more_evidence",
    }
    result = run_portfolio_promotion_decision_engine(accumulation_result=unsafe_winner)
    assert result["portfolio_promotion_status"] == "PORTFOLIO_REJECTED"
    assert result["demo_review_candidate"] is False


def test_unstable_winner_blocked():
    result = run_portfolio_promotion_decision_engine(
        evidence_batches=[
            {"strategy_competitors": _make_batch(10.0, 2.0)},
            {"strategy_competitors": _make_batch(10.0, 15.0)},
            {"strategy_competitors": _make_batch(10.0, 2.0)},
        ],
        winner_consistency_threshold=0.9,
        minimum_batches=3,
    )
    assert result["portfolio_promotion_status"] == "PORTFOLIO_MORE_EVIDENCE_REQUIRED"
    assert result["winner_consistency_rate"] < 0.9
    assert "winner_consistency_below_threshold" in result["blocked_reasons"]


def test_deterministic_output():
    batch = [
        {"strategy_competitors": _make_batch(40.0, 3.0)},
        {"strategy_competitors": _make_batch(52.0, 1.0)},
        {"strategy_competitors": _make_batch(45.0, 6.0)},
    ]
    first = run_portfolio_promotion_decision_engine(evidence_batches=batch)
    second = run_portfolio_promotion_decision_engine(evidence_batches=batch)
    assert first == second


def test_safety_source_scan():
    source = inspect.getsource(__import__("automation.forex_engine.portfolio_promotion_decision_engine", fromlist=["*"]))
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

    result = run_portfolio_promotion_decision_engine(
        evidence_batches=[{"strategy_competitors": _make_batch(60.0, 10.0)}],
        minimum_batches=1,
        winner_consistency_threshold=0.1,
    )
    safety = result["safety"]
    assert safety["paper_only"] is True
    assert safety["broker_access"] is False
    assert safety["credentials_access"] is False
    assert safety["network_access"] is False
    assert safety["live_trading_active"] is False
    assert safety["demo_execution_active"] is False
    assert safety["capital_allocation_modified"] is False
