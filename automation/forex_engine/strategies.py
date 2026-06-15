"""PAPER_ONLY Supertrend strategy candidates for local edge research."""

from dataclasses import dataclass

from automation.forex_engine.indicators import DOWN, UP, atr, supertrend
from automation.forex_engine.market_data import validate_candle_sequence
from automation.forex_engine.models import Direction, ForexSignal, SignalCandidate


SUPERTREND_PULLBACK_V1 = "supertrend_pullback_v1"


@dataclass(frozen=True)
class SupertrendPullbackConfig:
    atr_period: int = 3
    supertrend_multiplier: float = 2.0
    min_body_to_range: float = 0.45
    min_atr: float = 0.0004
    max_band_extension_atr: float = 2.5
    min_reward_risk: float = 1.5
    target_reward_risk: float = 2.0
    chop_lookback: int = 4


def evaluate_supertrend_pullback(candles, strategy_config=SupertrendPullbackConfig()):
    validate_candle_sequence(candles)
    last = candles[-1]
    no_trade_reasons = []
    if len(candles) < strategy_config.atr_period + 2:
        no_trade_reasons.append("NO_TRADE: insufficient_data")
        return _blocked_candidate(candles, no_trade_reasons, strategy_config)

    trend = supertrend(candles, strategy_config.atr_period, strategy_config.supertrend_multiplier)
    atr_values = atr(candles, strategy_config.atr_period)
    last_trend = trend[-1]
    last_atr = atr_values[-1]

    if last_trend["direction"] not in (UP, DOWN):
        no_trade_reasons.append("NO_TRADE: no_supertrend_direction")
    if last_atr is None or last_atr < strategy_config.min_atr:
        no_trade_reasons.append("NO_TRADE: volatility_below_atr_threshold")
    if _recent_flip_count(trend, strategy_config.chop_lookback) >= 2 or _recent_close_flip_count(candles, strategy_config.chop_lookback) >= 3:
        no_trade_reasons.append("NO_TRADE: chop_zone_repeated_flips")
    if _body_to_range(last) < strategy_config.min_body_to_range:
        no_trade_reasons.append("NO_TRADE: weak_candle_body")

    direction = Direction.BUY if last_trend["direction"] == UP else Direction.SELL
    band = last_trend["lower_band"] if direction == Direction.BUY else last_trend["upper_band"]
    if band is None:
        no_trade_reasons.append("NO_TRADE: missing_supertrend_band")
        return _blocked_candidate(candles, no_trade_reasons, strategy_config)

    if direction == Direction.BUY and last.close <= last.open:
        no_trade_reasons.append("NO_TRADE: close_confirmation_missing")
    if direction == Direction.SELL and last.close >= last.open:
        no_trade_reasons.append("NO_TRADE: close_confirmation_missing")

    extension = abs(last.close - band)
    if last_atr and extension > strategy_config.max_band_extension_atr * last_atr:
        no_trade_reasons.append("NO_TRADE: entry_extended_from_band")

    stop_buffer = max(last_atr or 0.0, abs(last.close - band) * 0.5)
    if direction == Direction.BUY:
        stop_loss = min(band, last.low) - stop_buffer * 0.25
        risk = last.close - stop_loss
        take_profit = last.close + (risk * strategy_config.target_reward_risk)
    else:
        stop_loss = max(band, last.high) + stop_buffer * 0.25
        risk = stop_loss - last.close
        take_profit = last.close - (risk * strategy_config.target_reward_risk)

    reward = abs(take_profit - last.close)
    reward_risk = reward / risk if risk > 0 else 0.0
    if risk <= 0 or reward_risk < strategy_config.min_reward_risk:
        no_trade_reasons.append("NO_TRADE: reward_risk_below_minimum")

    if no_trade_reasons:
        return _blocked_candidate(candles, no_trade_reasons, strategy_config, direction, stop_loss, take_profit)

    candidate = SignalCandidate(
        symbol=last.symbol,
        timeframe=last.timeframe,
        direction=direction,
        entry_price=round(last.close, 5),
        stop_loss=round(stop_loss, 5),
        take_profit=round(take_profit, 5),
        strategy_name=SUPERTREND_PULLBACK_V1,
        regime_trend="SUPERTREND_UP" if direction == Direction.BUY else "SUPERTREND_DOWN",
        regime_volatility="ATR_OK",
        confidence_hint=78,
        reasons=[
            "supertrend_direction",
            "close_confirmation",
            "body_strength_filter",
            "atr_volatility_filter",
            "reward_risk_filter",
        ],
        metadata={
            "mode": "PAPER_ONLY",
            "atr": round(last_atr, 10),
            "band": round(band, 10),
            "reward_risk": round(reward_risk, 4),
            "warning": "edge candidate only; no live approval",
        },
    )
    return {
        "strategy_name": SUPERTREND_PULLBACK_V1,
        "accepted": True,
        "candidate": candidate,
        "signal": candidate_to_signal(candidate, last.timestamp),
        "no_trade_reasons": [],
    }


def generate_supertrend_signals_from_candles(candles, _config=None):
    result = evaluate_supertrend_pullback(candles)
    signal = result.get("signal")
    return ([signal] if signal else []), result


def candidate_to_signal(candidate, timestamp):
    if candidate.blocked_reason:
        raise ValueError(candidate.blocked_reason)
    return ForexSignal(
        symbol=candidate.symbol,
        timeframe=candidate.timeframe,
        direction=candidate.direction,
        entry_price=candidate.entry_price,
        stop_loss=candidate.stop_loss,
        take_profit=candidate.take_profit,
        timestamp=timestamp,
        strategy_name=candidate.strategy_name,
        metadata=dict(candidate.metadata),
    )


def _blocked_candidate(candles, reasons, strategy_config, direction=None, stop_loss=None, take_profit=None):
    last = candles[-1]
    candidate = SignalCandidate(
        symbol=last.symbol,
        timeframe=last.timeframe,
        direction=direction,
        entry_price=round(last.close, 5),
        stop_loss=round(stop_loss if stop_loss is not None else last.close, 5),
        take_profit=round(take_profit if take_profit is not None else last.close, 5),
        strategy_name=SUPERTREND_PULLBACK_V1,
        regime_trend="BLOCKED",
        regime_volatility="BLOCKED",
        confidence_hint=0,
        reasons=list(reasons),
        blocked_reason="; ".join(reasons),
        metadata={
            "mode": "PAPER_ONLY",
            "min_reward_risk": strategy_config.min_reward_risk,
            "warning": "NO_TRADE research result only",
        },
    )
    return {
        "strategy_name": SUPERTREND_PULLBACK_V1,
        "accepted": False,
        "candidate": candidate,
        "signal": None,
        "no_trade_reasons": list(reasons),
    }


def _body_to_range(candle):
    candle_range = candle.high - candle.low
    if candle_range <= 0:
        return 0.0
    return abs(candle.close - candle.open) / candle_range


def _recent_flip_count(trend, lookback):
    directions = [item["direction"] for item in trend if item["direction"] in (UP, DOWN)]
    recent = directions[-lookback:]
    if len(recent) < 2:
        return 0
    return sum(1 for previous, current in zip(recent, recent[1:]) if previous != current)


def _recent_close_flip_count(candles, lookback):
    recent = candles[-lookback:]
    directions = []
    for candle in recent:
        if candle.close > candle.open:
            directions.append(UP)
        elif candle.close < candle.open:
            directions.append(DOWN)
        else:
            directions.append(0)
    return sum(1 for previous, current in zip(directions, directions[1:]) if previous and current and previous != current)
