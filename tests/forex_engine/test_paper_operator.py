from dataclasses import replace

from automation.forex_engine.config import ForexEngineConfig
from automation.forex_engine.models import (
    AlertState,
    EngineMode,
    OptimizationCandidate,
    OperatorAlert,
    PaperOperatorStatus,
    PauseReason,
    RiskPosture,
    StrategyComparisonResult,
    StrategyScorecard,
    StrategyStatus,
    SupervisorSummary,
    WalkForwardResult,
    WalkForwardSplit,
    WalkForwardStatus,
    WalkForwardWindowResult,
)
from automation.forex_engine.paper_operator import PaperOperator


def _scorecard(status=StrategyStatus.INSUFFICIENT_DATA):
    return StrategyScorecard(
        mode=EngineMode.PAPER_ONLY,
        strategy_name="test_strategy",
        symbol="EURUSD",
        timeframe="5m",
        score=40,
        status=status,
        rank=1,
        trades=1,
        wins=0,
        losses=1,
        win_rate_pct=0,
        profit_factor=0.0,
        net_pnl_usd=-1.0,
        max_drawdown_usd=1.0,
        max_drawdown_pct=0.2,
        starting_balance_usd=500.0,
        ending_balance_usd=499.0,
        optimization_candidates=[
            OptimizationCandidate("sample_size", "Small sample.", "HIGH", "Use more candles.")
        ],
    )


def _comparison(status=StrategyStatus.INSUFFICIENT_DATA):
    return StrategyComparisonResult(
        mode=EngineMode.PAPER_ONLY,
        compared_at="2026-06-06T00:00:00+00:00",
        strategy_count=1,
        scorecards=[_scorecard(status)],
        insufficient_data_count=1 if status == StrategyStatus.INSUFFICIENT_DATA else 0,
    )


def _walk_forward(status=WalkForwardStatus.INSUFFICIENT_DATA):
    split = WalkForwardSplit(
        mode=EngineMode.PAPER_ONLY,
        symbol="EURUSD",
        timeframe="5m",
        train_ratio=0.6,
        test_ratio=0.4,
        train_count=2,
        test_count=1,
        train_start="2026-06-06T00:00:00Z",
        train_end="2026-06-06T00:05:00Z",
        test_start="2026-06-06T00:10:00Z",
        test_end="2026-06-06T00:10:00Z",
    )
    window = WalkForwardWindowResult(
        mode=EngineMode.PAPER_ONLY,
        symbol="EURUSD",
        timeframe="5m",
        window_name="train",
        candles_processed=2,
        trades=0,
        net_pnl_usd=0.0,
        win_rate_pct=0.0,
        profit_factor=None,
        max_drawdown_usd=0.0,
        max_drawdown_pct=0.0,
        status=status,
        summary_note="test",
    )
    return WalkForwardResult(
        mode=EngineMode.PAPER_ONLY,
        symbol="EURUSD",
        timeframe="5m",
        strategy_name="test_strategy",
        split=split,
        train_result=window,
        test_result=replace(window, window_name="test"),
        degradation_pct=None,
        status=status,
    )


def _active_names(alerts):
    return {alert.name for alert in alerts if alert.active}


def test_paper_operator_boundary_ok_alert():
    alerts = PaperOperator(ForexEngineConfig()).evaluate_alerts()
    assert AlertState.PAPER_ONLY_BOUNDARY_OK in _active_names(alerts)


def test_non_paper_mode_blocks_operator():
    operator = PaperOperator(replace(ForexEngineConfig(), mode="NOT_PAPER"))
    alerts = operator.evaluate_alerts(validation_passed=True)
    assert operator.determine_operator_status(alerts, validation_passed=True) == PaperOperatorStatus.BLOCKED


def test_insufficient_data_alert_active():
    alerts = PaperOperator(ForexEngineConfig()).evaluate_alerts(
        strategy_comparison=_comparison(),
        walk_forward_results=[_walk_forward()],
    )
    assert AlertState.INSUFFICIENT_DATA_ALERT in _active_names(alerts)


def test_profit_milestone_alert():
    alerts = PaperOperator(ForexEngineConfig()).evaluate_alerts(net_pnl_usd=50.0)
    assert AlertState.PROFIT_MILESTONE_ALERT in _active_names(alerts)


def test_loss_streak_alert():
    config = ForexEngineConfig()
    alerts = PaperOperator(config).evaluate_alerts(consecutive_losses=config.pause_after_consecutive_losses)
    assert AlertState.LOSS_STREAK_ALERT in _active_names(alerts)


