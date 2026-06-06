"""Run the AI_OS Forex Engine v1 Sprint 3 PAPER_ONLY backtest demo."""

import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from automation.forex_engine.backtest import run_backtest_for_fixture
from automation.forex_engine.config import ForexEngineConfig, validate_config


def main() -> int:
    config = ForexEngineConfig()
    validate_config(config)
    timeframe = "5m"
    results = [run_backtest_for_fixture(symbol, timeframe, config) for symbol in config.symbols]

    print("AI_OS Forex Engine v1 Sprint 3 Backtest Demo")
    print(f"Mode: {config.mode}")
    print("Data source: local CSV fixtures only")
    print(f"Symbols tested: {', '.join(config.symbols)}")
    print(f"Timeframe: {timeframe}")

    total_trades = 0
    combined_net_pnl = 0.0
    for result in results:
        total_trades += result.trades_closed
        combined_net_pnl += result.net_pnl_usd
        print(
            f"{result.symbol}: candles={result.candles_processed}, "
            f"signals={result.signals_generated}, trades_opened={result.trades_opened}, "
            f"trades_closed={result.trades_closed}, net_pnl={result.net_pnl_usd:.2f}, "
            f"win_rate={result.win_rate_pct:.2f}%, profit_factor={result.profit_factor}"
        )

    print(f"Combined total trades: {total_trades}")
    print(f"Combined net PnL: {combined_net_pnl:.2f} USD")
    print("Safety note: No broker/API/network/live execution path used.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
