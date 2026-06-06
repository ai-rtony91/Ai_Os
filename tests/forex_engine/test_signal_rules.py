import importlib

import pytest

from automation.forex_engine.backtest import run_backtest
from automation.forex_engine.config import ForexEngineConfig
from automation.forex_engine.market_data import load_fixture_candles
from automation.forex_engine.models import BacktestConfig, Candle, Direction, EngineMode, SignalCandidate
from automation.forex_engine.regime import (
    RANGING,
    TRENDING_DOWN,
    TRENDING_UP,
    assess_regime,
)
from automation.forex_engine.signal_rules import (
    SPRINT_4_STRATEGY_NAME,
    IntradaySignalRules,
    candidate_to_forex_signal,
    generate_signals_from_candles,
)


def candle(close, timestamp, high=None, low=None, symbol="EURUSD"):
    high = high if high is not None else close + 0.0010
    low = low if low is not None else close - 0.0010
    return Candle(
        symbol=symbol,
        timeframe="5m",
        timestamp=timestamp,
        open=close,
        high=high,
        low=low,
        close=close,
        volume=1000,
        source="local_test_fixture",
    )


def rising_candles():
    return [
        candle(1.0800, "2026-06-06T09:00:00Z"),
        candle(1.0810, "2026-06-06T09:05:00Z"),
        candle(1.0820, "2026-06-06T09:10:00Z"),
    ]


def falling_candles():
    return [
        candle(1.0820, "2026-06-06T09:00:00Z"),
        candle(1.0810, "2026-06-06T09:05:00Z"),
        candle(1.0800, "2026-06-06T09:10:00Z"),
    ]


def ranging_candles():
    return [
        candle(1.0800, "2026-06-06T09:00:00Z", high=1.0815, low=1.0785),
        candle(1.0801, "2026-06-06T09:05:00Z", high=1.0814, low=1.0787),
        candle(1.0800, "2026-06-06T09:10:00Z", high=1.0813, low=1.0786),
    ]


def test_regime_detects_trending_up():
    assert assess_regime(rising_candles()).trend_state == TRENDING_UP


def test_regime_detects_trending_down():
    assert assess_regime(falling_candles()).trend_state == TRENDING_DOWN


def test_regime_detects_ranging():
    assert assess_regime(ranging_candles()).trend_state == RANGING


def test_regime_rejects_empty_candles():
    with pytest.raises(ValueError, match="requires"):
        assess_regime([])


def test_signal_rules_generate_buy_for_trending_up():
    result = IntradaySignalRules(ForexEngineConfig()).evaluate(rising_candles())
    assert result.accepted_count == 1
    assert result.candidates[0].direction == Direction.BUY


def test_signal_rules_generate_sell_for_trending_down():
    result = IntradaySignalRules(ForexEngineConfig()).evaluate(falling_candles())
    assert result.accepted_count == 1
    assert result.candidates[0].direction == Direction.SELL


def test_signal_rules_blocks_ranging_market():
    result = IntradaySignalRules(ForexEngineConfig()).evaluate(ranging_candles())
    assert result.accepted_count == 0
    assert result.blocked_count == 1
    assert "Ranging" in result.candidates[0].blocked_reason


def test_signal_rules_blocks_invalid_stop_distance():
    candidate = SignalCandidate(
        symbol="EURUSD",
        timeframe="5m",
        direction=Direction.BUY,
        entry_price=1.0800,
        stop_loss=1.0800,
        take_profit=1.0820,
        strategy_name=SPRINT_4_STRATEGY_NAME,
        regime_trend=TRENDING_UP,
        regime_volatility="NORMAL_VOLATILITY",
        confidence_hint=75,
    )
    blocked = IntradaySignalRules(ForexEngineConfig()).apply_quality_filter(candidate)
    assert "Invalid stop distance" in blocked.blocked_reason


def test_candidate_to_forex_signal_preserves_metadata():
    candidate = IntradaySignalRules(ForexEngineConfig()).evaluate(rising_candles()).candidates[0]
    signal = candidate_to_forex_signal(candidate, "2026-06-06T09:10:00Z")
    assert signal.metadata["source"] == "sprint_4_signal_rules"
    assert signal.metadata["regime_trend"] == TRENDING_UP
    assert signal.metadata["warning"] == "research signal only"


def test_generate_signals_from_fixture():
    signals, result = generate_signals_from_candles(
        load_fixture_candles("EURUSD", "5m", ForexEngineConfig()),
        ForexEngineConfig(),
    )
    assert result.mode == EngineMode.PAPER_ONLY
    assert result.symbol == "EURUSD"
    assert len(signals) <= len(result.candidates)


def test_all_fixture_symbols_can_be_evaluated():
    config = ForexEngineConfig()
    for symbol in config.symbols:
        result = IntradaySignalRules(config).evaluate(load_fixture_candles(symbol, "5m", config))
        assert result.symbol == symbol


def test_signal_rules_demo_imports_without_network():
    module = importlib.import_module("automation.forex_engine.run_signal_rules_demo")
    assert module.main


def test_backtest_can_still_use_sprint_3_demo_strategy():
    result = run_backtest(load_fixture_candles("EURUSD", "5m", ForexEngineConfig()))
    assert result.strategy_name == "sprint_3_demo_strategy"
    assert result.mode == EngineMode.PAPER_ONLY


def test_backtest_can_use_sprint_4_signal_provider_if_implemented():
    config = ForexEngineConfig()
    backtest_config = BacktestConfig(
        symbol="EURUSD",
        timeframe="5m",
        starting_balance_usd=config.starting_balance_usd,
        strategy_name="sprint_4_intraday_rules_v1",
    )
    result = run_backtest(load_fixture_candles("EURUSD", "5m", config), backtest_config)
    assert result.strategy_name == "sprint_4_intraday_rules_v1"
    assert result.mode == EngineMode.PAPER_ONLY
