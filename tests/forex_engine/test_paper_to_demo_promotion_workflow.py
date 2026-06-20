"""Tests for paper-to-demo promotion workflow."""
from __future__ import annotations

import inspect

from automation.forex_engine import paper_to_demo_promotion_workflow as workflow


def _ledger(pnls: list[float], risk: float = 100.0) -> dict:
    return {
        "session_id": "paper-session-test",
        "events": [
            {
                "event_id": f"evt-{index:04d}",
                "event_type": "paper_trade_closed",
                "payload": {"trade_id": f"t-{index}", "realized_pl": pnl, "risk_dollars": risk},
                "paper_only": True,
            }
            for index, pnl in enumerate(pnls, start=1)
        ],
        "paper_only": True,
    }


def _replay(pnls: list[float]) -> dict:
    return {
        "session_id": "paper-session-test",
        "starting_balance": 10000.0,
        "ending_balance": round(10000.0 + sum(pnls), 8),
        "closed_trades": [{"realized_pl": pnl, "risk_dollars": 100.0} for pnl in pnls],
        "paper_only": True,
    }


def test_profitable_candidate_workflow():
    pnls = [200.0, -100.0, 150.0, -50.0, 125.0, 75.0]
    result = workflow.run_paper_to_demo_promotion_workflow(_ledger(pnls), _replay(pnls))
    assert result["workflow_completed"] is True
    assert result["demo_candidate"] is True
    assert result["promotion_status"] == "DEMO_CANDIDATE"
    assert result["blocked_reasons"] == []
    assert result["evidence_references"]["ledger_event_count"] == 6
    assert result["evidence_references"]["session_id"] == "paper-session-test"


def test_blocked_workflow():
    pnls = [-100.0, -50.0, 25.0, -75.0, -25.0]
    result = workflow.run_paper_to_demo_promotion_workflow(_ledger(pnls), _replay(pnls))
    assert result["workflow_completed"] is True
    assert result["demo_candidate"] is False
    assert result["promotion_status"] == "REJECTED"
    assert "negative_expectancy" in result["blocked_reasons"]


def test_insufficient_sample_workflow():
    pnls = [200.0, -50.0]
    result = workflow.run_paper_to_demo_promotion_workflow(_ledger(pnls), _replay(pnls))
    assert result["promotion_status"] == "MORE_EVIDENCE_REQUIRED"
    assert "insufficient_sample_size" in result["blocked_reasons"]
    assert result["next_safe_action"] == "continue_paper_trading_collect_more_evidence"


def test_failed_evidence_workflow():
    result = workflow.run_paper_to_demo_promotion_workflow()
    assert result["promotion_status"] == "MORE_EVIDENCE_REQUIRED"
    assert result["demo_candidate"] is False
    assert "missing_ledger_evidence" in result["blocked_reasons"]
    assert "missing_replay_evidence" in result["blocked_reasons"]
    assert result["evidence_references"]["replay_present"] is False


def test_promotion_gate_blocked_workflow():
    pnls = [200.0, -100.0, 150.0, -50.0, 125.0, 75.0]
    result = workflow.run_paper_to_demo_promotion_workflow(
        _ledger(pnls),
        _replay(pnls),
        promotion_limits={"minimum_profit_factor": 10.0},
    )
    assert result["workflow_completed"] is True
    assert result["profitability_result"]["profitability_ready"] is True
    assert result["promotion_status"] == "REJECTED"
    assert result["demo_candidate"] is False
    assert "profit_factor_below_threshold" in result["blocked_reasons"]
    assert result["next_safe_action"] == "reject_strategy_or_rework_edge"


def test_deterministic_output():
    pnls = [200.0, -100.0, 150.0, -50.0, 125.0, 75.0]
    first = workflow.run_paper_to_demo_promotion_workflow(_ledger(pnls), _replay(pnls))
    second = workflow.run_paper_to_demo_promotion_workflow(_ledger(pnls), _replay(pnls))
    assert first == second


def test_can_consume_precomputed_evaluator_output():
    evaluator_result = {
        "profitability_ready": True,
        "sample_size_met": True,
        "expectancy_per_trade": 40.0,
        "expectancy_r": 0.4,
        "profit_factor": 2.0,
        "win_rate_pct": 60.0,
        "average_win": 120.0,
        "average_loss": 80.0,
        "max_drawdown": 200.0,
        "risk_quality_passed": True,
        "evidence_quality_passed": True,
        "blocked_reasons": [],
    }
    result = workflow.run_paper_to_demo_promotion_workflow(profitability_result=evaluator_result)
    assert result["demo_candidate"] is True
    assert result["profitability_result"] == evaluator_result


def test_safety_boundary_enforcement():
    result = workflow.run_paper_to_demo_promotion_workflow()
    safety = result["safety"]
    assert safety["paper_only"] is True
    assert safety["demo_review_only"] is True
    assert safety["submit_orders"] is False
    assert safety["broker_access"] is False
    assert safety["credentials_access"] is False
    assert safety["network_api_access"] is False
    assert safety["demo_execution_active"] is False
    assert safety["live_execution_active"] is False
    assert safety["capital_allocation_modified"] is False
    assert safety["real_orders"] is False


def test_source_has_no_forbidden_runtime_apis():
    source = inspect.getsource(workflow)
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
