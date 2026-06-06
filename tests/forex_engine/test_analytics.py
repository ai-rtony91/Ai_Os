from automation.forex_engine.analytics import ForexAnalytics
from automation.forex_engine.models import PaperTrade, TradeOutcome


def make_closed_trade(trade_id, outcome, pnl):
    return PaperTrade(
        trade_id=trade_id,
        mode="PAPER_ONLY",
        symbol="EURUSD",
        timeframe="5m",
        direction="BUY",
        entry_price=1.0,
        stop_loss=0.9,
        take_profit=1.2,
        position_size_units=10,
        risk_amount_usd=2.50,
        confidence_score=80,
        outcome=outcome,
        pnl_usd=pnl,
    )


def test_no_trades_summary_does_not_crash():
    summary = ForexAnalytics().summarize(500.0, 500.0, [], [])
    assert summary.total_trades == 0
    assert summary.win_rate_pct == 0.0
    assert summary.current_balance_usd == 500.0


def test_closed_trade_metrics_are_calculated():
    closed = [
        make_closed_trade("1", TradeOutcome.WIN, 4.0),
        make_closed_trade("2", TradeOutcome.LOSS, -2.0),
    ]
    summary = ForexAnalytics().summarize(500.0, 502.0, [], closed)
    assert summary.wins == 1
    assert summary.losses == 1
    assert summary.win_rate_pct == 50.0
    assert summary.gross_profit_usd == 4.0
    assert summary.gross_loss_usd == 2.0
    assert summary.net_pnl_usd == 2.0
    assert summary.profit_factor == 2.0
    assert summary.current_balance_usd == 502.0


def test_profit_factor_is_safe_when_no_gross_loss():
    closed = [make_closed_trade("1", TradeOutcome.WIN, 4.0)]
    summary = ForexAnalytics().summarize(500.0, 504.0, [], closed)
    assert summary.profit_factor is None
    assert "undefined" in summary.consistency_note
