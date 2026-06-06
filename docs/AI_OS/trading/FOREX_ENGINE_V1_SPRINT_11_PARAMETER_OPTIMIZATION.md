# AI_OS Forex Engine v1 — Sprint 11 Parameter Optimization + Overfitting Guards

## Objective

Sprint 11 creates deterministic parameter optimization scaffolding for local PAPER_ONLY research.

## Why This Sprint Matters

Sprint 1 proved paper trade accounting.
Sprint 2 proved local candle loading.
Sprint 3 proved local backtesting.
Sprint 4 added regime and signal candidates.
Sprint 5 added setup confidence grading.
Sprint 6 added strategy comparison.
Sprint 7 added walk-forward validation.
Sprint 8 added paper operator reporting.
Sprint 9 added broker sandbox modeling.
Sprint 10 added risk management and kill-switch modeling.
Sprint 11 compares parameter sets while guarding against overfitting.

## Scope

Included:

- ParameterOptimizationEngine
- ParameterSet
- ParameterOptimizationScore
- ParameterOptimizationResult
- OptimizationStatus
- OverfittingRisk
- Parameter optimization demo
- Tests
- Documentation

Excluded:

- Live broker execution
- Broker APIs
- External data download
- Credentials
- ML training
- Telegram sending
- Email sending
- Push notifications
- Scheduler
- Hardware

## Current Defaults

- Starting account: 500 USD
- Paper risk: 0.5 percent
- Daily drawdown stop: 2 percent
- Max open paper trades: 2
- Symbols: EURUSD, GBPUSD, USDJPY, XAUUSD
- Mode: PAPER_ONLY
- Optimization mode: OPTIMIZATION_MODEL_ONLY

## Files Added

- `automation/forex_engine/parameter_optimization.py`
- `automation/forex_engine/run_parameter_optimization_demo.py`
- `tests/forex_engine/test_parameter_optimization.py`
- `docs/AI_OS/trading/FOREX_ENGINE_V1_SPRINT_11_PARAMETER_OPTIMIZATION.md`

## Parameter Optimization Flow

1. Define parameter sets
2. Load local research summaries
3. Score each parameter set
4. Detect overfitting risk
5. Rank candidates
6. Return operator-readable result

## Parameter Sets

- conservative
- balanced
- aggressive

Each set defines confidence threshold, reward/risk minimum, filters, max open trades, and paper risk percent.

## Scoring Rules

- Tiny samples are penalized.
- Positive net PnL adds score.
- Negative net PnL subtracts score.
- Win rate, profit factor, drawdown, filters, and risk settings affect the score.
- Aggressive risk is penalized for the 500 USD starter profile.

## Overfitting Guards

- Tiny sample results are high risk.
- No-loss or no-profit-factor samples are caution cases.
- High score on tiny samples is high overfitting risk.
- Walk-forward support is required before low risk can be trusted.

## Recommendations

Recommendations are research notes only. They point toward larger datasets, walk-forward evidence, and more conservative filters.

## Demo Command

```powershell
python -m automation.forex_engine.run_parameter_optimization_demo
```

## Validation

```powershell
python -m pytest tests/forex_engine
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

- Sprint 11 is local OPTIMIZATION_MODEL_ONLY and PAPER_ONLY.
- No broker execution.
- No API calls.
- No network calls.
- No credentials.
- No live order path.
- No alert sending.
- No scheduling.
- No profitability claim.
- No optimized-edge claim.
- No live readiness claim.

## Known Limitations

- Model only.
- Fake/tiny fixture data.
- No real historical optimization.
- No walk-forward-confirmed edge.
- No ML.
- No real broker.
- No live readiness.

## Success Criteria

- ParameterOptimizationEngine exists.
- ParameterSet exists.
- ParameterOptimizationScore exists.
- ParameterOptimizationResult exists.
- OverfittingRisk exists.
- OptimizationStatus exists.
- Conservative, balanced, and aggressive parameter sets exist.
- Tiny sample is marked insufficient.
- Overfitting risk guard works.
- Aggressive risk is penalized.
- Missing filters are penalized.
- Ranking is deterministic.
- Parameter optimization demo runs.
- Existing demos still run.
- All forex_engine tests pass.
- No broker/API/network ingestion exists.
- No live execution exists.
- No run_live_trading_demo.py exists.

## Next Sprint

Sprint 12 should add portfolio optimization demo and capital allocation scaffolding, still without live execution, broker credentials, or real API calls.
