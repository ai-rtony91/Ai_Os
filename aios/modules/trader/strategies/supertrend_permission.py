"""Deterministic SuperTrend-style permission filter.

This is a permission layer only. It does not create orders and does not
override the risk manager.
"""

from __future__ import annotations

from aios.modules.trader.events import MarketBar, PermissionEvent


class SuperTrendPermissionFilter:
    def evaluate(self, bar: MarketBar) -> PermissionEvent:
        if bar.high < bar.low:
            permission = "blocked"
            reason = "Invalid bar range."
        elif bar.close > bar.open:
            permission = "bullish"
            reason = "Close is above open."
        elif bar.close < bar.open:
            permission = "bearish"
            reason = "Close is below open."
        else:
            permission = "neutral"
            reason = "Flat bar."

        return PermissionEvent(
            symbol=bar.symbol,
            timeframe=bar.timeframe,
            timestamp=bar.timestamp,
            permission=permission,
            reason=reason,
        )
