"""Tests for demo review readiness engine."""
from __future__ import annotations

import importlib.util
import inspect
from pathlib import Path

from automation.forex_engine.demo_review_readiness_engine import run_demo_review_readiness_engine
from automation.forex_engine.portfolio_evidence_accumulation_runner import DEFAULT_MIN_WINNER_CONSISTENCY

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


def _build_payload(strategy_name: str, candidate_data: list[dict[str, object]]):
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
        _build_payload("DAY_TRADING_BREAKOUT_V1", _repeat_candidate(breakout_candidate, 20)),
        _build_payload("MEAN_REVERSION_V1", _repeat_candidate(mean_candidate, 20)),
    ]
    if unsafe:
        batch[1]["safety"]["broker_access"] = True
    return batch


def _make_promotion_payload(
    status: str,
    stable_winner: dict[str, object] | None = None,
    consistency: float = DEFAULT_MIN_WINNER_CONSISTENCY,
    blocked_reasons: list[str] | None = None,
) -> dict[str, object]:
    return {
        "decision_completed": True,
        "portfolio_promotion_status": status,
        "demo_review_candidate": status == "PORTFOLIO_DEMO_REVIEW_CANDIDATE",
        "stable_winner": stable_winner or {},
        "winner_consistency_rate": consistency,
        "blocked_reasons": blocked_reasons or [],
        "promotion_reasons": [],
        "next_safe_action": "test",
        "safety": _safe_payload(),
    }


def test_demo_review_ready():
    result = run_demo_review_readiness_engine(
        evidence_batches=[
            {"strategy_competitors": _make_batch(70.0, 8.0)},
            {"strategy_competitors": _make_batch(65.0, 4.0)},
            {"strategy_competitors": _make_batch(72.0, 6.0)},
        ],
    )
    assert result["readiness_completed"] is True
    assert result["demo_review_ready"] is True
    assert result["portfolio_promotion_status"] == "PORTFOLIO_DEMO_REVIEW_CANDIDATE"
    assert result["stable_winner"].get("strategy_name") == "DAY_TRADING_BREAKOUT_V1"


def test_more_evidence_required():
    result = run_demo_review_readiness_engine(
        evidence_batches=[{"strategy_competitors": _make_batch(40.0, 5.0)}],
        minimum_batches=3,
    )
    assert result["demo_review_ready"] is False
    assert result["portfolio_promotion_status"] == "PORTFOLIO_MORE_EVIDENCE_REQUIRED"
    assert "insufficient_batches" in result["readiness_reasons"] or "collect_more_evidence_before_demo" in result["readiness_reasons"]


def test_portfolio_rejected():
    result = run_demo_review_readiness_engine(
        promotion_result=_make_promotion_payload(
            status="PORTFOLIO_REJECTED",
            stable_winner={},
            consistency=0.0,
        )
    )
    assert result["demo_review_ready"] is False
    assert result["portfolio_promotion_status"] == "PORTFOLIO_REJECTED"


def test_unstable_winner_blocked():
    result = run_demo_review_readiness_engine(
        promotion_result=_make_promotion_payload(
            status="PORTFOLIO_MORE_EVIDENCE_REQUIRED",
            stable_winner={"strategy_name": "DAY_TRADING_BREAKOUT_V1", "safety": _safe_payload()},
            consistency=0.3,
            blocked_reasons=["winner_consistency_below_threshold"],
        )
    )
    assert result["demo_review_ready"] is False
    assert result["portfolio_promotion_status"] == "PORTFOLIO_MORE_EVIDENCE_REQUIRED"
    assert "winner_consistency_below_threshold" in result["blocked_reasons"]


def test_unsafe_evidence_blocked():
    unsafe_winner = {
        "strategy_name": "DAY_TRADING_BREAKOUT_V1",
        "strategy_version": "v1",
        "safety": {
            "paper_only": True,
            "broker_access": True,
            "credentials_access": False,
            "network_access": False,
            "live_trading_active": False,
            "demo_execution_active": False,
            "capital_allocation_modified": False,
        },
        "blocked_reasons": [],
    }
    result = run_demo_review_readiness_engine(
        promotion_result=_make_promotion_payload(
            status="PORTFOLIO_DEMO_REVIEW_CANDIDATE",
            stable_winner=unsafe_winner,
            consistency=0.8,
        )
    )
    assert result["demo_review_ready"] is False
    assert result["portfolio_promotion_status"] == "PORTFOLIO_DEMO_REVIEW_CANDIDATE"
    assert "unsafe_or_negative_winner_evidence" in result["blocked_reasons"]


def test_missing_stable_winner_blocked():
    result = run_demo_review_readiness_engine(
        promotion_result=_make_promotion_payload(
            status="PORTFOLIO_DEMO_REVIEW_CANDIDATE",
            stable_winner={},
            consistency=0.8,
        )
    )
    assert result["demo_review_ready"] is False
    assert "missing_stable_winner" in result["blocked_reasons"]


def test_deterministic_output():
    payload = {
        "evidence_batches": [
            {"strategy_competitors": _make_batch(45.0, 5.0)},
            {"strategy_competitors": _make_batch(45.0, 5.0)},
            {"strategy_competitors": _make_batch(45.0, 5.0)},
        ],
    }
    first = run_demo_review_readiness_engine(**payload)
    second = run_demo_review_readiness_engine(**payload)
    assert first == second


def test_safety_source_scan():
    source = inspect.getsource(__import__("automation.forex_engine.demo_review_readiness_engine", fromlist=["*"]))
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

    result = run_demo_review_readiness_engine(
        evidence_batches=[{"strategy_competitors": _make_batch(48.0, 5.0)}],
        minimum_batches=1,
        winner_consistency_threshold=0.2,
    )
    safety = result["safety"]
    assert safety["paper_only"] is True
    assert safety["broker_access"] is False
    assert safety["credentials_access"] is False
    assert safety["network_access"] is False
    assert safety["live_trading_active"] is False
    assert safety["demo_execution_active"] is False
    assert safety["capital_allocation_modified"] is False
