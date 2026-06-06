"""Run the AI_OS Forex Engine v1 Sprint 10 PAPER_ONLY risk management demo."""

import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from automation.forex_engine.config import ForexEngineConfig, validate_config
from automation.forex_engine.models import EngineMode, RiskManagementScenario
from automation.forex_engine.risk_management import RiskManagementEngine, WEEKLY_DRAWDOWN_THRESHOLD_PCT


def build_demo_scenarios(config):
    base = {
        "mode": EngineMode.PAPER_ONLY,
        "starting_balance_usd": config.starting_balance_usd,
        "current_balance_usd": config.starting_balance_usd,
        "current_daily_pnl_usd": 0.0,
        "weekly_drawdown_pct": 0.0,
        "consecutive_losses": 0,
        "open_trade_count": 0,
        "proposed_order_risk_usd": 2.0,
        "validation_passed": True,
    }
    return [
        RiskManagementScenario(name="normal", **base),
        RiskManagementScenario(name="near_loss_streak", **{**base, "consecutive_losses": 2}),
        RiskManagementScenario(name="loss_streak", **{**base, "consecutive_losses": 3}),
        RiskManagementScenario(name="daily_drawdown_breach", **{**base, "current_daily_pnl_usd": -10.0}),
        RiskManagementScenario(name="weekly_drawdown_breach", **{**base, "weekly_drawdown_pct": 5.0}),
        RiskManagementScenario(name="max_open_trades", **{**base, "open_trade_count": 2}),
        RiskManagementScenario(name="oversize_order", **{**base, "proposed_order_risk_usd": 3.0}),
        RiskManagementScenario(name="non_paper_mode", **{**base, "mode": "LIVE"}),
    ]


def main() -> int:
    config = ForexEngineConfig()
    validate_config(config)
    engine = RiskManagementEngine(config)
    daily_limit = config.starting_balance_usd * (config.max_daily_drawdown_pct / 100)

    print("AI_OS Forex Engine v1 Sprint 10 Risk Management Demo")
    print(f"Mode: {config.mode}")
    print("Account profile: 500 USD starter profile")
    print(f"Risk per trade limit: {config.paper_risk_per_trade_pct} percent paper")
    print(f"Daily drawdown limit: {config.max_daily_drawdown_pct} percent ({daily_limit:.2f} USD)")
    print(f"Weekly drawdown limit: {WEEKLY_DRAWDOWN_THRESHOLD_PCT} percent")
    print(f"Max open paper trades: {config.max_open_trades_paper}")

    for scenario in build_demo_scenarios(config):
        report = engine.evaluate_scenario(scenario)
        kill_report = engine.build_kill_switch_report(report)
        print(
            f"Scenario: {scenario.name} | Risk action: {report.risk_action} | "
            f"Kill switch: {kill_report.state} | Breaches: {', '.join(report.breaches)} | "
            f"Recommended action: {report.recommended_action}"
        )

    print("Safety note: Local risk management model only; no broker/API/network/live execution path used.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