def test_daily_drawdown_alert():
    alerts = PaperOperator(ForexEngineConfig()).evaluate_alerts(current_daily_pnl_usd=-10.0)
    assert AlertState.DAILY_DRAWDOWN_ALERT in _active_names(alerts)


def test_weekly_drawdown_alert():
    alerts = PaperOperator(ForexEngineConfig()).evaluate_alerts(weekly_drawdown_pct=5.0)
    assert AlertState.WEEKLY_DRAWDOWN_ALERT in _active_names(alerts)


def test_validation_health_alert():
    alerts = PaperOperator(ForexEngineConfig()).evaluate_alerts(validation_passed=False)
    assert AlertState.VALIDATION_HEALTH_ALERT in _active_names(alerts)


def test_risk_posture_paused_for_hard_alert():
    operator = PaperOperator(ForexEngineConfig())
    alerts = [OperatorAlert(AlertState.LOSS_STREAK_ALERT, True, "CRITICAL", "losses", "pause")]
    assert operator.determine_risk_posture(alerts) == RiskPosture.PAUSED


def test_risk_posture_conservative_for_insufficient_data():
    operator = PaperOperator(ForexEngineConfig())
    alerts = [OperatorAlert(AlertState.INSUFFICIENT_DATA_ALERT, True, "WARN", "small sample", "expand data")]
    assert operator.determine_risk_posture(alerts) == RiskPosture.CONSERVATIVE


def test_operator_status_paused_for_insufficient_data():
    operator = PaperOperator(ForexEngineConfig())
    alerts = [OperatorAlert(AlertState.INSUFFICIENT_DATA_ALERT, True, "WARN", "small sample", "expand data")]
    assert operator.determine_operator_status(alerts) == PaperOperatorStatus.PAUSED_FOR_INSUFFICIENT_DATA


def test_operator_status_paused_for_risk_limit():
    operator = PaperOperator(ForexEngineConfig())
    alerts = [OperatorAlert(AlertState.DAILY_DRAWDOWN_ALERT, True, "CRITICAL", "drawdown", "pause")]
    assert operator.determine_operator_status(alerts) == PaperOperatorStatus.PAUSED_FOR_RISK_LIMIT


def test_operator_status_paused_for_loss_streak():
    operator = PaperOperator(ForexEngineConfig())
    alerts = [OperatorAlert(AlertState.LOSS_STREAK_ALERT, True, "CRITICAL", "losses", "pause")]
    assert operator.determine_operator_status(alerts) == PaperOperatorStatus.PAUSED_FOR_LOSS_STREAK


def test_supervisor_summary_never_promotion_ready_in_sprint_8():
    operator = PaperOperator(ForexEngineConfig())
    report = operator.build_daily_report(strategy_comparison=_comparison(), walk_forward_results=[_walk_forward()])
    summary = operator.build_supervisor_summary(report)
    assert isinstance(summary, SupervisorSummary)
    assert summary.promotion_ready is False


def test_operator_report_format_contains_required_sections():
    operator = PaperOperator(ForexEngineConfig())
    report = operator.build_daily_report(strategy_comparison=_comparison(), walk_forward_results=[_walk_forward()])
    formatted = operator.format_operator_report(report)
    assert "Mode: PAPER_ONLY" in formatted
    assert "Risk posture:" in formatted
    assert "Active alerts:" in formatted
    assert "Next safe action:" in formatted
    assert report.pause_reason == PauseReason.INSUFFICIENT_DATA


def test_paper_operator_demo_imports_without_network():
    import automation.forex_engine.run_paper_operator_demo as demo

    assert demo.main


def test_paper_operator_demo_builds_report_from_fixture_stack():
    from automation.forex_engine.run_paper_operator_demo import build_demo_report

    report, summary, comparison, walk_forward_results = build_demo_report()
    assert report.mode == EngineMode.PAPER_ONLY
    assert summary.promotion_ready is False
    assert comparison.scorecards
    assert walk_forward_results


def test_existing_demos_still_import():
    import automation.forex_engine.run_backtest_demo as backtest_demo
    import automation.forex_engine.run_confidence_demo as confidence_demo
    import automation.forex_engine.run_market_data_demo as market_data_demo
    import automation.forex_engine.run_paper_demo as paper_demo
    import automation.forex_engine.run_signal_rules_demo as signal_rules_demo
    import automation.forex_engine.run_strategy_comparison_demo as strategy_comparison_demo
    import automation.forex_engine.run_walk_forward_demo as walk_forward_demo

    assert backtest_demo.main
    assert confidence_demo.main
    assert market_data_demo.main
    assert paper_demo.main
    assert signal_rules_demo.main
    assert strategy_comparison_demo.main
    assert walk_forward_demo.main
