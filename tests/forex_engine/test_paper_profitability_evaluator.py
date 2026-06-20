"""Tests for paper profitability evaluator."""
from __future__ import annotations

import inspect

from automation.forex_engine import paper_profitability_evaluator as evaluator


def _ledger(pnls: list[float], risk: float = 100.0) -> dict:
    return {
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
        "starting_balance": 10000.0,
        "ending_balance": round(10000.0 + sum(pnls), 8),
        "closed_trades": [{"realized_pl": pnl, "risk_dollars": 100.0} for pnl in pnls],
        "paper_only": True,
    }


def test_profitable_session_allowed_for_demo_review():
    pnls = [200.0, -100.0, 150.0, -50.0, 125.0, 75.0]
    result = evaluator.evaluate_paper_profitability(_ledger(pnls), _replay(pnls))
    assert result["allowed"] is True
    assert result["decision"] == "REVIEW_FOR_DEMO_VALIDATION"
    assert result["profitability_ready"] is True
    assert result["blocked_reasons"] == []


def test_losing_session_blocks():
    pnls = [-100.0, -50.0, 25.0, -75.0, -25.0]
    result = evaluator.evaluate_paper_profitability(_ledger(pnls), _replay(pnls))
    assert result["allowed"] is False
    assert "negative_expectancy" in result["blocked_reasons"]
    assert "profit_factor_below_threshold" in result["blocked_reasons"]


def test_insufficient_sample_blocks():
    pnls = [200.0, -50.0]
    result = evaluator.evaluate_paper_profitability(_ledger(pnls), _replay(pnls))
    assert result["sample_size_met"] is False
    assert "insufficient_sample_size" in result["blocked_reasons"]


def test_negative_expectancy_blocks():
    pnls = [50.0, -100.0, 50.0, -100.0, 25.0]
    result = evaluator.evaluate_paper_profitability(_ledger(pnls), _replay(pnls))
    assert result["expectancy_per_trade"] < 0
    assert "negative_expectancy" in result["blocked_reasons"]


def test_excessive_drawdown_blocks():
    pnls = [300.0, -100.0, 200.0, -100.0, 150.0]
    balances = [10000.0, 10300.0, 9400.0, 9600.0, 9500.0, 9650.0]
    result = evaluator.evaluate_paper_profitability(
        _ledger(pnls),
        _replay(pnls),
        balance_history=balances,
        limits={"maximum_drawdown": 500.0},
    )
    assert result["max_drawdown"] == 900.0
    assert "excessive_drawdown" in result["blocked_reasons"]


def test_missing_evidence_blocks():
    result = evaluator.evaluate_paper_profitability()
    assert result["allowed"] is False
    assert "missing_ledger_evidence" in result["blocked_reasons"]
    assert "missing_replay_evidence" in result["blocked_reasons"]


def test_metric_correctness():
    pnls = [200.0, -100.0, 100.0, -50.0, 50.0]
    result = evaluator.evaluate_paper_profitability(
        _ledger(pnls),
        _replay(pnls),
        limits={"minimum_profit_factor": 1.0},
    )
    assert result["metrics"]["total_trades"] == 5
    assert result["metrics"]["winners"] == 3
    assert result["metrics"]["losers"] == 2
    assert result["win_rate_pct"] == 60.0
    assert result["average_win"] == 116.66666667
    assert result["average_loss"] == 75.0
    assert result["expectancy_per_trade"] == 40.0
    assert result["expectancy_r"] == 0.4
    assert result["profit_factor"] == 2.33333333
    assert result["metrics"]["gross_profit"] == 350.0
    assert result["metrics"]["gross_loss"] == 150.0
    assert result["metrics"]["consecutive_loss_count"] == 1


def test_breakeven_trades_do_not_create_false_negative_expectancy():
    pnls = [100.0, -50.0, 0.0, 0.0, 0.0]
    result = evaluator.evaluate_paper_profitability(
        _ledger(pnls),
        _replay(pnls),
        limits={"minimum_profit_factor": 1.0},
    )
    assert result["expectancy_per_trade"] == 10.0
    assert result["metrics"]["breakeven"] == 3
    assert result["allowed"] is True


def test_ledger_without_closed_trades_blocks_profitable_replay():
    ledger = {
        "events": [{"event_type": "paper_trade_opened", "payload": {"trade_id": "t-1"}}],
        "paper_only": True,
    }
    result = evaluator.evaluate_paper_profitability(ledger, _replay([200.0, -50.0, 150.0, -50.0, 100.0]))
    assert result["allowed"] is False
    assert "missing_ledger_evidence" in result["blocked_reasons"]
    assert result["evidence_quality_passed"] is False


