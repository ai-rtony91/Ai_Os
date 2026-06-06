"""Market regime scaffold for Sprint 1."""

UNKNOWN = "UNKNOWN"
TRENDING = "TRENDING"
RANGING = "RANGING"
HIGH_VOLATILITY = "HIGH_VOLATILITY"
LOW_VOLATILITY = "LOW_VOLATILITY"


def assess_regime(candles=None):
    return {
        "regime": UNKNOWN,
        "reason": "Regime engine scaffold. Historical candle analysis begins in a later sprint.",
    }
