"""Deterministic confidence scoring for PAPER_ONLY Sprint 1 signals."""

from automation.forex_engine.models import ConfidenceAssessment, Direction


class ConfidenceEngine:
    def __init__(self, config):
        self.config = config

    def score_signal(self, signal, regime=None) -> ConfidenceAssessment:
        score = 50
        reasons = ["Base deterministic PAPER_ONLY confidence score: 50."]

        if signal.symbol in self.config.symbols:
            score += 8
            reasons.append("Allowed symbol.")
        else:
            score -= 15
            reasons.append("Unsupported symbol.")

        if signal.timeframe in self.config.timeframes:
            score += 8
            reasons.append("Allowed timeframe.")
        else:
            score -= 10
            reasons.append("Unsupported timeframe.")

        structure_valid = self._has_valid_structure(signal)
        if structure_valid:
            score += 10
            reasons.append("Valid stop and target structure.")
        else:
            score -= 20
            reasons.append("Invalid stop or target structure.")

        risk_to_reward = self._risk_to_reward(signal)
        if risk_to_reward >= 1.0:
            score += 8
            reasons.append("Risk-to-reward is at least 1.0.")
        else:
            score -= 8
            reasons.append("Risk-to-reward is below 1.0.")

        if signal.strategy_name:
            score += 5
            reasons.append("Strategy name provided.")
        if signal.metadata.get("setup_quality"):
            score += 6
            reasons.append("Setup quality metadata provided.")
        if signal.metadata.get("session"):
            score += 5
            reasons.append("Session metadata provided.")

        score = max(0, min(100, score))
        allowed = score >= self.config.minimum_confidence_to_trade
        return ConfidenceAssessment(
            score=score,
            reasons=reasons,
            allowed=allowed,
            blocked_reason=None if allowed else "Confidence below PAPER_ONLY trade threshold.",
        )

    def _has_valid_structure(self, signal) -> bool:
        if signal.entry_price <= 0 or signal.stop_loss <= 0 or signal.take_profit <= 0:
            return False
        if signal.direction == Direction.BUY:
            return signal.stop_loss < signal.entry_price < signal.take_profit
        if signal.direction == Direction.SELL:
            return signal.take_profit < signal.entry_price < signal.stop_loss
        return False

    def _risk_to_reward(self, signal) -> float:
        risk = abs(signal.entry_price - signal.stop_loss)
        reward = abs(signal.take_profit - signal.entry_price)
        if risk <= 0:
            return 0.0
        return reward / risk
