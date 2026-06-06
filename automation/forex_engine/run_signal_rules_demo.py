"""Run the AI_OS Forex Engine v1 Sprint 4 PAPER_ONLY signal rules demo."""

import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from automation.forex_engine.config import ForexEngineConfig, validate_config
from automation.forex_engine.market_data import load_fixture_candles
from automation.forex_engine.signal_rules import IntradaySignalRules


def main() -> int:
    config = ForexEngineConfig()
    validate_config(config)
    timeframe = "5m"
    rules = IntradaySignalRules(config)
    results = []

    print("AI_OS Forex Engine v1 Sprint 4 Regime + Signal Rules Demo")
    print(f"Mode: {config.mode}")
    print("Data source: local CSV fixtures only")
    print(f"Symbols tested: {', '.join(config.symbols)}")
    print(f"Timeframe: {timeframe}")

    for symbol in config.symbols:
        candles = load_fixture_candles(symbol, timeframe, config)
        result = rules.evaluate(candles)
        results.append(result)
        candidate = result.candidates[0] if result.candidates else None
        direction = candidate.direction if candidate else None
        blocked_reason = candidate.blocked_reason if candidate else None
        print(
            f"{symbol}: regime={result.regime.trend_state}, "
            f"volatility={result.regime.volatility_state}, "
            f"signal_candidates={len(result.candidates)}, accepted={result.accepted_count}, "
            f"blocked={result.blocked_count}, direction={direction}, blocked_reason={blocked_reason}"
        )

    print(f"Total candidates: {sum(len(result.candidates) for result in results)}")
    print(f"Total accepted: {sum(result.accepted_count for result in results)}")
    print(f"Total blocked: {sum(result.blocked_count for result in results)}")
    print("Safety note: Local research signals only; no broker/API/network/live execution path used.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
