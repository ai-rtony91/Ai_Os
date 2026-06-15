from automation.forex_engine.metrics import calculate_edge_metrics


def test_metrics_are_correct_on_deterministic_trade_samples():
    metrics = calculate_edge_metrics(
        [
            {"pnl_usd": 10.0, "r_multiple": 2.0},
            {"pnl_usd": -5.0, "r_multiple": -1.0},
            {"pnl_usd": 5.0, "r_multiple": 1.0},
        ],
        no_trade_reasons=["NO_TRADE: weak", "NO_TRADE: weak", "NO_TRADE: chop"],
    )
    assert metrics["total_trades"] == 3
    assert metrics["wins"] == 2
    assert metrics["losses"] == 1
    assert metrics["win_rate"] == 66.67
    assert metrics["average_r"] == 0.6667
    assert metrics["expectancy_r"] == 0.6667
    assert metrics["profit_factor"] == 3.0
    assert metrics["longest_losing_streak"] == 1
    assert metrics["no_trade_reason_counts"]["NO_TRADE: weak"] == 2


def test_weak_sample_does_not_get_promoted_by_metrics():
    metrics = calculate_edge_metrics([{"pnl_usd": -5.0, "r_multiple": -1.0}])
    assert metrics["pass"] is False
    assert metrics["expectancy_r"] < 0
