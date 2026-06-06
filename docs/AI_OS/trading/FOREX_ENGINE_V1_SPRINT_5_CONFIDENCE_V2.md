# AI_OS Forex Engine v1 — Sprint 5 Confidence v2 + Setup Quality

## Objective

Sprint 5 creates deterministic confidence scoring v2 and setup quality grading for PAPER_ONLY forex research.

## Why This Sprint Matters

Sprint 1 proved paper trade accounting.
Sprint 2 proved local candle loading.
Sprint 3 proved local backtesting.
Sprint 4 added regime and signal candidates.
Sprint 5 explains setup quality and selectivity.

## Scope

Included:

- ConfidenceEngineV2
- SetupQualityAssessment
- Confidence components
- Setup grades
- Confidence bands
- Recommendations
- Confidence demo
- Tests
- Documentation

Excluded:

- Profitability claims
- Live trading
- Broker APIs
- External data download
- Optimization
- Walk-forward testing
- Advanced ML
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

- `automation/forex_engine/confidence_v2.py`
- `automation/forex_engine/run_confidence_demo.py`
- `tests/forex_engine/test_confidence_v2.py`

## Confidence v2 Flow

1. Signal candidate
2. ForexSignal conversion
3. Regime metadata
4. Risk/reward check
5. Component scoring
6. Grade assignment
7. Band assignment
8. Allowed/reduced-risk/blocked decision
9. Recommendations

## Scoring Components

- Symbol/timeframe
- Direction
- Risk/reward
- Regime alignment
- Volatility alignment
- Metadata quality
- Blocked reason

## Setup Grades

- A
- B
- C
- D
- F

## Confidence Bands

- HIGH_QUALITY
- TRADE_CANDIDATE
- WATCHLIST
- BLOCKED

## Blocked Conditions

- Invalid direction
- Invalid risk/reward
- Regime mismatch if severe
- Candidate blocked reason
- Score below threshold

## Recommendations

Confidence v2 emits deterministic PAPER_ONLY research recommendations such as improving reward-to-risk, waiting for regime alignment, waiting for volatility normalization, or keeping a setup on watchlist.

## Demo Command

```powershell
python -m automation.forex_engine.run_confidence_demo
```

## Validation

```powershell
python -m pytest tests/forex_engine
python -m automation.forex_engine.run_confidence_demo
python -m automation.forex_engine.run_signal_rules_demo
python -m automation.forex_engine.run_backtest_demo
python -m automation.forex_engine.run_market_data_demo
python -m automation.forex_engine.run_paper_demo
```

## Safety Boundary

- Sprint 5 is PAPER_ONLY.
- No broker execution.
- No API ingestion.
- No network ingestion.
- No credentials.
- No live order path.
- No profitability claim.

## Known Limitations

- Deterministic scoring only.
- No ML.
- No trained model.
- No optimization.
- No walk-forward validation.
- No real historical data quality checks beyond fixtures.
- No spread.
- No slippage.
- No commissions.
- No swaps.
- No pip-value correctness.
- No XAUUSD tick-value correctness.
- No live readiness.

## Success Criteria

- Confidence v2 exists.
- Setup grading exists.
- Confidence bands exist.
- Components explain score.
- Recommendations exist.
- Demo runs.
- Signal rules demo still runs.
- Backtest demo still runs.
- Market data demo still runs.
- Paper demo still runs.
- All forex_engine tests pass.
- No live execution path exists.
- No network ingestion exists.

## Next Sprint

Sprint 6 should add strategy performance comparison and optimization scaffolding using backtest results and confidence v2 outputs, still PAPER_ONLY.
