import importlib

from automation.forex_engine.backtest import run_backtest
from automation.forex_engine.config import ForexEngineConfig
from automation.forex_engine.market_data import load_fixture_candles
from automation.forex_engine.models import (
    BacktestResult,
    BacktestTradeResult,
    EngineMode,
    StrategyScorecard,
    StrategyStatus,
)
from automation.forex_engine.strategy_comparison import StrategyComparisonEngine


def trade(trade_id, outcome="WIN", pnl=1.0):
    return BacktestTradeResult(
        trade_id=trade_id,
        symbol="EURUSD",
        timeframe="5m",
        direction="BUY",
        entry_price=1.0,
        stop_loss=0.99,
        take_profit=1.02,
        exit_price=1.02 if pnl >= 0 else 0.99,
        opened_at="2026-06-06T09:00:00Z",
        closed_at="2026-06-06T09:05:00Z",
        outcome=outcome,
        pnl_usd=pnl,
        confidence_score=80,
        close_reason="TAKE_PROFIT" if pnl >= 0 else "STOP_LOSS",
    )


def result(
    strategy_name="test_strategy",
    trades=6,
    wins=4,
    losses=2,
    net_pnl=5.0,
    win_rate=66.67,
    profit_factor=1.8,
    drawdown_pct=0.5,
):
    trade_results = [trade(str(i), "WIN", 2.0) for i in range(wins)]
    trade_results.extend(trade(f"l{i}", "LOSS", -1.0) for i in range(losses))
    return BacktestResult(
        mode=EngineMode.PAPER_ONLY,
        symbol="EURUSD",
        timeframe="5m",
        strategy_name=strategy_name,
        candles_processed=50,
        signals_generated=trades,
        signals_accepted=trades,
        signals_blocked=0,
        trades_opened=trades,
        trades_closed=trades,
        starting_balance_usd=500.0,
        ending_balance_usd=500.0 + net_pnl,
        net_pnl_usd=net_pnl,
        win_rate_pct=win_rate,
        profit_factor=profit_factor,
        max_drawdown_usd=500.0 * (drawdown_pct / 100),
        max_drawdown_pct=drawdown_pct,
        results=trade_results,
        summary_note="test",
    )


def test_scorecard_from_positive_backtest_result():
    scorecard = StrategyComparisonEngine(ForexEngineConfig()).score_backtest_result(result())
    assert scorecard.mode == EngineMode.PAPER_ONLY
    assert scorecard.score > 50
    assert scorecard.components


def test_scorecard_marks_tiny_sample_insufficient_data():
    scorecard = StrategyComparisonEngine(ForexEngineConfig()).score_backtest_result(result(trades=2, wins=1, losses=1))
    assert scorecard.status == StrategyStatus.INSUFFICIENT_DATA


def test_scorecard_negative_pnl_penalty():
    scorecard = StrategyComparisonEngine(ForexEngineConfig()).score_backtest_result(
        result(net_pnl=-10, win_rate=30, profit_factor=0.5, losses=5, wins=1)
    )
    assert scorecard.score < 50 or scorecard.status in (StrategyStatus.REJECTED, StrategyStatus.WATCHLIST)


def test_profit_factor_none_adds_caution_candidate():
    scorecard = StrategyComparisonEngine(ForexEngineConfig()).score_backtest_result(result(profit_factor=None))
    assert any(candidate.name == "loss_sample" for candidate in scorecard.optimization_candidates)


def test_win_rate_below_50_adds_entry_filter_candidate():
    scorecard = StrategyComparisonEngine(ForexEngineConfig()).score_backtest_result(result(win_rate=40, losses=4, wins=2))
    assert any(candidate.name == "entry_filter" for candidate in scorecard.optimization_candidates)


def test_drawdown_penalty():
    scorecard = StrategyComparisonEngine(ForexEngineConfig()).score_backtest_result(result(drawdown_pct=3.0))
    assert any(candidate.name == "drawdown_control" for candidate in scorecard.optimization_candidates)


def test_rank_scorecards_orders_by_status_and_score():
    engine = StrategyComparisonEngine(ForexEngineConfig())
    weak = engine.score_backtest_result(result("weak", trades=2, wins=1, losses=1))
    strong = engine.score_backtest_result(result("strong", trades=8, wins=6, losses=2))
    ranked = engine.rank_scorecards([weak, strong])
    assert ranked[0].strategy_name == "strong"
    assert ranked[0].rank == 1


def test_compare_results_returns_top_strategy():
    comparison = StrategyComparisonEngine(ForexEngineConfig()).compare_results([result("a"), result("b", net_pnl=1)])
    assert comparison.top_strategy


def test_compare_results_counts_statuses():
    comparison = StrategyComparisonEngine(ForexEngineConfig()).compare_results(
        [result("tiny", trades=2, wins=1, losses=1), result("watch", net_pnl=0, win_rate=50)]
    )
    assert comparison.strategy_count == 2
    assert comparison.insufficient_data_count >= 1


def test_optimization_candidates_include_sample_size_for_tiny_sample():
    scorecard = StrategyComparisonEngine(ForexEngineConfig()).score_backtest_result(result(trades=2, wins=1, losses=1))
    assert any(candidate.name == "sample_size" for candidate in scorecard.optimization_candidates)


def test_strategy_comparison_demo_imports_without_network():
    assert importlib.import_module("automation.forex_engine.run_strategy_comparison_demo").main


def test_strategy_comparison_demo_runs_fixture_results():
    config = ForexEngineConfig()
    backtest_result = run_backtest(load_fixture_candles("EURUSD", "5m", config))
    comparison = StrategyComparisonEngine(config).compare_results([backtest_result])
    assert comparison.mode == EngineMode.PAPER_ONLY
    assert comparison.scorecards


def test_existing_demos_still_import():
    assert importlib.import_module("automation.forex_engine.run_confidence_demo").main
    assert importlib.import_module("automation.forex_engine.run_signal_rules_demo").main
    assert importlib.import_module("automation.forex_engine.run_backtest_demo").main
    assert importlib.import_module("automation.forex_engine.run_market_data_demo").main
    assert importlib.import_module("automation.forex_engine.run_paper_demo").main


def test_no_live_execution_fields_required():
    scorecard = StrategyComparisonEngine(ForexEngineConfig()).score_backtest_result(result())
    assert isinstance(scorecard, StrategyScorecard)
    assert "broker" not in scorecard.metadata
