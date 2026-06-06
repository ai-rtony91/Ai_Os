"""Run the AI_OS Forex Engine v1 Sprint 11 parameter optimization demo."""

import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from automation.forex_engine.backtest import run_backtest
from automation.forex_engine.config import ForexEngineConfig, validate_config
from automation.forex_engine.market_data import load_fixture_candles
from automation.forex_engine.models import BacktestConfig
from automation.forex_engine.parameter_optimization import OPTIMIZATION_MODE, ParameterOptimizationEngine
from automation.forex_engine.strategy_comparison import StrategyComparisonEngine


def build_demo_result(config=None):
    config = config or ForexEngineConfig()
    validate_config(config)
    timeframe = "5m"
    backtest_results = []
    for symbol in config.symbols:
        candles = load_fixture_candles(symbol, timeframe, config)
        backtest_results.append(
            run_backtest(
                candles,
                BacktestConfig(
                    symbol=symbol,
                    timeframe=timeframe,
                    starting_balance_usd=config.starting_balance_usd,
                    strategy_name="sprint_4_intraday_rules_v1",
                ),
            )
        )
    scorecards = StrategyComparisonEngine(config).compare_results(backtest_results).scorecards
    engine = ParameterOptimizationEngine(config)
    return engine.compare_parameter_sets(engine.default_parameter_sets(), scorecards)


def main() -> int:
    config = ForexEngineConfig()
    result = build_demo_result(config)
    recommendations = []
    for score in result.scores:
        recommendations.extend(score.recommendations)
    deduped_recommendations = list(dict.fromkeys(recommendations))

    print("AI_OS Forex Engine v1 Sprint 11 Parameter Optimization Demo")
    print(f"Mode: {config.mode}")
    print(f"Optimization mode: {OPTIMIZATION_MODE}")
    print("Data source: local fixture/research summaries only")
    print(f"Parameter sets tested: {', '.join(score.parameter_set_name for score in result.scores)}")
    print(f"Best parameter set: {result.best_parameter_set}")
    print(f"Optimization status: {result.status}")
    print(f"Overfitting risk: {result.overfitting_risk}")
    for score in result.scores:
        print(
            f"{score.parameter_set_name}: score={score.score:.2f}, status={score.status}, "
            f"risk={score.overfitting_risk}, sample={score.sample_size}"
        )
    print(f"Recommendations: {'; '.join(deduped_recommendations)}")
    print("Safety note: Local parameter optimization scaffold only; no broker/API/network/live execution path used.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
