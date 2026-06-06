from pathlib import Path

from automation.forex_engine.config import ForexEngineConfig
from automation.forex_engine.models import (
    EngineMode,
    OptimizationStatus,
    OverfittingRisk,
    ParameterSet,
    StrategyScorecard,
)
from automation.forex_engine.parameter_optimization import ParameterOptimizationEngine


def _scorecard(**overrides):
    data = {
        "mode": EngineMode.PAPER_ONLY,
        "strategy_name": "sprint_4_intraday_rules_v1",
        "symbol": "EURUSD",
        "timeframe": "5m",
        "score": 60.0,
        "status": "WATCHLIST",
        "rank": 1,
        "trades": 3,
        "wins": 2,
        "losses": 1,
        "win_rate_pct": 66.0,
        "profit_factor": 1.2,
        "net_pnl_usd": 2.0,
        "max_drawdown_usd": 0.0,
        "max_drawdown_pct": 0.0,
        "starting_balance_usd": 500.0,
        "ending_balance_usd": 502.0,
    }
    data.update(overrides)
    return StrategyScorecard(**data)


def _engine():
    return ParameterOptimizationEngine(ForexEngineConfig())


def _balanced():
    return _engine().default_parameter_sets()[1]


def test_default_parameter_sets_exist():
    names = [item.name for item in _engine().default_parameter_sets()]
    assert names == ["conservative", "balanced", "aggressive"]


def test_parameter_score_marks_tiny_sample_insufficient():
    score = _engine().score_parameter_set(_balanced(), _scorecard(trades=3))
    assert score.status == OptimizationStatus.INSUFFICIENT_DATA


def test_overfitting_risk_high_for_tiny_high_score():
    risk = _engine().detect_overfitting_risk(score=90, sample_size=3, profit_factor=2.0)
    assert risk == OverfittingRisk.HIGH


def test_negative_pnl_penalizes_score():
    engine = _engine()
    positive = engine.score_parameter_set(_balanced(), _scorecard(net_pnl_usd=5.0, trades=25))
    negative = engine.score_parameter_set(_balanced(), _scorecard(net_pnl_usd=-5.0, trades=25))
    assert negative.score < positive.score


def test_profit_factor_none_adds_caution():
    score = _engine().score_parameter_set(_balanced(), _scorecard(profit_factor=None))
    assert any("Profit factor is inconclusive" in component.reason for component in score.components)
    assert any("Profit factor is inconclusive" in item for item in score.recommendations)


def test_missing_regime_filter_penalized():
    engine = _engine()
    filtered = engine.score_parameter_set(_balanced(), _scorecard(trades=25))
    no_filter = ParameterSet(**{**_balanced().__dict__, "name": "no_regime", "regime_filter": False})
    unfiltered = engine.score_parameter_set(no_filter, _scorecard(trades=25))
    assert unfiltered.score < filtered.score


def test_missing_volatility_filter_penalized():
    engine = _engine()
    filtered = engine.score_parameter_set(_balanced(), _scorecard(trades=25))
    no_filter = ParameterSet(**{**_balanced().__dict__, "name": "no_volatility", "volatility_filter": False})
    unfiltered = engine.score_parameter_set(no_filter, _scorecard(trades=25))
    assert unfiltered.score < filtered.score


def test_aggressive_risk_penalized_for_500_account():
    engine = _engine()
    balanced = engine.score_parameter_set(_balanced(), _scorecard(trades=25))
    aggressive = engine.score_parameter_set(engine.default_parameter_sets()[2], _scorecard(trades=25))
    assert aggressive.score < balanced.score


def test_rank_scores_deterministic():
    engine = _engine()
    scores = [
        engine.score_parameter_set(engine.default_parameter_sets()[2], _scorecard(trades=25, net_pnl_usd=1.0)),
        engine.score_parameter_set(engine.default_parameter_sets()[1], _scorecard(trades=25, net_pnl_usd=2.0)),
    ]
    ranked = engine.rank_scores(scores)
    assert [score.parameter_set_name for score in ranked] == ["balanced", "aggressive"]


def test_compare_parameter_sets_returns_best():
    engine = _engine()
    result = engine.compare_parameter_sets(engine.default_parameter_sets(), [_scorecard(trades=3)])
    assert result.best_parameter_set is not None
    assert result.tested_count == 3


def test_recommendations_present():
    score = _engine().score_parameter_set(_balanced(), _scorecard(trades=3))
    assert score.recommendations


def test_parameter_optimization_demo_imports_without_network():
    import automation.forex_engine.run_parameter_optimization_demo as demo

    assert demo.main


def test_existing_demos_still_import():
    import automation.forex_engine.run_backtest_demo as backtest_demo
    import automation.forex_engine.run_broker_sandbox_demo as broker_sandbox_demo
    import automation.forex_engine.run_confidence_demo as confidence_demo
    import automation.forex_engine.run_market_data_demo as market_data_demo
    import automation.forex_engine.run_paper_demo as paper_demo
    import automation.forex_engine.run_paper_operator_demo as paper_operator_demo
    import automation.forex_engine.run_risk_management_demo as risk_management_demo
    import automation.forex_engine.run_signal_rules_demo as signal_rules_demo
    import automation.forex_engine.run_strategy_comparison_demo as strategy_comparison_demo
    import automation.forex_engine.run_walk_forward_demo as walk_forward_demo

    assert backtest_demo.main
    assert broker_sandbox_demo.main
    assert confidence_demo.main
    assert market_data_demo.main
    assert paper_demo.main
    assert paper_operator_demo.main
    assert risk_management_demo.main
    assert signal_rules_demo.main
    assert strategy_comparison_demo.main
    assert walk_forward_demo.main


def test_no_live_trading_demo_created():
    assert not Path("automation/forex_engine/run_live_trading_demo.py").exists()
