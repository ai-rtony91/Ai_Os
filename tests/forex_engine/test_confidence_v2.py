import importlib

from automation.forex_engine.confidence import ConfidenceEngine
from automation.forex_engine.confidence_v2 import ConfidenceEngineV2, band_for_score, grade_for_score
from automation.forex_engine.config import ForexEngineConfig
from automation.forex_engine.market_data import load_fixture_candles
from automation.forex_engine.models import (
    ConfidenceBand,
    Direction,
    ForexSignal,
    RegimeAssessment,
    SetupGrade,
    SignalCandidate,
)
from automation.forex_engine.regime import HIGH_VOLATILITY, LOW_VOLATILITY, NORMAL_VOLATILITY, RANGING, TRENDING_DOWN, TRENDING_UP
from automation.forex_engine.signal_rules import IntradaySignalRules, candidate_to_forex_signal


def regime(trend=TRENDING_UP, volatility=NORMAL_VOLATILITY):
    return RegimeAssessment(
        symbol="EURUSD",
        timeframe="5m",
        trend_state=trend,
        volatility_state=volatility,
        candle_count=3,
        lookback=3,
        reason="test regime",
    )


def signal(direction=Direction.BUY, entry=1.0800, stop=1.0790, target=1.0820):
    return ForexSignal(
        symbol="EURUSD",
        timeframe="5m",
        direction=direction,
        entry_price=entry,
        stop_loss=stop,
        take_profit=target,
        timestamp="2026-06-06T09:10:00Z",
        strategy_name="sprint_4_intraday_trend_follow_v1",
        metadata={
            "source": "sprint_4_signal_rules",
            "setup_quality": "research",
            "session": "fixture",
            "regime_trend": TRENDING_UP if direction == Direction.BUY else TRENDING_DOWN,
            "regime_volatility": NORMAL_VOLATILITY,
            "reasons": ["trend", "local fixture"],
        },
    )


def test_confidence_v2_scores_valid_trend_aligned_buy():
    assessment = ConfidenceEngineV2(ForexEngineConfig()).score_signal(signal(), regime(TRENDING_UP))
    assert assessment.band in (ConfidenceBand.TRADE_CANDIDATE, ConfidenceBand.HIGH_QUALITY)
    assert assessment.allowed


def test_confidence_v2_scores_valid_trend_aligned_sell():
    sell_signal = signal(Direction.SELL, entry=1.0800, stop=1.0810, target=1.0780)
    assessment = ConfidenceEngineV2(ForexEngineConfig()).score_signal(sell_signal, regime(TRENDING_DOWN))
    assert assessment.allowed


def test_confidence_v2_blocks_invalid_buy_risk_reward():
    assessment = ConfidenceEngineV2(ForexEngineConfig()).score_signal(
        signal(Direction.BUY, entry=1.0800, stop=1.0810, target=1.0790),
        regime(TRENDING_UP),
    )
    assert assessment.band == ConfidenceBand.BLOCKED
    assert "risk/reward" in assessment.blocked_reason


def test_confidence_v2_blocks_invalid_sell_risk_reward():
    sell_signal = signal(Direction.SELL, entry=1.0800, stop=1.0790, target=1.0810)
    assessment = ConfidenceEngineV2(ForexEngineConfig()).score_signal(sell_signal, regime(TRENDING_DOWN))
    assert assessment.band == ConfidenceBand.BLOCKED
    assert "risk/reward" in assessment.blocked_reason


def test_confidence_v2_penalizes_regime_mismatch():
    aligned = ConfidenceEngineV2(ForexEngineConfig()).score_signal(signal(), regime(TRENDING_UP))
    mismatch = ConfidenceEngineV2(ForexEngineConfig()).score_signal(signal(), regime(TRENDING_DOWN))
    assert mismatch.score < aligned.score


def test_confidence_v2_penalizes_ranging_for_trend_follow():
    assessment = ConfidenceEngineV2(ForexEngineConfig()).score_signal(signal(), regime(RANGING))
    assert assessment.band in (ConfidenceBand.WATCHLIST, ConfidenceBand.BLOCKED)


