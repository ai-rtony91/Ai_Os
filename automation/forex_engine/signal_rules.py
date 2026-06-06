"""PAPER_ONLY regime and intraday signal rules for Sprint 4 research."""

from automation.forex_engine.market_data import validate_candle_sequence
from automation.forex_engine.models import (
    Direction,
    EngineMode,
    ForexSignal,
    SignalCandidate,
    SignalRuleResult,
)
from automation.forex_engine.regime import (
    HIGH_VOLATILITY,
    LOW_VOLATILITY,
    NORMAL_VOLATILITY,
    RANGING,
    TRENDING_DOWN,
    TRENDING_UP,
    UNKNOWN,
    assess_regime,
)


SPRINT_4_STRATEGY_NAME = "sprint_4_intraday_trend_follow_v1"


class IntradaySignalRules:
    def __init__(self, config):
        self.config = config

    def evaluate(self, candles) -> SignalRuleResult:
        validate_candle_sequence(candles)
        regime = assess_regime(candles)
        candidate = self.generate_candidate(candles, regime)
        candidates = [candidate] if candidate is not None else []
        accepted_count = sum(1 for item in candidates if item.blocked_reason is None)
        blocked_count = sum(1 for item in candidates if item.blocked_reason is not None)
        if not candidates:
            note = "No Sprint 4 signal candidate generated."
        elif accepted_count:
            note = "Sprint 4 PAPER_ONLY research candidate accepted."
        else:
            note = "Sprint 4 PAPER_ONLY research candidate blocked."
        return SignalRuleResult(
            symbol=candles[-1].symbol,
            timeframe=candles[-1].timeframe,
            mode=EngineMode.PAPER_ONLY,
            regime=regime,
            candidates=candidates,
            accepted_count=accepted_count,
            blocked_count=blocked_count,
            summary_note=note,
        )

    def generate_candidate(self, candles, regime_assessment):
        if len(candles) < 3 or regime_assessment.trend_state == UNKNOWN:
            return SignalCandidate(
                symbol=candles[-1].symbol,
                timeframe=candles[-1].timeframe,
                direction=None,
                entry_price=candles[-1].close,
                stop_loss=candles[-1].close,
                take_profit=candles[-1].close,
                strategy_name=SPRINT_4_STRATEGY_NAME,
                regime_trend=regime_assessment.trend_state,
                regime_volatility=regime_assessment.volatility_state,
                confidence_hint=0,
                reasons=["Insufficient candles or unknown regime."],
                blocked_reason="Unknown regime blocked for Sprint 4 trend-follow rule.",
                metadata={"source": "sprint_4_signal_rules"},
            )

        last = candles[-1]
        recent = candles[-3:]
        reasons = ["local fixture", "deterministic rule"]
        direction = None
        stop_loss = last.close
        take_profit = last.close

        if regime_assessment.trend_state == TRENDING_UP:
            direction = Direction.BUY
            stop_loss = min(candle.low for candle in recent)
            risk_distance = last.close - stop_loss
            take_profit = last.close + (2 * risk_distance)
            reasons.insert(0, "trend up")
        elif regime_assessment.trend_state == TRENDING_DOWN:
            direction = Direction.SELL
            stop_loss = max(candle.high for candle in recent)
            risk_distance = stop_loss - last.close
            take_profit = last.close - (2 * risk_distance)
            reasons.insert(0, "trend down")
        elif regime_assessment.trend_state == RANGING:
            return SignalCandidate(
                symbol=last.symbol,
                timeframe=last.timeframe,
                direction=None,
                entry_price=last.close,
                stop_loss=last.close,
                take_profit=last.close,
                strategy_name=SPRINT_4_STRATEGY_NAME,
                regime_trend=regime_assessment.trend_state,
                regime_volatility=regime_assessment.volatility_state,
                confidence_hint=0,
                reasons=["ranging regime", "local fixture", "deterministic rule"],
                blocked_reason="Ranging regime blocked for Sprint 4 trend-follow rule.",
                metadata={"source": "sprint_4_signal_rules"},
            )

        candidate = SignalCandidate(
            symbol=last.symbol,
            timeframe=last.timeframe,
            direction=direction,
            entry_price=last.close,
            stop_loss=round(stop_loss, 5),
            take_profit=round(take_profit, 5),
            strategy_name=SPRINT_4_STRATEGY_NAME,
            regime_trend=regime_assessment.trend_state,
            regime_volatility=regime_assessment.volatility_state,
            confidence_hint=75,
            reasons=reasons,
            metadata={"source": "sprint_4_signal_rules"},
        )
        return self.apply_quality_filter(candidate)

    def apply_quality_filter(self, candidate):
        if candidate.regime_volatility == LOW_VOLATILITY:
            candidate.blocked_reason = "Low volatility blocked for Sprint 4 trend-follow rule."
        elif candidate.regime_volatility == HIGH_VOLATILITY:
            candidate.blocked_reason = "High volatility blocked for Sprint 4 trend-follow rule."
        elif candidate.direction == Direction.BUY:
            if candidate.entry_price - candidate.stop_loss <= 0:
                candidate.blocked_reason = "Invalid stop distance for Sprint 4 BUY candidate."
            elif candidate.take_profit <= candidate.entry_price:
                candidate.blocked_reason = "Invalid take profit for Sprint 4 BUY candidate."
        elif candidate.direction == Direction.SELL:
            if candidate.stop_loss - candidate.entry_price <= 0:
                candidate.blocked_reason = "Invalid stop distance for Sprint 4 SELL candidate."
            elif candidate.take_profit >= candidate.entry_price:
                candidate.blocked_reason = "Invalid take profit for Sprint 4 SELL candidate."
        else:
            candidate.blocked_reason = candidate.blocked_reason or "Missing direction for Sprint 4 candidate."
        return candidate


def candidate_to_forex_signal(candidate, timestamp):
    if candidate.blocked_reason:
        raise ValueError(candidate.blocked_reason)
    if candidate.direction not in (Direction.BUY, Direction.SELL):
        raise ValueError("SignalCandidate direction must be BUY or SELL.")
    return ForexSignal(
        symbol=candidate.symbol,
        timeframe=candidate.timeframe,
        direction=candidate.direction,
        entry_price=candidate.entry_price,
        stop_loss=candidate.stop_loss,
        take_profit=candidate.take_profit,
        timestamp=timestamp,
        strategy_name=candidate.strategy_name,
        metadata={
            "source": "sprint_4_signal_rules",
            "setup_quality": "research",
            "session": "fixture",
            "regime_trend": candidate.regime_trend,
            "regime_volatility": candidate.regime_volatility,
            "confidence_hint": candidate.confidence_hint,
            "reasons": list(candidate.reasons),
            "warning": "research signal only",
        },
    )


def generate_signals_from_candles(candles, config):
    result = IntradaySignalRules(config).evaluate(candles)
    signals = [
        candidate_to_forex_signal(candidate, candles[-1].timestamp)
        for candidate in result.candidates
        if candidate.blocked_reason is None
    ]
    return signals, result
