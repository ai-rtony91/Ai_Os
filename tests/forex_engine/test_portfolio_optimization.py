from pathlib import Path

import pytest

from automation.forex_engine.config import ForexEngineConfig
from automation.forex_engine.models import (
    AllocationMethod,
    ConcentrationStatus,
    PortfolioAllocation,
    PortfolioOptimizationStatus,
)
from automation.forex_engine.portfolio_optimization import PortfolioOptimizationEngine


def _engine():
    return PortfolioOptimizationEngine(ForexEngineConfig())


def test_equal_weight_allocation_four_symbols():
    result = _engine().build_equal_weight_allocation()
    assert {item.symbol: item.allocation_usd for item in result.allocations} == {
        "EURUSD": 125.0,
        "GBPUSD": 125.0,
        "USDJPY": 125.0,
        "XAUUSD": 125.0,
    }


def test_equal_weight_allocation_percentages():
    result = _engine().build_equal_weight_allocation()
    assert all(item.allocation_pct == 25.0 for item in result.allocations)


def test_xauusd_cap_warning_when_above_cap():
    allocations = [
        PortfolioAllocation("EURUSD", 100, 20, 175, None, "OK"),
        PortfolioAllocation("GBPUSD", 100, 20, 175, None, "OK"),
        PortfolioAllocation("USDJPY", 100, 20, 175, None, "OK"),
        PortfolioAllocation("XAUUSD", 200, 40, 125, None, "CAUTION"),
    ]
    summary = _engine().evaluate_concentration(allocations)
    assert summary.concentration_status == ConcentrationStatus.TOO_CONCENTRATED
    assert any("XAUUSD" in warning for warning in summary.warnings)


def test_max_symbol_cap_detects_concentration():
    allocations = [
        PortfolioAllocation("EURUSD", 200, 40, 175, None, "CAUTION"),
        PortfolioAllocation("GBPUSD", 100, 20, 175, None, "OK"),
        PortfolioAllocation("USDJPY", 100, 20, 175, None, "OK"),
        PortfolioAllocation("XAUUSD", 100, 20, 125, None, "OK"),
    ]
    assert _engine().evaluate_concentration(allocations).concentration_status == ConcentrationStatus.TOO_CONCENTRATED


def test_risk_capped_allocation_respects_caps():
    result = _engine().build_risk_capped_allocation({"EURUSD": 500, "GBPUSD": 50, "USDJPY": 50, "XAUUSD": 500})
    assert all(item.allocation_pct <= 35 for item in result.allocations if item.symbol != "XAUUSD")
    assert next(item for item in result.allocations if item.symbol == "XAUUSD").allocation_pct <= 25


def test_confidence_weighted_placeholder_is_deterministic():
    scores = {"EURUSD": 100, "GBPUSD": 85, "USDJPY": 70, "XAUUSD": 60}
    first = _engine().build_confidence_weighted_placeholder(scores)
    second = _engine().build_confidence_weighted_placeholder(scores)
    assert [(item.symbol, item.allocation_usd) for item in first.allocations] == [
        (item.symbol, item.allocation_usd) for item in second.allocations
    ]


def test_confidence_weighted_placeholder_falls_back_without_scores():
    result = _engine().build_confidence_weighted_placeholder({})
    assert result.allocation_method == AllocationMethod.CONFIDENCE_WEIGHTED_PLACEHOLDER
    assert all(item.allocation_usd == 125.0 for item in result.allocations)
    assert any("fell back" in warning for warning in result.warnings)


def test_portfolio_result_marks_insufficient_data():
    assert _engine().build_equal_weight_allocation().optimization_status == PortfolioOptimizationStatus.INSUFFICIENT_DATA


def test_portfolio_recommendations_present():
    assert _engine().build_equal_weight_allocation().recommendations


def test_portfolio_risk_summary_fields():
    summary = _engine().evaluate_concentration(_engine().build_equal_weight_allocation().allocations)
    assert summary.max_symbol_allocation_pct == 25.0
    assert summary.max_symbol_allocation_usd == 125.0
    assert summary.concentration_status == ConcentrationStatus.OK


def test_unallocated_capital_non_negative():
    result = _engine().build_risk_capped_allocation({"EURUSD": 500, "GBPUSD": 50, "USDJPY": 50, "XAUUSD": 500})
    assert result.unallocated_capital_usd >= 0


def test_invalid_starting_capital_rejected():
    with pytest.raises(ValueError):
        _engine().build_equal_weight_allocation(0)


def test_portfolio_optimization_demo_imports_without_network():
    import automation.forex_engine.run_portfolio_optimization_demo as demo

    assert demo.main


def test_existing_demos_still_import():
    import automation.forex_engine.run_backtest_demo as backtest_demo
    import automation.forex_engine.run_broker_sandbox_demo as broker_sandbox_demo
    import automation.forex_engine.run_confidence_demo as confidence_demo
    import automation.forex_engine.run_market_data_demo as market_data_demo
    import automation.forex_engine.run_paper_demo as paper_demo
    import automation.forex_engine.run_paper_operator_demo as paper_operator_demo
    import automation.forex_engine.run_parameter_optimization_demo as parameter_demo
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
    assert parameter_demo.main
    assert risk_management_demo.main
    assert signal_rules_demo.main
    assert strategy_comparison_demo.main
    assert walk_forward_demo.main


def test_no_live_trading_demo_created():
    assert not Path("automation/forex_engine/run_live_trading_demo.py").exists()
