"""Deterministic regime classification for PAPER_ONLY Sprint 4 research."""

UNKNOWN = "UNKNOWN"
TRENDING = "TRENDING"
TRENDING_UP = "TRENDING_UP"
TRENDING_DOWN = "TRENDING_DOWN"
RANGING = "RANGING"
NORMAL_VOLATILITY = "NORMAL_VOLATILITY"
HIGH_VOLATILITY = "HIGH_VOLATILITY"
LOW_VOLATILITY = "LOW_VOLATILITY"

from automation.forex_engine.models import RegimeAssessment


DEFAULT_LOOKBACK = 3
LOW_VOLATILITY_RANGE_PCT = 0.0003
HIGH_VOLATILITY_RANGE_PCT = 0.0020


def assess_regime(candles=None, lookback=DEFAULT_LOOKBACK):
    if not candles:
        raise ValueError("Regime assessment requires at least one candle.")

    selected = list(candles)[-lookback:]
    first = selected[0]
    candle_count = len(candles)
    if len(selected) < 3:
        return RegimeAssessment(
            symbol=first.symbol,
            timeframe=first.timeframe,
            trend_state=UNKNOWN,
            volatility_state=UNKNOWN,
            candle_count=candle_count,
            lookback=len(selected),
            reason="Insufficient candles for Sprint 4 regime classification.",
            metadata={"paper_only": True},
        )

    ranges = [candle.high - candle.low for candle in selected]
    closes = [candle.close for candle in selected]
    average_range = sum(ranges) / len(ranges)
    average_close = sum(closes) / len(closes)
    close_change = closes[-1] - closes[0]
    threshold = average_range * 0.5
    range_pct = average_range / average_close if average_close > 0 else 0.0

    if close_change >= threshold:
        trend_state = TRENDING_UP
        trend_reason = "Last close is meaningfully above first close."
    elif close_change <= -threshold:
        trend_state = TRENDING_DOWN
        trend_reason = "Last close is meaningfully below first close."
    else:
        trend_state = RANGING
        trend_reason = "Close change is small relative to average candle range."

    if range_pct < LOW_VOLATILITY_RANGE_PCT:
        volatility_state = LOW_VOLATILITY
        volatility_reason = "Average range percent is below Sprint 4 low-volatility threshold."
    elif range_pct > HIGH_VOLATILITY_RANGE_PCT:
        volatility_state = HIGH_VOLATILITY
        volatility_reason = "Average range percent is above Sprint 4 high-volatility threshold."
    else:
        volatility_state = NORMAL_VOLATILITY
        volatility_reason = "Average range percent is within Sprint 4 normal-volatility band."

    return RegimeAssessment(
        symbol=first.symbol,
        timeframe=first.timeframe,
        trend_state=trend_state,
        volatility_state=volatility_state,
        candle_count=candle_count,
        lookback=len(selected),
        reason=f"{trend_reason} {volatility_reason}",
        metadata={
            "average_range": average_range,
            "average_close": average_close,
            "close_change": close_change,
            "range_pct": range_pct,
            "threshold": threshold,
            "paper_only": True,
        },
    )
