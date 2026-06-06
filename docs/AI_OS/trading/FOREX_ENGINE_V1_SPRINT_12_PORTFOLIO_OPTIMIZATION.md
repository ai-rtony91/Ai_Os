# AI_OS Forex Engine v1 — Sprint 12 Portfolio Optimization + Capital Allocation

## Objective

Sprint 12 creates local PAPER_ONLY portfolio optimization and capital allocation scaffolding.

## Why This Sprint Matters

Sprint 1 proved paper trade accounting.
Sprint 2 proved local candle loading.
Sprint 3 proved local backtesting.
Sprint 4 added regime and signal rules.
Sprint 5 added confidence v2.
Sprint 6 added strategy comparison.
Sprint 7 added walk-forward validation.
Sprint 8 added paper operator status.
Sprint 9 added broker sandbox modeling.
Sprint 10 added risk management.
Sprint 11 added parameter optimization.
Sprint 12 models capital allocation across symbols.

## Scope

Included:

- PortfolioOptimizationEngine
- PortfolioAllocation
- PortfolioOptimizationResult
- PortfolioRiskSummary
- Equal-weight allocation
- Risk-capped allocation
- Confidence-weighted placeholder
- Portfolio optimization demo
- Tests
- Documentation

Excluded:

- Live trading
- Broker APIs
- Real capital allocation
- External data download
- Credentials
- Telegram sending
- Email sending
- Push notifications
- Scheduler
- Hardware
- run_live_trading_demo

## Current Defaults

- Starting account: 500 USD
- Paper risk: 0.5 percent
- Daily drawdown stop: 2 percent
- Weekly drawdown threshold: 5 percent
- Max open paper trades: 2
- Symbols: EURUSD, GBPUSD, USDJPY, XAUUSD
- Mode: PAPER_ONLY
- Portfolio mode: PORTFOLIO_MODEL_ONLY

## Files Added

- `automation/forex_engine/portfolio_optimization.py`
- `automation/forex_engine/run_portfolio_optimization_demo.py`
- `tests/forex_engine/test_portfolio_optimization.py`
- `docs/AI_OS/trading/FOREX_ENGINE_V1_SPRINT_12_PORTFOLIO_OPTIMIZATION.md`

## Portfolio Optimization Flow

1. Load config
2. Create allocation model
3. Build equal-weight allocation
4. Build risk-capped allocation
5. Build confidence-weighted placeholder
6. Evaluate concentration
7. Build recommendations
8. Print operator summary

## Allocation Methods

- EQUAL_WEIGHT
- RISK_CAPPED
- CONFIDENCE_WEIGHTED_PLACEHOLDER

## Concentration Rules

- Max symbol cap: 35%
- XAUUSD cap: 25%
- Minimum symbols: 2

## XAUUSD Cap

XAUUSD is capped at 25 percent in Sprint 12 because tick value and volatility modeling remain future work.

## Recommendations

- Use larger historical datasets before trusting allocation.
- Keep XAUUSD capped until tick-value and volatility modeling improve.
- Reduce concentration before portfolio promotion.
- Leave unallocated capital in reserve when caps block allocation.
- Treat equal-weight allocation as a conservative modeling baseline.

## Demo Command

```powershell
python -m automation.forex_engine.run_portfolio_optimization_demo
```

## Validation

```powershell
python -m pytest tests/forex_engine
python -m automation.forex_engine.run_portfolio_optimization_demo
python -m automation.forex_engine.run_parameter_optimization_demo
python -m automation.forex_engine.run_risk_management_demo
python -m automation.forex_engine.run_broker_sandbox_demo
python -m automation.forex_engine.run_paper_operator_demo
python -m automation.forex_engine.run_walk_forward_demo
python -m automation.forex_engine.run_strategy_comparison_demo
python -m automation.forex_engine.run_confidence_demo
python -m automation.forex_engine.run_signal_rules_demo
python -m automation.forex_engine.run_backtest_demo
python -m automation.forex_engine.run_market_data_demo
python -m automation.forex_engine.run_paper_demo
```

## Safety Boundary

- Sprint 12 is local PORTFOLIO_MODEL_ONLY.
- No broker execution.
- No API calls.
- No network calls.
- No credentials.
- No live order path.
- No alert sending.
- No scheduling.
- No profitability claim.
- No optimized portfolio claim.
- No live readiness claim.

## Known Limitations

- Model only.
- No real broker.
- No broker API.
- No credentials.
- No network.
- No real capital allocation.
- No live portfolio management.
- No Sharpe ratio based on real returns yet.
- No correlation model yet.
- No covariance model yet.
- No slippage.
- No spread.
- No commissions.
- No swaps.
- No pip-value correctness.
- No XAUUSD tick-value correctness.
- No live readiness.

## Success Criteria

- PortfolioOptimizationEngine exists.
- PortfolioAllocation exists.
- PortfolioOptimizationResult exists.
- PortfolioRiskSummary exists.
- Equal-weight allocation works.
- Risk-capped allocation works.
- Confidence-weighted placeholder works.
- XAUUSD cap works.
- Max symbol cap works.
- Insufficient data status works.
- Portfolio optimization demo runs.
- Parameter optimization demo still runs.
- Risk management demo still runs.
- Broker sandbox demo still runs.
- Paper operator demo still runs.
- Walk-forward demo still runs.
- Strategy comparison demo still runs.
- Confidence demo still runs.
- Signal rules demo still runs.
- Backtest demo still runs.
- Market data demo still runs.
- Paper demo still runs.
- All forex_engine tests pass.
- No live execution path exists.
- No network ingestion exists.
- No run_live_trading_demo.py exists.

## Next Sprint

Sprint 13 should add real historical-data import readiness and larger local dataset validation, still without network download, broker credentials, or live execution.
