"""Conservative PAPER_ONLY trade cost model for edge research."""

from dataclasses import dataclass

from automation.forex_engine.models import Direction


@dataclass(frozen=True)
class TradeCostAssumptions:
    spread: float = 0.00010
    slippage: float = 0.00005
    commission_per_trade_usd: float = 0.0


def conservative_entry_price(direction, raw_price, assumptions=TradeCostAssumptions()):
    adjustment = assumptions.spread / 2 + assumptions.slippage
    if direction == Direction.BUY:
        return round(raw_price + adjustment, 10)
    if direction == Direction.SELL:
        return round(raw_price - adjustment, 10)
    raise ValueError("Direction must be BUY or SELL.")


def conservative_exit_price(direction, raw_price, assumptions=TradeCostAssumptions()):
    adjustment = assumptions.spread / 2 + assumptions.slippage
    if direction == Direction.BUY:
        return round(raw_price - adjustment, 10)
    if direction == Direction.SELL:
        return round(raw_price + adjustment, 10)
    raise ValueError("Direction must be BUY or SELL.")


def trade_cost_usd(position_size_units, assumptions=TradeCostAssumptions()):
    per_unit_cost = assumptions.spread + (2 * assumptions.slippage)
    return round(abs(position_size_units) * per_unit_cost + assumptions.commission_per_trade_usd, 2)


def apply_cost_to_pnl(raw_pnl_usd, position_size_units, assumptions=TradeCostAssumptions()):
    return round(raw_pnl_usd - trade_cost_usd(position_size_units, assumptions), 2)


def cost_assumption_summary(assumptions=TradeCostAssumptions()):
    return {
        "spread": assumptions.spread,
        "slippage": assumptions.slippage,
        "commission_per_trade_usd": assumptions.commission_per_trade_usd,
        "fill_policy": "conservative entry and exit adjustment",
        "mode": "PAPER_ONLY",
    }
