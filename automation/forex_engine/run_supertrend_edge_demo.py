"""Run the PAPER_ONLY Supertrend edge research demo."""

from automation.forex_engine.backtest import run_supertrend_edge_backtest
from automation.forex_engine.daily_edge_report import deterministic_supertrend_sample


def main() -> int:
    candles = deterministic_supertrend_sample()
    result = run_supertrend_edge_backtest(candles)
    metrics = result["metrics"]
    print("AI_OS Forex Engine Supertrend Edge Demo")
    print(f"Mode: {result['mode']}")
    print(f"Strategy: {result['strategy_name']}")
    print("Data source: deterministic local sample")
    print(f"Candles: {result['candles_processed']}")
    print(f"Trades: {metrics['total_trades']}")
    print(f"Expectancy R: {metrics['expectancy_r']}")
    print(f"Profit factor: {metrics['profit_factor']}")
    print("Safety note: PAPER_ONLY research; no broker/API/network/live execution.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