def test_replay_without_closed_trades_blocks_profitable_ledger():
    pnls = [200.0, -50.0, 150.0, -50.0, 100.0]
    replay = {"starting_balance": 10000.0, "ending_balance": 10350.0, "paper_only": True}
    result = evaluator.evaluate_paper_profitability(_ledger(pnls), replay)
    assert result["allowed"] is False
    assert "missing_replay_evidence" in result["blocked_reasons"]
    assert result["evidence_quality_passed"] is False


def test_inconsistent_ledger_and_replay_blocks_promotion():
    ledger_pnls = [200.0, -50.0, 150.0, -50.0, 100.0]
    replay_pnls = [200.0, -50.0, 150.0, -50.0, -100.0]
    result = evaluator.evaluate_paper_profitability(_ledger(ledger_pnls), _replay(replay_pnls))
    assert result["allowed"] is False
    assert "inconsistent_ledger_replay_evidence" in result["blocked_reasons"]
    assert result["evidence_quality_passed"] is False


def test_malformed_trade_numbers_block_instead_of_zero_coercion():
    bad_ledger = {
        "events": [
            {
                "event_type": "paper_trade_closed",
                "payload": {"trade_id": "bad", "realized_pl": float("nan"), "risk_dollars": 100.0},
            }
        ]
    }
    bad_replay = {
        "starting_balance": 10000.0,
        "ending_balance": 10000.0,
        "closed_trades": [{"realized_pl": 100.0, "risk_dollars": float("inf")}],
    }
    result = evaluator.evaluate_paper_profitability(bad_ledger, bad_replay)
    assert result["allowed"] is False
    assert "invalid_ledger_evidence" in result["blocked_reasons"]
    assert "invalid_replay_evidence" in result["blocked_reasons"]
    assert "missing_ledger_evidence" in result["blocked_reasons"]
    assert "missing_replay_evidence" in result["blocked_reasons"]


def test_missing_or_zero_risk_blocks_r_adjusted_false_positive():
    pnls = [200.0, -50.0, 150.0, -50.0, 100.0]
    ledger = _ledger(pnls, risk=0.0)
    replay = {
        "starting_balance": 10000.0,
        "ending_balance": 10350.0,
        "closed_trades": [{"realized_pl": pnl} for pnl in pnls],
        "paper_only": True,
    }
    result = evaluator.evaluate_paper_profitability(ledger, replay)
    assert result["allowed"] is False
    assert "invalid_ledger_evidence" in result["blocked_reasons"]
    assert "invalid_replay_evidence" in result["blocked_reasons"]
    assert result["evidence_quality_passed"] is False


def test_replay_balance_mismatch_blocks_corrupted_replay():
    pnls = [200.0, -50.0, 150.0, -50.0, 100.0]
    replay = _replay(pnls)
    replay["ending_balance"] = 9999.0
    result = evaluator.evaluate_paper_profitability(_ledger(pnls), replay)
    assert result["allowed"] is False
    assert "inconsistent_replay_evidence" in result["blocked_reasons"]
    assert result["evidence_quality_passed"] is False


def test_invalid_balance_history_blocks_even_when_trade_metrics_pass():
    pnls = [200.0, -50.0, 150.0, -50.0, 100.0]
    result = evaluator.evaluate_paper_profitability(
        _ledger(pnls),
        _replay(pnls),
        balance_history=[10000.0, "not-a-number", 10350.0],
    )
    assert result["allowed"] is False
    assert "invalid_balance_history" in result["blocked_reasons"]
    assert result["risk_quality_passed"] is False


def test_outputs_are_deterministic_for_identical_inputs():
    pnls = [200.0, -50.0, 150.0, -50.0, 100.0]
    first = evaluator.evaluate_paper_profitability(_ledger(pnls), _replay(pnls))
    second = evaluator.evaluate_paper_profitability(_ledger(pnls), _replay(pnls))
    assert first == second


def test_safety_boundary_enforced():
    result = evaluator.evaluate_paper_profitability(_ledger([200.0, -50.0, 150.0, -50.0, 100.0]), _replay([200.0, -50.0, 150.0, -50.0, 100.0]))
    safety = result["safety"]
    assert safety["paper_only"] is True
    assert safety["live_trading_allowed"] is False
    assert safety["broker_execution_allowed"] is False
    assert safety["credentials_allowed"] is False
    assert safety["production_deployment_allowed"] is False
    assert safety["network_used"] is False
    assert safety["live_order_placed"] is False


def test_source_has_no_forbidden_runtime_apis():
    source = inspect.getsource(evaluator)
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