def test_confidence_v2_low_volatility_reduces_score():
    normal = ConfidenceEngineV2(ForexEngineConfig()).score_signal(signal(), regime(TRENDING_UP, NORMAL_VOLATILITY))
    low = ConfidenceEngineV2(ForexEngineConfig()).score_signal(signal(), regime(TRENDING_UP, LOW_VOLATILITY))
    assert low.score < normal.score
    assert low.band != ConfidenceBand.HIGH_QUALITY


def test_confidence_v2_high_volatility_reduces_or_blocks():
    normal = ConfidenceEngineV2(ForexEngineConfig()).score_signal(signal(), regime(TRENDING_UP, NORMAL_VOLATILITY))
    high = ConfidenceEngineV2(ForexEngineConfig()).score_signal(signal(), regime(TRENDING_UP, HIGH_VOLATILITY))
    assert high.score < normal.score


def test_confidence_v2_grade_thresholds():
    assert grade_for_score(85) == SetupGrade.A
    assert grade_for_score(75) == SetupGrade.B
    assert grade_for_score(65) == SetupGrade.C
    assert grade_for_score(50) == SetupGrade.D
    assert grade_for_score(49) == SetupGrade.F


def test_confidence_v2_band_thresholds():
    assert band_for_score(85) == ConfidenceBand.HIGH_QUALITY
    assert band_for_score(75) == ConfidenceBand.TRADE_CANDIDATE
    assert band_for_score(60) == ConfidenceBand.WATCHLIST
    assert band_for_score(59) == ConfidenceBand.BLOCKED
    assert band_for_score(90, "blocked") == ConfidenceBand.BLOCKED


def test_confidence_v2_components_are_explainable():
    assessment = ConfidenceEngineV2(ForexEngineConfig()).score_signal(signal(), regime(TRENDING_UP))
    assert assessment.components
    assert all(component.name and component.reason for component in assessment.components)


def test_confidence_v2_recommendations_present():
    assessment = ConfidenceEngineV2(ForexEngineConfig()).score_signal(signal(), regime(TRENDING_UP))
    assert assessment.recommendations


def test_confidence_v2_uses_signal_candidate_blocked_reason():
    candidate = SignalCandidate(
        symbol="EURUSD",
        timeframe="5m",
        direction=Direction.BUY,
        entry_price=1.0800,
        stop_loss=1.0790,
        take_profit=1.0820,
        strategy_name="sprint_4_intraday_trend_follow_v1",
        regime_trend=TRENDING_UP,
        regime_volatility=NORMAL_VOLATILITY,
        confidence_hint=75,
        blocked_reason="candidate blocked",
    )
    assessment = ConfidenceEngineV2(ForexEngineConfig()).score_signal(signal(), regime(TRENDING_UP), candidate)
    assert assessment.band == ConfidenceBand.BLOCKED
    assert assessment.blocked_reason == "candidate blocked"


def test_confidence_demo_imports_without_network():
    assert importlib.import_module("automation.forex_engine.run_confidence_demo").main


def test_all_fixture_signal_candidates_can_be_scored():
    config = ForexEngineConfig()
    engine = ConfidenceEngineV2(config)
    for symbol in config.symbols:
        candles = load_fixture_candles(symbol, "5m", config)
        rule_result = IntradaySignalRules(config).evaluate(candles)
        for candidate in rule_result.candidates:
            if candidate.blocked_reason is None:
                scored_signal = candidate_to_forex_signal(candidate, candles[-1].timestamp)
            else:
                continue
            assessment = engine.score_signal(scored_signal, rule_result.regime, candidate)
            assert assessment.mode == "PAPER_ONLY"


def test_existing_confidence_engine_still_imports():
    assessment = ConfidenceEngine(ForexEngineConfig()).score_signal(signal())
    assert assessment.score >= 0
