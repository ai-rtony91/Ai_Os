"""Run the AI_OS Forex Engine v1 Sprint 8 PAPER_ONLY paper operator demo."""

import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from automation.forex_engine.backtest import run_backtest
from automation.forex_engine.config import ForexEngineConfig, validate_config
from automation.forex_engine.market_data import load_fixture_candles
from automation.forex_engine.models import BacktestConfig
from automation.forex_engine.paper_operator import PaperOperator
from automation.forex_engine.strategy_comparison import StrategyComparisonEngine
from automation.forex_engine.walk_forward import WalkForwardEngine


def build_demo_report(config=None):
    config = config or ForexEngineConfig()
    validate_config(config)
    timeframe = "5m"
    backtest_results = []
    walk_forward_results = []
    walk_forward_engine = WalkForwardEngine(config)

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
        walk_forward_results.append(walk_forward_engine.run_walk_forward(candles, train_ratio=0.6))

    comparison = StrategyComparisonEngine(config).compare_results(backtest_results)
    operator = PaperOperator(config)
    report = operator.build_daily_report(
        strategy_comparison=comparison,
        walk_forward_results=walk_forward_results,
        net_pnl_usd=sum(result.net_pnl_usd for result in backtest_results),
        current_balance_usd=config.starting_balance_usd + sum(result.net_pnl_usd for result in backtest_results),
        current_daily_pnl_usd=0.0,
        consecutive_losses=0,
        weekly_drawdown_pct=0.0,
        validation_passed=True,
    )
    supervisor_summary = operator.build_supervisor_summary(report)
    return report, supervisor_summary, comparison, walk_forward_results


def main() -> int:
    config = ForexEngineConfig()
    report, supervisor_summary, comparison, walk_forward_results = build_demo_report(config)
    operator = PaperOperator(config)
    active_alerts = [alert.name for alert in report.alerts if alert.active]

    print("AI_OS Forex Engine v1 Sprint 8 Paper Operator Demo")
    print(f"Mode: {report.mode}")
    print("Data source: local fixture/research summaries only")
    print("Account profile: 500 USD starter profile")
    print(f"Risk posture: {report.risk_posture}")
    print(f"Paper operator status: {report.operator_status}")
    print(f"Pause reason: {report.pause_reason}")
    print(f"Active alerts: {', '.join(active_alerts)}")
    print(f"Daily PnL or research PnL summary: {report.net_pnl_usd:.2f} USD")
    print(f"Strategy scorecards: {comparison.strategy_count}")
    print(f"Walk-forward results: {len(walk_forward_results)}")
    print(operator.format_supervisor_summary(supervisor_summary))
    print(f"Next safe action: {report.next_safe_action}")
    print("Safety note: Local paper-operator summary only; no broker/API/network/live execution path used.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
