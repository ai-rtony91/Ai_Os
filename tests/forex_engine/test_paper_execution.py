import importlib.util

import pytest

from automation.forex_engine.confidence import ConfidenceEngine
from automation.forex_engine.config import ForexEngineConfig
from automation.forex_engine.models import Direction, EngineMode, ForexSignal, TradeOutcome, utc_now_iso
from automation.forex_engine.paper_execution import PaperExecutionEngine
from automation.forex_engine.risk import RiskEngine
from automation.forex_engine.signals import create_demo_signals


def make_engine():
    config = ForexEngineConfig()
    return PaperExecutionEngine(config, RiskEngine(config))


def submit_first_demo_trade(engine):
    signal = create_demo_signals()[0]
    confidence = ConfidenceEngine(engine.config).score_signal(signal)
    return engine.submit_signal(signal, confidence)


def test_valid_signal_with_passing_confidence_opens_paper_trade():
    engine = make_engine()
    trade = submit_first_demo_trade(engine)
    assert trade.mode == EngineMode.PAPER_ONLY
    assert len(engine.open_trades) == 1


def test_max_open_trades_rule_is_respected():
    engine = make_engine()
    confidence_engine = ConfidenceEngine(engine.config)
    for signal in create_demo_signals()[:2]:
        engine.submit_signal(signal, confidence_engine.score_signal(signal))
    with pytest.raises(ValueError, match="Max open"):
        engine.submit_signal(create_demo_signals()[2], confidence_engine.score_signal(create_demo_signals()[2]))


def test_closing_buy_trade_above_entry_creates_win():
    engine = make_engine()
    trade = submit_first_demo_trade(engine)
    closed = engine.close_trade(trade.trade_id, trade.take_profit)
    assert closed.outcome == TradeOutcome.WIN


def test_closing_buy_trade_below_entry_creates_loss():
    engine = make_engine()
    trade = submit_first_demo_trade(engine)
    closed = engine.close_trade(trade.trade_id, trade.stop_loss)
    assert closed.outcome == TradeOutcome.LOSS


def test_closing_sell_trade_below_entry_creates_win():
    engine = make_engine()
    signal = ForexSignal(
        symbol="GBPUSD",
        timeframe="5m",
        direction=Direction.SELL,
        entry_price=1.2700,
        stop_loss=1.2720,
        take_profit=1.2660,
        timestamp=utc_now_iso(),
        strategy_name="paper_sell_test",
        metadata={"setup_quality": "clean", "session": "new_york"},
    )
    confidence = ConfidenceEngine(engine.config).score_signal(signal)
    trade = engine.submit_signal(signal, confidence)
    closed = engine.close_trade(trade.trade_id, trade.take_profit)
    assert closed.outcome == TradeOutcome.WIN


def test_balance_updates_after_close():
    engine = make_engine()
    trade = submit_first_demo_trade(engine)
    closed = engine.close_trade(trade.trade_id, trade.take_profit)
    assert engine.current_balance_usd == round(engine.config.starting_balance_usd + closed.pnl_usd, 2)


def test_no_broker_module_is_required():
    assert importlib.util.find_spec("automation.forex_engine.paper_execution") is not None
