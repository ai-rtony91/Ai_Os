"""Run the AI_OS Forex Engine v1 Sprint 12 portfolio optimization demo."""

import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from automation.forex_engine.config import ForexEngineConfig, validate_config
from automation.forex_engine.portfolio_optimization import PORTFOLIO_MODE, PortfolioOptimizationEngine


def build_demo_results(config=None):
    config = config or ForexEngineConfig()
    validate_config(config)
    engine = PortfolioOptimizationEngine(config)
    symbol_scores = {"EURUSD": 100, "GBPUSD": 85, "USDJPY": 70, "XAUUSD": 60}
    equal = engine.build_equal_weight_allocation()
    weighted = engine.build_confidence_weighted_placeholder(symbol_scores)
    capped = engine.build_risk_capped_allocation(symbol_scores)
    return equal, weighted, capped


def main() -> int:
    config = ForexEngineConfig()
    equal, weighted, capped = build_demo_results(config)

    print("AI_OS Forex Engine v1 Sprint 12 Portfolio Optimization Demo")
    print(f"Mode: {config.mode}")
    print(f"Portfolio mode: {PORTFOLIO_MODE}")
    print(f"Starting capital: {config.starting_balance_usd:.2f} USD")
    print(f"Symbols: {', '.join(config.symbols)}")
    print("Allocation methods tested: EQUAL_WEIGHT, RISK_CAPPED, CONFIDENCE_WEIGHTED_PLACEHOLDER")
    print("Equal-weight allocation summary:")
    for allocation in equal.allocations:
        print(f"{allocation.symbol} allocation: {allocation.allocation_usd:.2f} USD")
    print(
        f"Risk-capped allocation summary: allocated={capped.allocated_capital_usd:.2f}, "
        f"unallocated={capped.unallocated_capital_usd:.2f}"
    )
    print(
        f"Confidence-weighted placeholder summary: allocated={weighted.allocated_capital_usd:.2f}, "
        f"unallocated={weighted.unallocated_capital_usd:.2f}"
    )
    print(f"Concentration status: {equal.concentration_status}")
    print(f"Optimization status: {equal.optimization_status}")
    print(f"Risk posture: {equal.risk_posture}")
    print(f"Recommendations: {'; '.join(equal.recommendations)}")
    print("Safety note: Local portfolio optimization scaffold only; no broker/API/network/live execution path used.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
