"""Tests for demo validation result aggregator."""
from __future__ import annotations

import importlib.util
import inspect
from pathlib import Path

from automation.forex_engine.demo_validation_result_aggregator import (
    RECOMMENDATION_DEMO_VALIDATION_FAILED,
    RECOMMENDATION_DEMO_VALIDATION_PASSED,
    RECOMMENDATION_MORE_EVIDENCE_REQUIRED,
    run_demo_validation_result_aggregator,
)
from automation.forex_engine.portfolio_promotion_decision_engine import (
    DECISION_DEMO_REVIEW_CANDIDATE,
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


def _review_payload(
    status: str = DECISION_DEMO_REVIEW_CANDIDATE,
    winner: dict[str, object] | None = None,
    consistency: float = 0.75,
    ready: bool = True,
    blocked: list[str] | None = None,
    safety: dict[str, object] | None = None,
) -> dict[str, object]:
    return {
        "readiness_completed": True,
        "demo_review_ready": ready,
        "portfolio_promotion_status": status,
        "stable_winner": winner or {},
        "winner_consistency_rate": consistency,
        "blocked_reasons": blocked or [],
        "next_safe_action": "test",
        "safety": safety or _safe_payload(),
    }


def _scorecard_payload(
    passed: bool = True,
    completed: bool = True,
    score: float = 80.0,
    status: str = DECISION_DEMO_REVIEW_CANDIDATE,
    winner: dict[str, object] | None = None,
    reasons: list[str] | None = None,
    safety: dict[str, object] | None = None,
) -> dict[str, object]:
    return {
        "scorecard_completed": completed,
        "scorecard_passed": passed,
        "demo_validation_score": score,
        "stable_winner": winner or {},
        "portfolio_promotion_status": status,
        "demo_review_ready": True,
        "blocked_reasons": reasons or [],
        "next_safe_action": "test",
        "safety": safety or _safe_payload(),
    }


def test_validation_passed():
    result = run_demo_validation_result_aggregator(
        scorecard_result=_scorecard_payload(
            passed=True,
            completed=True,
            score=85.0,
            winner={"strategy_name": "DAY_TRADING_BREAKOUT_V1", "safety": _safe_payload()},
        ),
        demo_review_result=_review_payload(
            winner={"strategy_name": "DAY_TRADING_BREAKOUT_V1", "safety": _safe_payload()},
        ),
    )
    assert result["aggregation_completed"] is True
    assert result["demo_validation_passed"] is True
    assert result["demo_review_ready"] is True
    assert result["scorecard_passed"] is True
    assert result["promotion_recommendation"] == RECOMMENDATION_DEMO_VALIDATION_PASSED
    assert result["demo_validation_score"] == 85.0
    assert result["safety"]["paper_only"] is True


def test_validation_failed():
    result = run_demo_validation_result_aggregator(
        scorecard_result=_scorecard_payload(
            passed=False,
            completed=True,
            score=0.0,
            winner={"strategy_name": "DAY_TRADING_BREAKOUT_V1", "safety": _safe_payload()},
        ),
        demo_review_result=_review_payload(ready=True, winner={"strategy_name": "DAY_TRADING_BREAKOUT_V1", "safety": _safe_payload()}),
    )
    assert result["demo_validation_passed"] is False
    assert result["scorecard_passed"] is False
    assert result["promotion_recommendation"] == RECOMMENDATION_DEMO_VALIDATION_FAILED
    assert result["stable_winner"]["strategy_name"] == "DAY_TRADING_BREAKOUT_V1"


def test_missing_stable_winner():
    result = run_demo_validation_result_aggregator(
        scorecard_result=_scorecard_payload(
            passed=True,
            completed=True,
            score=74.0,
            winner={},
        ),
        demo_review_result=_review_payload(winner={}),
    )
    assert result["demo_validation_passed"] is False
    assert "missing_stable_winner" in result["blocked_reasons"]
    assert result["promotion_recommendation"] == RECOMMENDATION_MORE_EVIDENCE_REQUIRED


def test_failed_scorecard():
    result = run_demo_validation_result_aggregator(
        scorecard_result=_scorecard_payload(
            passed=False,
            completed=False,
            score=55.0,
            winner={"strategy_name": "DAY_TRADING_BREAKOUT_V1", "safety": _safe_payload()},
        ),
        demo_review_result=_review_payload(),
    )
    assert result["scorecard_passed"] is False
    assert result["demo_validation_passed"] is False
    assert "scorecard_not_completed" in result["blocked_reasons"] or "scorecard_failed" in result["blocked_reasons"]


def test_failed_readiness():
    result = run_demo_validation_result_aggregator(
        scorecard_result=_scorecard_payload(winner={"strategy_name": "DAY_TRADING_BREAKOUT_V1", "safety": _safe_payload()}),
        demo_review_result=_review_payload(ready=False),
    )
    assert result["demo_review_ready"] is False
    assert result["demo_validation_passed"] is False
    assert "demo_review_not_ready" in result["blocked_reasons"]
    assert result["promotion_recommendation"] == RECOMMENDATION_MORE_EVIDENCE_REQUIRED


def test_missing_promotion_approval():
    result = run_demo_validation_result_aggregator(
        scorecard_result=_scorecard_payload(
            passed=True,
            completed=True,
            status="PORTFOLIO_MORE_EVIDENCE_REQUIRED",
            winner={"strategy_name": "DAY_TRADING_BREAKOUT_V1", "safety": _safe_payload()},
        ),
        demo_review_result=_review_payload(status="PORTFOLIO_MORE_EVIDENCE_REQUIRED", winner={"strategy_name": "DAY_TRADING_BREAKOUT_V1", "safety": _safe_payload()}),
    )
    assert result["portfolio_promotion_status"] == "PORTFOLIO_MORE_EVIDENCE_REQUIRED"
    assert result["demo_validation_passed"] is False
    assert any(reason.startswith("portfolio_promotion_status_not_candidate") for reason in result["blocked_reasons"])


def test_deterministic_output():
    payload = {
        "demo_review_result": _review_payload(
            winner={"strategy_name": "DAY_TRADING_BREAKOUT_V1", "safety": _safe_payload()},
            consistency=0.77,
        ),
        "scorecard_result": _scorecard_payload(
            passed=True,
            completed=True,
            score=81.0,
            winner={"strategy_name": "DAY_TRADING_BREAKOUT_V1", "safety": _safe_payload()},
        ),
    }
    first = run_demo_validation_result_aggregator(**payload)
    second = run_demo_validation_result_aggregator(**payload)
    assert first == second


def test_safety_source_scan():
    source = inspect.getsource(__import__("automation.forex_engine.demo_validation_result_aggregator", fromlist=["*"]))
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
