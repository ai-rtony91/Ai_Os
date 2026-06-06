# AI_OS Forex Engine v1 — Sprint 13 Historical Data Readiness

## Objective

Sprint 13 creates local PAPER_ONLY historical data readiness scaffolding.

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
Sprint 12 added portfolio optimization.
Sprint 13 prepares larger local historical dataset validation.

## Scope

Included:

- HistoricalDataReadinessEngine
- DatasetManifest
- DatasetQualityScore
- HistoricalDatasetSummary
- DatasetIssue
- Schema validation
- Duplicate detection
- Timestamp ordering checks
- OHLC checks
- Synthetic local dataset demo
- Tests
- Documentation

Excluded:

- Live trading
- Broker APIs
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
- Symbols: EURUSD, GBPUSD, USDJPY, XAUUSD
- Mode: PAPER_ONLY
- Readiness mode: HISTORICAL_DATA_READINESS_ONLY

## Files Added

- `automation/forex_engine/historical_data_readiness.py`
- `automation/forex_engine/run_historical_data_readiness_demo.py`
- `tests/forex_engine/test_historical_data_readiness.py`
- `docs/AI_OS/trading/FOREX_ENGINE_V1_SPRINT_13_HISTORICAL_DATA_READINESS.md`

## Historical Data Readiness Flow

1. Receive a local CSV path.
2. Reject URL-style paths.
3. Read CSV rows locally.
4. Validate required schema.
5. Validate symbols, timeframes, OHLC, volume, and timestamps.
6. Detect duplicate symbol/timeframe/timestamp rows.
7. Detect unsorted timestamps within each symbol/timeframe.
8. Build a dataset manifest.
9. Score dataset quality.
10. Return an operator-readable readiness summary.

## Required CSV Schema

```text
timestamp,symbol,timeframe,open,high,low,close,volume
```

## Dataset Manifest

The manifest records mode, dataset name, source type, local path, row count, symbols, timeframes, first and last timestamp, schema fields, creation time, and metadata.

## Quality Scoring

The score starts at 100 and subtracts for missing required fields, invalid rows, duplicate timestamps, unsorted timestamps, too few rows, invalid symbols, and invalid timeframes. The score is clamped between 0 and 100.

## Readiness Statuses

- READY_FOR_LOCAL_IMPORT
- INSUFFICIENT_DATA
- INVALID_DATASET
- NEEDS_CLEANING

## Synthetic Demo Dataset

The demo generates deterministic local synthetic CSV data under `automation/forex_engine/runtime/historical_data_demo/`. Runtime output is local generated evidence only and is not committed.

## Validation

```powershell
python -m pytest tests/forex_engine
python -m automation.forex_engine.run_historical_data_readiness_demo
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

Sprint 13 is local HISTORICAL_DATA_READINESS_ONLY.
No broker execution.
No API calls.
No network calls.
No data downloads.
No credentials.
No live order path.
No alert sending.
No scheduling.
No profitability claim.
No live readiness claim.

## Known Limitations

- Model only.
- Synthetic demo data only.
- No external historical provider integration.
- No real broker.
- No broker API.
- No credentials.
- No network.
- No real market-data quality certification.
- No live readiness.

## Success Criteria

- HistoricalDataReadinessEngine exists.
- DatasetManifest exists.
- DatasetQualityScore exists.
- HistoricalDatasetSummary exists.
- DatasetIssue exists.
- Required schema validation works.
- Invalid rows are detected.
- Duplicate timestamps are detected.
- Unsorted timestamps are detected.
- Tiny datasets become INSUFFICIENT_DATA.
- Valid synthetic dataset can become READY_FOR_LOCAL_IMPORT.
- Readiness demo runs.
- Portfolio optimization demo still runs.
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

Sprint 14 should add local large-dataset backtest adapter support using operator-provided CSV files only, still without network download, broker credentials, or live execution.
