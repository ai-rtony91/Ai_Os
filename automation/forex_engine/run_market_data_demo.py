"""Run the AI_OS Forex Engine v1 Sprint 2 local market data demo."""

from automation.forex_engine.config import ForexEngineConfig, validate_config
from automation.forex_engine.market_data import load_fixture_candles, summarize_candles


def main() -> int:
    config = ForexEngineConfig()
    validate_config(config)

    summaries = []
    timeframe = "5m"
    for symbol in config.symbols:
        candles = load_fixture_candles(symbol, timeframe, config)
        summaries.append(summarize_candles(candles))

    print("AI_OS Forex Engine v1 Sprint 2 Market Data Demo")
    print(f"Mode: {config.mode}")
    print(f"Loaded symbols: {', '.join(summary['symbol'] for summary in summaries)}")
    print(f"Loaded timeframe: {timeframe}")
    for summary in summaries:
        print(
            f"{summary['symbol']}: candles={summary['count']}, "
            f"first={summary['first_timestamp']}, last={summary['last_timestamp']}, "
            f"low={summary['min_low']}, high={summary['max_high']}, "
            f"first_close={summary['first_close']}, last_close={summary['last_close']}"
        )
    print("Safety note: local fixture data only; no broker/API/network call used.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
