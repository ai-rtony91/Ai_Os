"""Tests for strategy evaluation harness."""
from __future__ import annotations

import inspect

from automation.forex_engine import strategy_evaluation_harness as harness


def _candidates(pnls: list[float]) -> list[dict]:
    return [
        {
            "trade_id": f"strategy-trade-{index:04d}",
            "symbol": "EURUSD",
            "direction": "buy",
            "entry": 1.1,
            "stop": 1.09,
            "target": 1.12,
            "risk_percent": 1.0,
            "spread": 0.0001,
            "realized_pl": pnl,
            "timestamp": "2026-01-01T00:00:00Z",
        }
        for index, pnl in enumerate(pnls, start=1)
    ]


def test_profitable_strategy_candidate():
    result = harness.evaluate_strategy("Mean Reversion Alpha", "v1", _candidates([200.0, -100.0, 150.0, -50.0, 125.0, 75.0]))
    assert result["strategy_name"] == "Mean Reversion Alpha"
    assert result["strategy_version"] == "v1"
    assert result["total_trades"] == 6
    assert result["demo_candidate"] is True
    assert result["promotion_status"] == "DEMO_REVIEW_CANDIDATE"
    assert result["blocked_reasons"] == []
    assert result["profitability_result"]["profitability_ready"] is True
    assert result["evidence_references"]["closed_trade_count"] == 6
    assert result["evidence_references"]["replay_present"] is True


def test_losing_strategy_candidate_is_rejected():
    result = harness.evaluate_strategy("Losing Breakout", "v2", _candidates([-100.0, -50.0, 25.0, -75.0, -25.0]))
    assert result["strategy_name"] == "Losing Breakout"
    assert result["strategy_version"] == "v2"
    assert result["total_trades"] == 5
    assert result["demo_candidate"] is False
    assert result["promotion_status"] == "REJECTED"
    assert "negative_expectancy" in result["blocked_reasons"]
    assert result["next_safe_action"] == "reject_strategy_or_rework_edge"


def test_insufficient_evidence_strategy_requires_more_paper_evidence():
    result = harness.evaluate_strategy("Early Signal", "v1", _candidates([200.0, -50.0]))
    assert result["total_trades"] == 2
    assert result["demo_candidate"] is False
    assert result["promotion_status"] == "MORE_EVIDENCE_REQUIRED"
    assert "insufficient_sample_size" in result["blocked_reasons"]
    assert result["next_safe_action"] == "continue_paper_trading_collect_more_evidence"


def test_malformed_strategy_candidate_blocks_promotion():
    result = harness.evaluate_strategy(
        "Malformed Strategy",
        "v1",
        [
            {
                "trade_id": "bad-001",
                "symbol": "EURUSD",
                "direction": "sideways",
                "entry": "not-a-price",
                "stop": 1.09,
                "target": 1.12,
                "risk_percent": 1.0,
                "realized_pl": "not-pnl",
            }
        ],
    )
    assert result["total_trades"] == 0
    assert result["demo_candidate"] is False
    assert result["promotion_status"] == "MORE_EVIDENCE_REQUIRED"
    assert "malformed_strategy_candidate" in result["blocked_reasons"]
    assert "evidence_quality_failed" in result["blocked_reasons"]
    assert result["profitability_result"]["evidence_quality_passed"] is False


def test_strategy_can_read_trade_outcomes_from_paper_session_evidence():
    result = harness.evaluate_strategy(
        "Evidence Supplied Strategy",
        "v3",
        paper_session_evidence={"deterministic_trade_outcomes": _candidates([200.0, -100.0, 150.0, -50.0, 125.0, 75.0])},
    )
    assert result["strategy_name"] == "Evidence Supplied Strategy"
    assert result["strategy_version"] == "v3"
    assert result["promotion_status"] == "DEMO_REVIEW_CANDIDATE"
    assert result["evidence_references"]["ledger_event_count"] == 36


def test_deterministic_repeated_output():
    candidates = _candidates([200.0, -100.0, 150.0, -50.0, 125.0, 75.0])
    first = harness.evaluate_strategy("Deterministic Alpha", "v1", candidates)
    second = harness.evaluate_strategy("Deterministic Alpha", "v1", candidates)
    assert first == second


def test_safety_boundary_enforced():
    result = harness.evaluate_strategy("Safety Alpha", "v1", _candidates([200.0, -100.0, 150.0, -50.0, 125.0, 75.0]))
    safety = result["safety"]
    assert safety["paper_only"] is True
    assert safety["strategy_evaluation_only"] is True
    assert safety["broker_api_access"] is False
    assert safety["credentials_access"] is False
    assert safety["orders_submitted"] is False
    assert safety["live_trades_placed"] is False
    assert safety["capital_allocation_modified"] is False
    assert safety["production_deployment_active"] is False
    assert safety["demo_execution_active"] is False
    assert safety["network_api_access"] is False


def test_source_has_no_forbidden_runtime_apis():
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
