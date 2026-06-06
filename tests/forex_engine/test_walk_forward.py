import importlib

import pytest

from automation.forex_engine.config import ForexEngineConfig
from automation.forex_engine.market_data import load_fixture_candles
from automation.forex_engine.models import WalkForwardStatus, WalkForwardWindowResult
from automation.forex_engine.walk_forward import WalkForwardEngine


def fixture_candles():
    return load_fixture_candles("EURUSD", "5m", ForexEngineConfig())


def window(net_pnl, candles=10, trades=5, win_rate=50.0):
    return WalkForwardWindowResult(
        mode="PAPER_ONLY",
        symbol="EURUSD",
        timeframe="5m",
        window_name="test",
        candles_processed=candles,
        trades=trades,
        net_pnl_usd=net_pnl,
        win_rate_pct=win_rate,
        profit_factor=1.2,
        max_drawdown_usd=0.0,
        max_drawdown_pct=0.0,
        status=WalkForwardStatus.PASSED,
        summary_note="test",
    )


def test_split_candles_chronological_order():
    train, test, _split = WalkForwardEngine(ForexEngineConfig()).split_candles(fixture_candles(), 0.6)
    assert train[-1].timestamp < test[0].timestamp


def test_split_rejects_empty_candles():
    with pytest.raises(ValueError, match="empty"):
        WalkForwardEngine(ForexEngineConfig()).split_candles([])


def test_split_rejects_invalid_train_ratio():
    with pytest.raises(ValueError, match="train_ratio"):
        WalkForwardEngine(ForexEngineConfig()).split_candles(fixture_candles(), 0)
    with pytest.raises(ValueError, match="train_ratio"):
        WalkForwardEngine(ForexEngineConfig()).split_candles(fixture_candles(), 1)


def test_split_has_no_overlap():
    train, test, _split = WalkForwardEngine(ForexEngineConfig()).split_candles(fixture_candles(), 0.6)
    assert not ({item.timestamp for item in train} & {item.timestamp for item in test})


def test_split_counts_sum_to_total():
    train, test, split = WalkForwardEngine(ForexEngineConfig()).split_candles(fixture_candles(), 0.6)
    assert split.train_count + split.test_count == len(fixture_candles())
    assert len(train) + len(test) == len(fixture_candles())


def test_walk_forward_marks_tiny_fixture_insufficient_data():
    result = WalkForwardEngine(ForexEngineConfig()).run_walk_forward(fixture_candles())
    assert result.status == WalkForwardStatus.INSUFFICIENT_DATA


def test_walk_forward_result_has_train_and_test_results():
    result = WalkForwardEngine(ForexEngineConfig()).run_walk_forward(fixture_candles())
    assert result.train_result
    assert result.test_result


def test_degradation_positive_train_calculates_pct():
    status, degradation = WalkForwardEngine(ForexEngineConfig()).compare_train_test(window(10), window(5))
    assert degradation == 50.0
    assert status == WalkForwardStatus.PASSED


def test_degradation_non_positive_train_is_handled_safely():
    status, degradation = WalkForwardEngine(ForexEngineConfig()).compare_train_test(window(0), window(-1))
    assert degradation is None
    assert status == WalkForwardStatus.FAILED


def test_recommendations_for_insufficient_data():
    result = WalkForwardEngine(ForexEngineConfig()).run_walk_forward(fixture_candles())
    assert "larger historical datasets" in result.recommendations[0]


def test_walk_forward_demo_imports_without_network():
    assert importlib.import_module("automation.forex_engine.run_walk_forward_demo").main


def test_all_fixture_symbols_walk_forward_runs():
    config = ForexEngineConfig()
    engine = WalkForwardEngine(config)
    for symbol in config.symbols:
        result = engine.run_walk_forward(load_fixture_candles(symbol, "5m", config))
        assert result.mode == "PAPER_ONLY"


def test_existing_strategy_comparison_demo_imports():
    assert importlib.import_module("automation.forex_engine.run_strategy_comparison_demo").main


def test_no_live_execution_fields_required():
    result = WalkForwardEngine(ForexEngineConfig()).run_walk_forward(fixture_candles())
    assert "broker" not in result.metadata
