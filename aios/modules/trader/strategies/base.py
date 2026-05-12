"""Strategy contract for paper-only signal generation."""

from __future__ import annotations

from typing import Protocol

from aios.modules.trader.events import MarketBar, SignalEvent


class StrategyBase(Protocol):
    def generate_signal(self, bar: MarketBar) -> SignalEvent:
        """Return a review signal only; strategies do not submit orders."""
