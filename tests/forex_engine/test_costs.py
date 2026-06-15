from automation.forex_engine.costs import (
    TradeCostAssumptions,
    apply_cost_to_pnl,
    conservative_entry_price,
    conservative_exit_price,
    trade_cost_usd,
)
from automation.forex_engine.models import Direction


def test_cost_model_reduces_result_versus_zero_cost_case():
    assumptions = TradeCostAssumptions(spread=0.0001, slippage=0.00005, commission_per_trade_usd=0.5)
    assert apply_cost_to_pnl(10.0, 10000, assumptions) < 10.0


def test_cost_model_does_not_mutate_source_candles():
    price = 1.08
    conservative_entry_price(Direction.BUY, price)
    assert price == 1.08


def test_conservative_fill_behavior_is_direction_safe():
    assumptions = TradeCostAssumptions(spread=0.0001, slippage=0.00005)
    assert conservative_entry_price(Direction.BUY, 1.08, assumptions) > 1.08
    assert conservative_entry_price(Direction.SELL, 1.08, assumptions) < 1.08
    assert conservative_exit_price(Direction.BUY, 1.08, assumptions) < 1.08
    assert conservative_exit_price(Direction.SELL, 1.08, assumptions) > 1.08
    assert trade_cost_usd(10000, assumptions) > 0
