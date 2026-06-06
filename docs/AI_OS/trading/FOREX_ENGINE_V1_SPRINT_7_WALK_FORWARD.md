# AI_OS Forex Engine v1 — Sprint 7 Walk-Forward Validation

## Objective

Sprint 7 creates deterministic walk-forward validation scaffolding and out-of-sample split logic for PAPER_ONLY forex research.

## Why This Sprint Matters

Sprint 1 proved paper trade accounting.
Sprint 2 proved local candle loading.
Sprint 3 proved local backtesting.
Sprint 4 added regime and signal candidates.
Sprint 5 added setup confidence grading.
Sprint 6 compared strategy outputs.
Sprint 7 separates in-sample and out-of-sample validation.

## Scope

Included:

- WalkForwardEngine
- WalkForwardSplit
- WalkForwardWindowResult
- WalkForwardResult
- Chronological train/test split
- Degradation logic
- Recommendations
- Walk-forward demo
- Tests
- Documentation

Excluded:

- Profitability claims
- Live trading
- Broker APIs
- External data download
- Real optimization
- ML
- Telegram
- Scheduler
- Hardware

## Current Defaults

- Starting account: 500 USD
- Paper risk: 0.5 percent
- Daily drawdown stop: 2 percent
- Max open paper trades: 2
- Symbols: EURUSD, GBPUSD, USDJPY, XAUUSD
- Fixture timeframe: 5m
- Mode: PAPER_ONLY

## Files Added

- `automation/forex_engine/walk_forward.py`
- `automation/forex_engine/run_walk_forward_demo.py`
- `tests/forex_engine/test_walk_forward.py`

## Walk-Forward Flow

1. Local candles
2. Validate sequence
3. Split train/test chronologically
4. Run train backtest
5. Run test backtest
6. Compare degradation
7. Assign status
8. Generate recommendations

## Train/Test Split Rules

- Train first.
- Test second.
- No overlap.
- Default train ratio 0.6.
- Invalid ratios are rejected.

## Validation Statuses

- PASSED
- DEGRADED
- FAILED
- INSUFFICIENT_DATA

## Degradation Logic

When train net PnL is positive, degradation is calculated from train net PnL versus test net PnL.

When train net PnL is non-positive, degradation is not meaningful and is handled safely without crashing.

## Recommendations

- Insufficient data: use larger historical datasets before trusting results.
- Degraded: review regime filters and confidence thresholds.
- Failed: reject or rework before further promotion.
- Passed: move only to broader paper research, not live trading.

## Demo Command

```powershell
python -m automation.forex_engine.run_walk_forward_demo
```

## Validation

```powershell
python -m pytest tests/forex_engine
python -m automation.forex_engine.run_walk_forward_demo
python -m automation.forex_engine.run_strategy_comparison_demo
python -m automation.forex_engine.run_confidence_demo
python -m automation.forex_engine.run_signal_rules_demo
python -m automation.forex_engine.run_backtest_demo
python -m automation.forex_engine.run_market_data_demo
python -m automation.forex_engine.run_paper_demo
```

## Safety Boundary

- Sprint 7 is PAPER_ONLY.
- No broker execution.
- No API ingestion.
- No network ingestion.
- No credentials.
- No live order path.
- No profitability claim.

## Known Limitations

- Fixture data is fake.
- Sample size is tiny.
- Walk-forward logic is scaffold only.
- No real historical data yet.
- No spread.
- No slippage.
- No commissions.
- No swaps.
- No pip-value correctness.
- No XAUUSD tick-value correctness.
- No live readiness.
- No ML.

## Success Criteria

- WalkForwardEngine exists.
- Train/test split exists.
- Chronological split is enforced.
- No-overlap rule exists.
- Degradation logic exists.
- Recommendations exist.
- Walk-forward demo runs.
- Strategy comparison demo still runs.
- Confidence demo still runs.
- Signal rules demo still runs.
- Backtest demo still runs.
- Market data demo still runs.
- Paper demo still runs.
- All forex_engine tests pass.
- No live execution path exists.
- No network ingestion exists.

## Next Sprint

Sprint 8 should add paper operator mode with daily reports, alert-state modeling, pause rules, and supervisor summaries, still PAPER_ONLY.
