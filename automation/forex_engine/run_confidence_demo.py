"""Run the AI_OS Forex Engine v1 Sprint 5 PAPER_ONLY confidence demo."""

import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from automation.forex_engine.confidence_v2 import ConfidenceEngineV2
from automation.forex_engine.config import ForexEngineConfig, validate_config
from automation.forex_engine.market_data import load_fixture_candles
from automation.forex_engine.models import ConfidenceBand
from automation.forex_engine.signal_rules import IntradaySignalRules, candidate_to_forex_signal


def main() -> int:
    config = ForexEngineConfig()
    validate_config(config)
    timeframe = "5m"
    confidence_engine = ConfidenceEngineV2(config)
    signal_rules = IntradaySignalRules(config)
    assessments = []

    print("AI_OS Forex Engine v1 Sprint 5 Confidence v2 Demo")
    print(f"Mode: {config.mode}")
    print("Data source: local CSV fixtures only")
    print(f"Symbols tested: {', '.join(config.symbols)}")
    print(f"Timeframe: {timeframe}")

    for symbol in config.symbols:
        candles = load_fixture_candles(symbol, timeframe, config)
        rule_result = signal_rules.evaluate(candles)
        for candidate in rule_result.candidates:
            if candidate.blocked_reason is None:
                signal = candidate_to_forex_signal(candidate, candles[-1].timestamp)
            else:
                signal = _signal_from_blocked_candidate(candidate, candles[-1].timestamp)
            assessment = confidence_engine.score_signal(signal, rule_result.regime, candidate)
            assessments.append(assessment)
            print(
                f"{symbol} {candidate.direction}: regime={rule_result.regime.trend_state}, "
                f"volatility={rule_result.regime.volatility_state}, score={assessment.score}, "
                f"grade={assessment.grade}, band={assessment.band}, allowed={assessment.allowed}, "
                f"reduced_risk={assessment.reduced_risk}, blocked_reason={assessment.blocked_reason}"
            )
            print(f"  reasons: {assessment.components[0].reason}; {assessment.recommendations[0]}")

    print(f"Total assessed: {len(assessments)}")
    print(f"High quality count: {sum(1 for item in assessments if item.band == ConfidenceBand.HIGH_QUALITY)}")
    print(f"Trade candidate count: {sum(1 for item in assessments if item.band == ConfidenceBand.TRADE_CANDIDATE)}")
    print(f"Watchlist count: {sum(1 for item in assessments if item.band == ConfidenceBand.WATCHLIST)}")
    print(f"Blocked count: {sum(1 for item in assessments if item.band == ConfidenceBand.BLOCKED)}")
    print("Safety note: Local research confidence only; no broker/API/network/live execution path used.")
    return 0


def _signal_from_blocked_candidate(candidate, timestamp):
    from automation.forex_engine.models import ForexSignal

    return ForexSignal(
        symbol=candidate.symbol,
        timeframe=candidate.timeframe,
        direction=candidate.direction or "BLOCKED",
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


if __name__ == "__main__":
    raise SystemExit(main())
