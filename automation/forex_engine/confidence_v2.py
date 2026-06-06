"""Explainable PAPER_ONLY confidence scoring v2 for Sprint 5 research."""

from automation.forex_engine.models import (
    ConfidenceBand,
    ConfidenceComponent,
    Direction,
    EngineMode,
    SetupGrade,
    SetupQualityAssessment,
)
from automation.forex_engine.regime import (
    HIGH_VOLATILITY,
    LOW_VOLATILITY,
    NORMAL_VOLATILITY,
    RANGING,
    TRENDING_DOWN,
    TRENDING_UP,
    UNKNOWN,
)


class ConfidenceEngineV2:
    def __init__(self, config):
        self.config = config

    def score_signal(self, signal, regime_assessment=None, signal_candidate=None) -> SetupQualityAssessment:
        components = [ConfidenceComponent("base", 50, "Base deterministic PAPER_ONLY research score.")]
        blocked_reason = None

        if signal_candidate is not None and signal_candidate.blocked_reason:
            blocked_reason = signal_candidate.blocked_reason
            components.append(
                ConfidenceComponent("candidate_block", -50, "SignalCandidate was already blocked.", {})
            )

        self._score_symbol_timeframe(signal, components)
        direction_block = self._score_direction(signal, components)
        blocked_reason = blocked_reason or direction_block
        risk_reward, structure_block = self._score_risk_reward(signal, components)
        blocked_reason = blocked_reason or structure_block
        self._score_regime(signal, regime_assessment, components)
        self._score_volatility(regime_assessment, components)
        self._score_metadata(signal, components)

        score = max(0, min(100, sum(component.score_delta for component in components)))
        grade = grade_for_score(score)
        band = band_for_score(score, blocked_reason)
        allowed = band in (ConfidenceBand.HIGH_QUALITY, ConfidenceBand.TRADE_CANDIDATE)
        reduced_risk = band == ConfidenceBand.WATCHLIST
        if band == ConfidenceBand.BLOCKED and blocked_reason is None:
            blocked_reason = "Confidence score below PAPER_ONLY research threshold."

        recommendations = build_recommendations(
            score=score,
            band=band,
            risk_reward=risk_reward,
            regime_assessment=regime_assessment,
            blocked_reason=blocked_reason,
        )
        return SetupQualityAssessment(
            mode=EngineMode.PAPER_ONLY,
            symbol=signal.symbol,
            timeframe=signal.timeframe,
            direction=signal.direction,
            score=score,
            grade=grade,
            band=band,
            allowed=allowed,
            reduced_risk=reduced_risk,
            blocked_reason=blocked_reason,
            components=components,
            recommendations=recommendations,
            metadata={
                "paper_only": True,
                "risk_reward": risk_reward,
                "research_only": True,
            },
        )

    def _score_symbol_timeframe(self, signal, components):
        if signal.symbol in self.config.symbols:
            components.append(ConfidenceComponent("symbol", 6, "Symbol is configured for PAPER_ONLY research."))
        else:
            components.append(ConfidenceComponent("symbol", -20, "Symbol is not configured."))
        if signal.timeframe in self.config.timeframes:
            components.append(ConfidenceComponent("timeframe", 6, "Timeframe is configured."))
        else:
            components.append(ConfidenceComponent("timeframe", -15, "Timeframe is not configured."))

    def _score_direction(self, signal, components):
        if signal.direction in (Direction.BUY, Direction.SELL):
            components.append(ConfidenceComponent("direction", 5, "Direction is BUY or SELL."))
            return None
        components.append(ConfidenceComponent("direction", -50, "Direction is invalid."))
        return "Invalid direction."

    def _score_risk_reward(self, signal, components):
        risk_reward = 0.0
        if signal.direction == Direction.BUY:
            risk = signal.entry_price - signal.stop_loss
            reward = signal.take_profit - signal.entry_price
        elif signal.direction == Direction.SELL:
            risk = signal.stop_loss - signal.entry_price
            reward = signal.entry_price - signal.take_profit
        else:
            components.append(ConfidenceComponent("risk_reward", -30, "Risk/reward cannot be calculated."))
            return risk_reward, "Invalid direction."

        if risk <= 0 or reward <= 0:
            components.append(
                ConfidenceComponent(
                    "risk_reward",
                    -45,
                    "Invalid risk/reward structure.",
                    {"risk": risk, "reward": reward},
                )
            )
            return risk_reward, "Invalid risk/reward structure."

        risk_reward = reward / risk
        if risk_reward >= 2.0:
            delta = 14
            reason = "Reward-to-risk is at least 2.0."
        elif risk_reward >= 1.5:
            delta = 10
            reason = "Reward-to-risk is at least 1.5."
        elif risk_reward >= 1.0:
            delta = 5
            reason = "Reward-to-risk is at least 1.0."
        else:
            delta = -12
            reason = "Reward-to-risk is below 1.0."
        components.append(
            ConfidenceComponent("risk_reward", delta, reason, {"risk_reward": round(risk_reward, 4)})
        )
        return risk_reward, None if risk_reward >= 1.0 else "Reward-to-risk below PAPER_ONLY research minimum."

    def _score_regime(self, signal, regime_assessment, components):
        trend = _trend_from_inputs(signal, regime_assessment)
        if trend == UNKNOWN:
            components.append(ConfidenceComponent("regime", -6, "Regime is unknown."))
        elif trend == RANGING:
            components.append(ConfidenceComponent("regime", -35, "Ranging regime weakens trend-follow setup."))
        elif signal.direction == Direction.BUY and trend == TRENDING_UP:
            components.append(ConfidenceComponent("regime", 12, "BUY aligns with TRENDING_UP regime."))
        elif signal.direction == Direction.SELL and trend == TRENDING_DOWN:
            components.append(ConfidenceComponent("regime", 12, "SELL aligns with TRENDING_DOWN regime."))
        elif signal.direction in (Direction.BUY, Direction.SELL):
            components.append(ConfidenceComponent("regime", -18, "Signal direction conflicts with regime."))

    def _score_volatility(self, regime_assessment, components):
        volatility = _volatility_from_regime(regime_assessment)
        if volatility == NORMAL_VOLATILITY:
            components.append(ConfidenceComponent("volatility", 7, "Volatility is normal for Sprint 5 rules."))
        elif volatility == LOW_VOLATILITY:
            components.append(ConfidenceComponent("volatility", -25, "Low volatility weakens setup quality."))
        elif volatility == HIGH_VOLATILITY:
            components.append(ConfidenceComponent("volatility", -25, "High volatility requires caution."))
        else:
            components.append(ConfidenceComponent("volatility", -5, "Volatility is unknown."))

    def _score_metadata(self, signal, components):
        metadata = signal.metadata or {}
        if metadata.get("source") == "sprint_4_signal_rules":
            components.append(ConfidenceComponent("metadata_source", 5, "Signal came from Sprint 4 rules."))
        if metadata.get("setup_quality") in ("research", "demo", "clean"):
            components.append(ConfidenceComponent("setup_quality", 4, "Setup quality metadata is present."))
        if metadata.get("reasons"):
            components.append(ConfidenceComponent("reasons", 3, "Signal includes explainable reasons."))
        if metadata.get("session"):
            components.append(ConfidenceComponent("session", 2, "Session metadata is present."))


