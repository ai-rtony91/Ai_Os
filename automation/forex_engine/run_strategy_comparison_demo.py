"""Run the AI_OS Forex Engine v1 Sprint 6 PAPER_ONLY strategy comparison demo."""

import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from automation.forex_engine.backtest import run_backtest
from automation.forex_engine.config import ForexEngineConfig, validate_config
from automation.forex_engine.market_data import load_fixture_candles
from automation.forex_engine.models import BacktestConfig
from automation.forex_engine.strategy_comparison import StrategyComparisonEngine


def main() -> int:
    config = ForexEngineConfig()
    validate_config(config)
    timeframe = "5m"
    strategies = ("sprint_3_demo_strategy", "sprint_4_intraday_rules_v1")
    results = []
    for strategy_name in strategies:
        for symbol in config.symbols:
            candles = load_fixture_candles(symbol, timeframe, config)
            backtest_config = BacktestConfig(
                symbol=symbol,
                timeframe=timeframe,
                starting_balance_usd=config.starting_balance_usd,
                strategy_name=strategy_name,
            )
            results.append(run_backtest(candles, backtest_config))

    comparison = StrategyComparisonEngine(config).compare_results(results)
    print("AI_OS Forex Engine v1 Sprint 6 Strategy Comparison Demo")
    print(f"Mode: {comparison.mode}")
    print("Data source: local fixture backtests only")
    print(f"Strategies compared: {', '.join(strategies)}")
    print(f"Symbols included: {', '.join(config.symbols)}")
    for scorecard in comparison.scorecards:
        candidate_names = ", ".join(item.name for item in scorecard.optimization_candidates) or "none"
        print(
            f"Rank {scorecard.rank}: {scorecard.strategy_name} {scorecard.symbol} | "
            f"score={scorecard.score:.2f} | status={scorecard.status} | trades={scorecard.trades} | "
            f"net_pnl={scorecard.net_pnl_usd:.2f} | win_rate={scorecard.win_rate_pct:.2f} | "
            f"profit_factor={scorecard.profit_factor} | drawdown={scorecard.max_drawdown_pct:.2f} | "
            f"optimization={candidate_names}"
        )
    print(f"Top strategy: {comparison.top_strategy}")
    print(f"Research candidate count: {comparison.research_candidate_count}")
    print(f"Watchlist count: {comparison.watchlist_count}")
    print(f"Rejected count: {comparison.rejected_count}")
    print(f"Insufficient data count: {comparison.insufficient_data_count}")
    print("Safety note: Local strategy comparison only; no broker/API/network/live execution path used.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
