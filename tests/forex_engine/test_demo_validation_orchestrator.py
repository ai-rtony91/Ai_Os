"""Tests for demo validation orchestrator."""
from __future__ import annotations

import importlib.util
import inspect
from pathlib import Path

from automation.forex_engine.demo_validation_orchestrator import run_demo_validation_orchestrator

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
        batch[0]["safety"]["broker_access"] = True
    return batch


def test_demo_validation_ready():
    result = run_demo_validation_orchestrator(
        evidence_batches=[
            {"strategy_competitors": _make_batch(75.0, 10.0)},
            {"strategy_competitors": _make_batch(72.0, 8.0)},
            {"strategy_competitors": _make_batch(74.0, 9.0)},
        ],
        winner_consistency_threshold=0.67,
    )

    assert result["orchestration_completed"] is True
    assert result["demo_validation_ready"] is True
    assert result["demo_review_ready"] is True
    assert result["validation_plan"]["validation_stage"] == "PAPER_DEMO_VALIDATION"
    assert result["validation_plan"]["strategy_name"] == "DAY_TRADING_BREAKOUT_V1"


def test_demo_review_not_ready_blocked():
    result = run_demo_validation_orchestrator(
        evidence_batches=[{"strategy_competitors": _make_batch(40.0, 5.0)}],
        minimum_batches=3,
        winner_consistency_threshold=0.67,
    )

    assert result["demo_validation_ready"] is False
    assert result["demo_review_ready"] is False
    assert "demo_review_not_ready" in result["blocked_reasons"]
    assert "demo_review_status_not_candidate" in result["blocked_reasons"]
    assert result["next_safe_action"] == "complete_demo_review_readiness"


def test_missing_stable_winner_blocked():
    result = run_demo_validation_orchestrator(
        demo_review_result={
            "readiness_completed": True,
            "demo_review_ready": True,
            "portfolio_promotion_status": "PORTFOLIO_DEMO_REVIEW_CANDIDATE",
            "stable_winner": {},
            "winner_consistency_rate": 0.95,
            "blocked_reasons": [],
            "next_safe_action": "collect_more_evidence",
            "safety": _safe_payload(),
        }
    )

    assert result["demo_validation_ready"] is False
    assert result["demo_review_ready"] is True
    assert "missing_stable_winner" in result["blocked_reasons"]
    assert result["next_safe_action"] == "collect_more_evidence_until_stable_winner"


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
    result = run_demo_validation_orchestrator(
        demo_review_result={
            "readiness_completed": True,
            "demo_review_ready": True,
            "portfolio_promotion_status": "PORTFOLIO_DEMO_REVIEW_CANDIDATE",
            "stable_winner": unsafe_winner,
            "winner_consistency_rate": 0.9,
            "blocked_reasons": [],
            "next_safe_action": "submit_demo_review_packet",
            "safety": _safe_payload(),
        }
    )

    assert result["demo_validation_ready"] is False
    assert "unsafe_or_negative_winner_evidence" in result["blocked_reasons"]
    assert result["next_safe_action"] == "fix_unsafe_winner_evidence_before_validation"


def test_validation_plan_shape():
    result = run_demo_validation_orchestrator(
        evidence_batches=[
            {"strategy_competitors": _make_batch(68.0, 11.0)},
            {"strategy_competitors": _make_batch(70.0, 13.0)},
            {"strategy_competitors": _make_batch(67.0, 9.0)},
        ],
        winner_consistency_threshold=0.67,
    )

    required_fields = {
        "strategy_name",
        "strategy_version",
        "validation_stage",
        "required_observations",
        "required_trade_count",
        "required_evidence_fields",
        "risk_controls_required",
        "operator_approval_required",
        "broker_connection_required_later",
        "credentials_required_later",
        "demo_execution_active",
    }
    assert set(result["validation_plan"]) >= required_fields
    assert isinstance(result["validation_plan"]["required_observations"], list)
    assert isinstance(result["validation_plan"]["required_evidence_fields"], list)
    assert isinstance(result["validation_plan"]["required_trade_count"], int)
    assert result["validation_plan"]["operator_approval_required"] is True


def test_deterministic_output():
    payload = {
        "evidence_batches": [
            {"strategy_competitors": _make_batch(60.0, 12.0)},
            {"strategy_competitors": _make_batch(66.0, 15.0)},
            {"strategy_competitors": _make_batch(64.0, 8.0)},
        ],
        "winner_consistency_threshold": 0.67,
    }
    first = run_demo_validation_orchestrator(**payload)
    second = run_demo_validation_orchestrator(**payload)
    assert first == second


def test_safety_source_scan():
    source = inspect.getsource(__import__("automation.forex_engine.demo_validation_orchestrator", fromlist=["*"]))
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

    result = run_demo_validation_orchestrator(
        evidence_batches=[{"strategy_competitors": _make_batch(75.0, 11.0)}],
        minimum_batches=1,
        winner_consistency_threshold=0.2,
    )
    assert result["safety"]["paper_only"] is True
    assert result["safety"]["broker_access"] is False
    assert result["safety"]["credentials_access"] is False
    assert result["safety"]["network_access"] is False
    assert result["safety"]["live_trading_active"] is False
    assert result["safety"]["demo_execution_active"] is False
    assert result["safety"]["capital_allocation_modified"] is False
