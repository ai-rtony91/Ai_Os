from automation.forex_engine.edge_gate_policy import FAIL, PAPER_FORWARD_READY, WATCHLIST, classify_edge_gate


def metrics(**overrides):
    data = {
        "total_trades": 30,
        "expectancy_r": 0.2,
        "profit_factor": 1.5,
        "max_drawdown_pct": 4.0,
        "longest_losing_streak": 3,
    }
    data.update(overrides)
    return data


def test_costless_only_winner_fails():
    result = classify_edge_gate(metrics(), cost_model_used=False)
    assert result["classification"] == FAIL
    assert "cost_model_required" in result["blockers"]


def test_too_few_trades_fails():
    result = classify_edge_gate(metrics(total_trades=3))
    assert result["classification"] == FAIL
    assert "minimum_sample_size_not_met" in result["blockers"]


def test_high_drawdown_goes_to_watchlist_or_fail_boundary():
    result = classify_edge_gate(metrics(max_drawdown_pct=20.0))
    assert result["classification"] == WATCHLIST
    assert "max_drawdown_cap_exceeded" in result["blockers"]


def test_valid_candidate_can_reach_paper_forward_ready_only():
    result = classify_edge_gate(metrics(), {"consistent_windows_pct": 80.0})
    assert result["classification"] == PAPER_FORWARD_READY
    assert result["live_ready"] is False
