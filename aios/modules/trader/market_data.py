"""In-memory market data feed for local deterministic replay."""

from __future__ import annotations

from aios.modules.trader.events import MarketBar


class MarketDataFeed:
    def __init__(self) -> None:
        self._bars: dict[tuple[str, str], list[MarketBar]] = {}

    def add_bar(self, bar: MarketBar) -> None:
        key = (bar.symbol, bar.timeframe)
        self._bars.setdefault(key, []).append(bar)

    def latest_bar(self, symbol: str, timeframe: str) -> MarketBar | None:
        bars = self._bars.get((symbol, timeframe), [])
        if not bars:
            return None
        return bars[-1]

    def bars(self, symbol: str, timeframe: str) -> list[MarketBar]:
        return list(self._bars.get((symbol, timeframe), []))
