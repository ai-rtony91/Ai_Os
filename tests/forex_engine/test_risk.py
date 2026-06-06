import pytest

from automation.forex_engine.config import ForexEngineConfig
from automation.forex_engine.models import PaperTrade, TradeOutcome
from automation.forex_engine.risk import RiskEngine
from automation.forex_engine.signals import create_demo_signals


def test_risk_amount_on_500_at_half_percent_is_250():
    assert RiskEngine(ForexEngineConfig()).calculate_risk_amount(500.0) == 2.50


def test_daily_drawdown_limit_on_500_at_two_percent_is_1000():
    assert RiskEngine(ForexEngineConfig()).calculate_daily_drawdown_limit(500.0) == 10.00


def test_new_trade_allowed_when_no_blockers_exist():
    decision = RiskEngine(ForexEngineConfig()).can_open_new_trade([], [], 500.0, 0.0)
    assert decision.allowed
    assert decision.blocked_reason is None


def test_new_trade_blocked_when_max_open_trades_reached():
    config = ForexEngineConfig()
    open_trades = [object(), object()]
    decision = RiskEngine(config).can_open_new_trade(open_trades, [], 500.0, 0.0)
    assert not decision.allowed
    assert "Max open" in decision.blocked_reason


def test_new_trade_blocked_after_three_consecutive_losses():
    closed = [
        PaperTrade("1", "PAPER_ONLY", "EURUSD", "5m", "BUY", 1, 0.9, 1.2, 1, 1, 80, outcome=TradeOutcome.LOSS),
        PaperTrade("2", "PAPER_ONLY", "EURUSD", "5m", "BUY", 1, 0.9, 1.2, 1, 1, 80, outcome=TradeOutcome.LOSS),
        PaperTrade("3", "PAPER_ONLY", "EURUSD", "5m", "BUY", 1, 0.9, 1.2, 1, 1, 80, outcome=TradeOutcome.LOSS),
    ]
    decision = RiskEngine(ForexEngineConfig()).can_open_new_trade([], closed, 500.0, 0.0)
    assert not decision.allowed
    assert "loss" in decision.blocked_reason.lower()


def test_new_trade_blocked_when_daily_drawdown_limit_reached():
    decision = RiskEngine(ForexEngineConfig()).can_open_new_trade([], [], 500.0, -10.0)
    assert not decision.allowed
    assert "drawdown" in decision.blocked_reason.lower()


def test_position_size_rejects_zero_stop_distance():
    signal = create_demo_signals()[0]
    signal.stop_loss = signal.entry_price
    with pytest.raises(ValueError, match="Stop distance"):
        RiskEngine(ForexEngineConfig()).calculate_position_size_units(signal, 2.50)
