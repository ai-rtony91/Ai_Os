"""Tests for deterministic paper-session sample generation."""
from __future__ import annotations

import inspect

from automation.forex_engine import paper_session_sample_generator as generator


def test_profitable_sample_becomes_demo_candidate():
    result = generator.generate_paper_session_sample([200.0, -100.0, 150.0, -50.0, 125.0, 75.0])
    assert result["sample_generated"] is True
    assert result["demo_candidate"] is True
    assert result["promotion_status"] == "DEMO_CANDIDATE"
    assert result["blocked_reasons"] == []
    assert result["profitability_result"]["expectancy_per_trade"] == 66.66666667
    assert len(result["paper_trade_ledger"]["events"]) == 36
    assert len(result["replay_evidence"]["closed_trades"]) == 6
    assert result["workflow_result"]["workflow_completed"] is True


def test_losing_sample_is_rejected():
    result = generator.generate_paper_session_sample([-100.0, -50.0, 25.0, -75.0, -25.0])
    assert result["demo_candidate"] is False
    assert result["promotion_status"] == "REJECTED"
    assert "negative_expectancy" in result["blocked_reasons"]
    assert "profit_factor_below_threshold" in result["blocked_reasons"]
    assert result["profitability_result"]["expectancy_per_trade"] == -45.0


def test_breakeven_heavy_sample_is_supported():
    result = generator.generate_paper_session_sample(
        [100.0, -50.0, 0.0, 0.0, 0.0],
        promotion_limits={"minimum_profit_factor": 1.0},
    )
    assert result["demo_candidate"] is True
    assert result["promotion_status"] == "DEMO_CANDIDATE"
    assert result["profitability_result"]["metrics"]["breakeven"] == 3
    assert result["profitability_result"]["expectancy_per_trade"] == 10.0


def test_insufficient_sample_requires_more_evidence():
    result = generator.generate_paper_session_sample([200.0, -50.0])
    assert result["demo_candidate"] is False
    assert result["promotion_status"] == "MORE_EVIDENCE_REQUIRED"
    assert "insufficient_sample_size" in result["blocked_reasons"]
    assert result["next_safe_action"] == "continue_paper_trading_collect_more_evidence"


def test_excessive_drawdown_sample_blocks_even_when_profitable():
    result = generator.generate_paper_session_sample([300.0, -900.0, 400.0, 300.0, 200.0])
    assert result["demo_candidate"] is False
    assert result["promotion_status"] == "REJECTED"
    assert result["profitability_result"]["expectancy_per_trade"] == 60.0
    assert result["profitability_result"]["max_drawdown"] == 900.0
    assert "excessive_drawdown" in result["blocked_reasons"]


def test_deterministic_repeated_output():
    sample = [200.0, -100.0, 150.0, -50.0, 125.0, 75.0]
    first = generator.generate_paper_session_sample(sample)
    second = generator.generate_paper_session_sample(sample)
    assert first == second


def test_safety_boundary_enforced():
    result = generator.generate_paper_session_sample([200.0, -100.0, 150.0, -50.0, 125.0, 75.0])
    safety = result["safety"]
    assert safety["paper_only"] is True
    assert safety["sample_generation_only"] is True
    assert safety["broker_access"] is False
    assert safety["network_api_access"] is False
    assert safety["credentials_access"] is False
    assert safety["demo_execution_active"] is False
    assert safety["live_execution_active"] is False
    assert safety["capital_allocation_modified"] is False
    assert safety["orders_submitted"] is False
    assert safety["real_orders"] is False


def test_source_has_no_forbidden_runtime_apis():
    source = inspect.getsource(generator)
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
