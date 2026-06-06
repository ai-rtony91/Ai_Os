from pathlib import Path

from automation.forex_engine.config import ForexEngineConfig
from automation.forex_engine.models import (
    EngineMode,
    KillSwitchState,
    RiskAction,
    RiskBreachType,
    RiskManagementScenario,
)
from automation.forex_engine.risk_management import RiskManagementEngine


def _scenario(**overrides):
    config = ForexEngineConfig()
    data = {
        "name": "normal",
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
    data.update(overrides)
    return RiskManagementScenario(**data)


def _engine():
    return RiskManagementEngine(ForexEngineConfig())


def test_normal_scenario_continue():
    report = _engine().evaluate_scenario(_scenario())
    assert report.risk_action == RiskAction.CONTINUE
    assert report.allowed is True


def test_daily_drawdown_triggers_kill_switch():
    report = _engine().evaluate_scenario(_scenario(name="daily", current_daily_pnl_usd=-10.0))
    assert report.risk_action == RiskAction.KILL_SWITCH
    assert RiskBreachType.DAILY_DRAWDOWN in report.breaches


def test_weekly_drawdown_triggers_kill_switch():
    report = _engine().evaluate_scenario(_scenario(name="weekly", weekly_drawdown_pct=5.0))
    assert report.risk_action == RiskAction.KILL_SWITCH
    assert RiskBreachType.WEEKLY_DRAWDOWN in report.breaches


def test_loss_streak_pauses_trading():
    report = _engine().evaluate_scenario(_scenario(name="losses", consecutive_losses=3))
    assert report.risk_action == RiskAction.PAUSE_TRADING
    assert RiskBreachType.LOSS_STREAK in report.breaches


def test_near_loss_streak_reduces_risk():
    report = _engine().evaluate_scenario(_scenario(name="near_losses", consecutive_losses=2))
    assert report.risk_action == RiskAction.REDUCE_RISK


def test_max_open_trades_blocks_order():
    report = _engine().evaluate_scenario(_scenario(name="max_open", open_trade_count=2))
    assert report.risk_action == RiskAction.BLOCK_ORDER
    assert RiskBreachType.MAX_OPEN_TRADES in report.breaches


def test_oversize_order_blocks_order():
    report = _engine().evaluate_scenario(_scenario(name="oversize", proposed_order_risk_usd=3.0))
    assert report.risk_action == RiskAction.BLOCK_ORDER
    assert RiskBreachType.ORDER_RISK_TOO_HIGH in report.breaches
    assert report.metadata["allowed_order_risk_usd"] == 2.5


def test_non_paper_mode_triggers_kill_switch():
    report = _engine().evaluate_scenario(_scenario(name="live", mode="LIVE"))
    assert report.risk_action == RiskAction.KILL_SWITCH
    assert RiskBreachType.NON_PAPER_MODE in report.breaches


def test_validation_failure_pauses_or_kills():
    report = _engine().evaluate_scenario(_scenario(name="validation", validation_passed=False))
    assert report.risk_action in (RiskAction.PAUSE_TRADING, RiskAction.KILL_SWITCH)
    assert RiskBreachType.VALIDATION_FAILED in report.breaches


def test_multiple_breaches_uses_highest_priority():
    report = _engine().evaluate_scenario(
        _scenario(name="multi", open_trade_count=2, current_daily_pnl_usd=-10.0)
    )
    assert report.risk_action == RiskAction.KILL_SWITCH
    assert RiskBreachType.MAX_OPEN_TRADES in report.breaches
    assert RiskBreachType.DAILY_DRAWDOWN in report.breaches


def test_kill_switch_report_for_daily_drawdown():
    engine = _engine()
    report = engine.evaluate_scenario(_scenario(name="daily", current_daily_pnl_usd=-10.0))
    kill_report = engine.build_kill_switch_report(report)
    assert kill_report.state in (KillSwitchState.ACTIVE, KillSwitchState.TRIGGERED)
    assert kill_report.reset_required is True


def test_kill_switch_not_triggered_for_simple_order_block():
    engine = _engine()
    report = engine.evaluate_scenario(_scenario(name="oversize", proposed_order_risk_usd=3.0))
    kill_report = engine.build_kill_switch_report(report)
    assert report.risk_action == RiskAction.BLOCK_ORDER
    assert kill_report.state == KillSwitchState.INACTIVE


def test_format_risk_report_contains_action_and_breaches():
    engine = _engine()
    report = engine.evaluate_scenario(_scenario(name="oversize", proposed_order_risk_usd=3.0))
    formatted = engine.format_risk_report(report)
    assert "Scenario: oversize" in formatted
    assert "Risk action: BLOCK_ORDER" in formatted
    assert "Breaches:" in formatted


def test_format_kill_switch_report_contains_next_safe_action():
    engine = _engine()
    report = engine.evaluate_scenario(_scenario(name="daily", current_daily_pnl_usd=-10.0))
    formatted = engine.format_kill_switch_report(engine.build_kill_switch_report(report))
    assert "Next safe action:" in formatted


def test_risk_management_demo_imports_without_network():
    import automation.forex_engine.run_risk_management_demo as demo

    assert demo.main


def test_existing_demos_still_import():
    import automation.forex_engine.run_backtest_demo as backtest_demo
    import automation.forex_engine.run_broker_sandbox_demo as broker_sandbox_demo
    import automation.forex_engine.run_confidence_demo as confidence_demo
    import automation.forex_engine.run_market_data_demo as market_data_demo
    import automation.forex_engine.run_paper_demo as paper_demo
    import automation.forex_engine.run_paper_operator_demo as paper_operator_demo
    import automation.forex_engine.run_signal_rules_demo as signal_rules_demo
    import automation.forex_engine.run_strategy_comparison_demo as strategy_comparison_demo
    import automation.forex_engine.run_walk_forward_demo as walk_forward_demo

    assert backtest_demo.main
    assert broker_sandbox_demo.main
    assert confidence_demo.main
    assert market_data_demo.main
    assert paper_demo.main
    assert paper_operator_demo.main
    assert signal_rules_demo.main
    assert strategy_comparison_demo.main
    assert walk_forward_demo.main


def test_no_live_trading_demo_created():
    assert not Path("automation/forex_engine/run_live_trading_demo.py").exists()
