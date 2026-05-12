from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


def build_tradingview_alert_payload(
    *,
    symbol: str = "EURUSD",
    pair: str = "EUR_USD",
    timeframe: str = "M15",
    signal_type: str = "EMA_VWAP_PULLBACK",
    direction: str = "BUY",
    price: float = 1.085,
    strategy_name: str = "AI_OS Paper EMA VWAP Pullback",
    alert_time: str | None = None,
    notes: str = "Paper-only template alert. No external connection is active.",
) -> dict[str, Any]:
    """Return a TradingView-style alert payload for local paper bridge tests."""
    return {
        "source": "TradingView",
        "symbol": symbol,
        "pair": pair,
        "timeframe": timeframe,
        "signal_type": signal_type,
        "direction": direction,
        "price": price,
        "strategy_name": strategy_name,
        "alert_time": alert_time or datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "risk_mode": "paper_only",
        "notes": notes,
    }
