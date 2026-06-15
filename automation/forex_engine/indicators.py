"""PAPER_ONLY indicator calculations for local forex edge research."""

from automation.forex_engine.market_data import validate_candle_sequence


UP = 1
DOWN = -1
FLAT = 0


def true_range(candles):
    """Return deterministic true range values for a validated candle sequence."""
    validate_candle_sequence(candles)
    ranges = []
    previous_close = None
    for candle in candles:
        high_low = candle.high - candle.low
        if previous_close is None:
            ranges.append(round(high_low, 10))
        else:
            ranges.append(
                round(
                    max(
                        high_low,
                        abs(candle.high - previous_close),
                        abs(candle.low - previous_close),
                    ),
                    10,
                )
            )
        previous_close = candle.close
    return ranges


def atr(candles, period=14):
    """Return same-length ATR output. Values before enough data are None."""
    if period <= 0:
        raise ValueError("ATR period must be positive.")
    ranges = true_range(candles)
    values = []
    previous_atr = None
    for index, value in enumerate(ranges):
        if index + 1 < period:
            values.append(None)
            continue
        if index + 1 == period:
            previous_atr = sum(ranges[:period]) / period
        else:
            previous_atr = ((previous_atr * (period - 1)) + value) / period
        values.append(round(previous_atr, 10))
    return values


def supertrend(candles, period=10, multiplier=3.0):
    """Calculate Supertrend bands and direction using local candles only."""
    if multiplier <= 0:
        raise ValueError("Supertrend multiplier must be positive.")
    validate_candle_sequence(candles)
    atr_values = atr(candles, period)
    output = []
    final_upper = None
    final_lower = None
    previous_direction = FLAT

    for index, candle in enumerate(candles):
        atr_value = atr_values[index]
        if atr_value is None:
            output.append(
                {
                    "timestamp": candle.timestamp,
                    "atr": None,
                    "upper_band": None,
                    "lower_band": None,
                    "supertrend": None,
                    "direction": FLAT,
                }
            )
            continue

        hl2 = (candle.high + candle.low) / 2
        basic_upper = hl2 + multiplier * atr_value
        basic_lower = hl2 - multiplier * atr_value
        previous_close = candles[index - 1].close if index > 0 else candle.close

        if final_upper is None or basic_upper < final_upper or previous_close > final_upper:
            final_upper = basic_upper
        if final_lower is None or basic_lower > final_lower or previous_close < final_lower:
            final_lower = basic_lower

        if previous_direction == DOWN and candle.close > final_upper:
            direction = UP
        elif previous_direction in (UP, FLAT) and candle.close < final_lower:
            direction = DOWN
        elif previous_direction == FLAT:
            direction = UP if candle.close >= hl2 else DOWN
        else:
            direction = previous_direction

        trend_value = final_lower if direction == UP else final_upper
        output.append(
            {
                "timestamp": candle.timestamp,
                "atr": round(atr_value, 10),
                "upper_band": round(final_upper, 10),
                "lower_band": round(final_lower, 10),
                "supertrend": round(trend_value, 10),
                "direction": direction,
            }
        )
        previous_direction = direction
    return output
