"""Local in-memory paper broker."""

from __future__ import annotations

from aios.modules.trader.config import TraderConfig
from aios.modules.trader.events import PaperFillEvent, PaperOrderIntent


class PaperBroker:
    def __init__(self, config: TraderConfig) -> None:
        config.validate_safety()
        self.config = config
        self.cash = config.starting_cash
        self.positions: dict[str, int] = {}
        self.fills: list[PaperFillEvent] = []
        self.rejected_order_count = 0
        self._paper_fill_sequence = 0

    def submit(self, order: PaperOrderIntent) -> PaperFillEvent:
        try:
            self.config.validate_safety()
            if order.live_execution_status != "BLOCKED":
                raise ValueError("PaperBroker rejects non-blocked live execution status.")
            if order.external_routing_enabled:
                raise ValueError("PaperBroker rejects external routing.")
            if not order.paper_only:
                raise ValueError("PaperBroker accepts paper-only intents only.")
            if order.direction not in {"BUY_REVIEW", "SELL_REVIEW"}:
                raise ValueError("PaperBroker only fills review buy/sell paper intents.")

            signed_quantity = order.quantity if order.direction == "BUY_REVIEW" else -order.quantity
            notional = order.limit_price * order.quantity
            if order.direction == "BUY_REVIEW":
                if self.cash < notional:
                    raise ValueError("PaperBroker rejects buy with insufficient paper cash.")
                self.cash -= notional
            else:
                if self.positions.get(order.symbol, 0) < order.quantity:
                    raise ValueError("PaperBroker rejects sell without enough paper position.")
                self.cash += notional
        except ValueError:
            self.rejected_order_count += 1
            raise
        self.positions[order.symbol] = self.positions.get(order.symbol, 0) + signed_quantity

        self._paper_fill_sequence += 1
        expected_fill_price = (
            order.expected_fill_price
            if order.expected_fill_price is not None
            else order.limit_price
        )
        actual_paper_fill_price = order.limit_price
        fill = PaperFillEvent(
            symbol=order.symbol,
            timeframe=order.timeframe,
            timestamp=order.timestamp,
            direction=order.direction,
            quantity=order.quantity,
            fill_price=actual_paper_fill_price,
            paper_order_id=order.paper_order_id,
            paper_fill_id=f"PAPER-FILL-{self._paper_fill_sequence:06d}",
            expected_fill_price=expected_fill_price,
            actual_paper_fill_price=actual_paper_fill_price,
            paper_slippage=actual_paper_fill_price - expected_fill_price,
            spread_estimate=order.spread_estimate,
            fill_latency_ms=0,
        )
        self.fills.append(fill)
        return fill
