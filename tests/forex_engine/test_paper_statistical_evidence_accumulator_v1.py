from __future__ import annotations

import inspect

from automation.forex_engine import paper_statistical_evidence_accumulator_v1 as gate


def _period(period_id: str, **overrides):
    value = {
        "period_id": period_id,
        "closed_trades": 12,
        "net_pnl_after_costs": 120.0,
        "expectancy_r": 0.2,
        "profit_factor": 1.5,
        "max_drawdown_r": 2.0,
        "walk_forward_folds": 3,
        "out_of_sample_folds": 3,
        "paper_only": True,
        "sanitized": True,
    }
    value.update(overrides)
    return value


def test_accumulated_evidence_reaches_owner_review_only():
    result = gate.evaluate_paper_statistical_evidence(
        "candidate-a", [_period("p1"), _period("p2"), _period("p3")]
    )
    assert result["classification"] == gate.READY
    assert result["metrics"]["total_trades"] == 36
    assert result["metrics"]["consecutive_profitable_periods"] == 3
    assert result["safety"]["owner_review_required"] is True
    assert result["safety"]["demo_execution_allowed"] is False
    assert result["safety"]["live_execution_allowed"] is False


def test_losing_latest_period_resets_consecutive_count():
    periods = [_period("p1"), _period("p2"), _period("p3", net_pnl_after_costs=-5.0)]
    result = gate.evaluate_paper_statistical_evidence("candidate-a", periods)
    assert result["classification"] == gate.ACCUMULATING
    assert result["metrics"]["consecutive_profitable_periods"] == 0
    assert "insufficient_consecutive_profitable_periods" in result["blockers"]


def test_after_cost_sample_and_walk_forward_thresholds_fail_closed():
    periods = [
        _period("p1", closed_trades=2, walk_forward_folds=2),
        _period("p2", closed_trades=2),
        _period("p3", closed_trades=2),
    ]
    result = gate.evaluate_paper_statistical_evidence("candidate-a", periods)
    assert "insufficient_total_trades" in result["blockers"]
    assert "insufficient_walk_forward_folds" in result["blockers"]


def test_invalid_or_unsanitized_evidence_is_blocked():
    result = gate.evaluate_paper_statistical_evidence(
        "candidate-a", [_period("p1", sanitized=False), _period("p1")]
    )
    assert result["classification"] == gate.BLOCKED_INVALID
    assert "sanitized_not_confirmed:0" in result["blockers"]
    assert "duplicate_period_id:p1" in result["blockers"]


def test_selector_is_deterministic_and_never_executes():
    lower = gate.evaluate_paper_statistical_evidence(
        "candidate-b", [_period("b1"), _period("b2"), _period("b3")]
    )
    higher = gate.evaluate_paper_statistical_evidence(
        "candidate-a",
        [_period("a1", expectancy_r=0.3), _period("a2", expectancy_r=0.3), _period("a3", expectancy_r=0.3)],
    )
    selection = gate.select_next_candidate_for_owner_review([lower, higher])
    assert selection["selected_candidate_id"] == "candidate-a"
    assert selection["owner_review_ready"] is True
    assert selection["execution_allowed"] is False


def test_source_has_no_runtime_or_file_io():
    source = inspect.getsource(gate)
    for token in ("import requests", "import socket", "import subprocess", "open(", "os.environ", "getenv("):
        assert token not in source