def grade_for_score(score):
    if score >= 85:
        return SetupGrade.A
    if score >= 75:
        return SetupGrade.B
    if score >= 65:
        return SetupGrade.C
    if score >= 50:
        return SetupGrade.D
    return SetupGrade.F


def band_for_score(score, blocked_reason=None):
    if blocked_reason or score < 60:
        return ConfidenceBand.BLOCKED
    if score >= 85:
        return ConfidenceBand.HIGH_QUALITY
    if score >= 75:
        return ConfidenceBand.TRADE_CANDIDATE
    return ConfidenceBand.WATCHLIST


def build_recommendations(score, band, risk_reward, regime_assessment, blocked_reason):
    recommendations = []
    if blocked_reason:
        recommendations.append(blocked_reason)
    if risk_reward and risk_reward < 1.5:
        recommendations.append("Improve reward-to-risk before considering this setup.")
    if regime_assessment:
        if regime_assessment.trend_state in (RANGING, UNKNOWN):
            recommendations.append("Wait for directional alignment with current regime.")
        if regime_assessment.volatility_state == HIGH_VOLATILITY:
            recommendations.append("Reduce risk or wait for volatility normalization.")
        if regime_assessment.volatility_state == LOW_VOLATILITY:
            recommendations.append("Wait for expansion or clearer movement.")
    if band in (ConfidenceBand.HIGH_QUALITY, ConfidenceBand.TRADE_CANDIDATE):
        recommendations.append("Candidate is acceptable for PAPER_ONLY research.")
    elif band == ConfidenceBand.WATCHLIST:
        recommendations.append("Keep this setup on PAPER_ONLY watchlist or use reduced risk.")
    if not recommendations:
        recommendations.append("Continue PAPER_ONLY research review.")
    return recommendations


def _trend_from_inputs(signal, regime_assessment):
    if regime_assessment is not None:
        return regime_assessment.trend_state
    return signal.metadata.get("regime_trend", UNKNOWN)


def _volatility_from_regime(regime_assessment):
    if regime_assessment is not None:
        return regime_assessment.volatility_state
    return UNKNOWN
