"""Trader engine wiring for the AIOS paper-only module."""

from __future__ import annotations

from aios.modules.trader.brokers.paper_broker import PaperBroker
from aios.modules.trader.config import TraderConfig
from aios.modules.trader.events import (
    MarketBar,
    PaperOrderIntent,
    SignalEvent,
    TraderDecisionEvent,
)
from aios.modules.trader.market_data import MarketDataFeed
from aios.modules.trader.outcomes import PaperOutcomeTracker
from aios.modules.trader.risk import RiskManager
from aios.modules.trader.strategies.base import StrategyBase
from aios.modules.trader.strategies.supertrend_permission import SuperTrendPermissionFilter


class _DefaultReviewStrategy:
    def generate_signal(self, bar: MarketBar) -> SignalEvent:
        if bar.close > bar.open:
            direction = "BUY_REVIEW"
        elif bar.close < bar.open:
            direction = "SELL_REVIEW"
        else:
            direction = "HOLD"
        return SignalEvent(
            symbol=bar.symbol,
            timeframe=bar.timeframe,
            timestamp=bar.timestamp,
            direction=direction,
            quantity=1,
            reason="default_close_vs_open_review",
        )


class TraderEngine:
    def __init__(
        self,
        config: TraderConfig | None = None,
        market_data: MarketDataFeed | None = None,
        strategy: StrategyBase | None = None,
        permission_filter: SuperTrendPermissionFilter | None = None,
        risk_manager: RiskManager | None = None,
        paper_broker: PaperBroker | None = None,
    ) -> None:
        self.config = config or TraderConfig()
        self.market_data = market_data or MarketDataFeed()
        self.strategy = strategy or _DefaultReviewStrategy()
        self.permission_filter = permission_filter or SuperTrendPermissionFilter()
        self.risk_manager = risk_manager or RiskManager()
        self.paper_broker = paper_broker or PaperBroker(self.config)
        self.paper_outcomes = PaperOutcomeTracker()
        self._paper_order_sequence = 0

    def on_bar(self, bar: MarketBar) -> TraderDecisionEvent:
        self.market_data.add_bar(bar)
        return self.run_once(bar.symbol, bar.timeframe)

    def run_once(self, symbol: str, timeframe: str) -> TraderDecisionEvent:
        bar = self.market_data.latest_bar(symbol, timeframe)
        if bar is None:
            return TraderDecisionEvent(
                symbol=symbol,
                timeframe=timeframe,
                timestamp="UNKNOWN",
                decision="BLOCKED",
                reason="No market bar is available.",
            )

        try:
            self.config.validate_safety()
            signal = self.strategy.generate_signal(bar)
            permission = self.permission_filter.evaluate(bar)
            risk = self.risk_manager.evaluate(signal, permission, self.config)
            if not risk.approved:
                return TraderDecisionEvent(
                    symbol=symbol,
                    timeframe=timeframe,
                    timestamp=bar.timestamp,
                    decision="BLOCKED",
                    signal=signal.to_dict(),
                    permission=permission.to_dict(),
                    risk=risk.to_dict(),
                    reason=risk.reason,
                )

            order = self._create_paper_order(bar, risk.direction, risk.quantity)
            fill = self.paper_broker.submit(order)
            paper_outcome = self.paper_outcomes.record_fill(fill.to_dict())
            return TraderDecisionEvent(
                symbol=symbol,
                timeframe=timeframe,
                timestamp=bar.timestamp,
                decision=risk.direction,
                signal=signal.to_dict(),
                permission=permission.to_dict(),
                risk=risk.to_dict(),
                paper_order=order.to_dict(),
                paper_fill=fill.to_dict(),
                paper_outcome=paper_outcome.to_dict() if paper_outcome else None,
                reason="Paper order filled locally.",
            )
        except ValueError as exc:
            return TraderDecisionEvent(
                symbol=symbol,
                timeframe=timeframe,
                timestamp=bar.timestamp,
                decision="BLOCKED",
                reason=str(exc),
            )

    def _create_paper_order(self, bar: MarketBar, direction: str, quantity: int) -> PaperOrderIntent:
        self._paper_order_sequence += 1
        return PaperOrderIntent(
            symbol=bar.symbol,
            timeframe=bar.timeframe,
            timestamp=bar.timestamp,
            direction=direction,
            quantity=quantity,
            limit_price=bar.close,
            paper_order_id=f"PAPER-ORDER-{self._paper_order_sequence:06d}",
            live_execution_status=self.config.live_execution_status,
            external_routing_enabled=self.config.external_routing_enabled,
        )
