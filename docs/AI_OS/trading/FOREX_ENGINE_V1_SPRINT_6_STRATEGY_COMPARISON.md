# AI_OS Forex Engine v1 — Sprint 6 Strategy Comparison + Optimization Scaffold

## Objective

Sprint 6 creates deterministic strategy performance comparison and optimization scaffolding for PAPER_ONLY forex research.

## Why This Sprint Matters

Sprint 1 proved paper trade accounting.
Sprint 2 proved local candle loading.
Sprint 3 proved local backtesting.
Sprint 4 added regime and signal candidates.
Sprint 5 added setup confidence grading.
Sprint 6 compares performance outputs and identifies what needs more testing.

## Scope

Included:

- StrategyComparisonEngine
- StrategyScorecard
- StrategyComparisonResult
- OptimizationCandidate
- Ranking rules
- Score components
- Strategy comparison demo
- Tests
- Documentation

Excluded:

- Profitability claims
- Live trading
- Broker APIs
- External data download
- Real optimization
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

- `automation/forex_engine/strategy_comparison.py`
- `automation/forex_engine/run_strategy_comparison_demo.py`
- `tests/forex_engine/test_strategy_comparison.py`

## Strategy Comparison Flow

1. Backtest result
2. Extract performance metrics
3. Score components
4. Assign strategy status
5. Build optimization candidates
6. Rank scorecards
7. Return comparison result

## Scorecard Components

- Sample size
- Net PnL
- Win rate
- Profit factor
- Drawdown
- Balance growth
- Consistency

## Strategy Statuses

- RESEARCH_CANDIDATE
- WATCHLIST
- REJECTED
- INSUFFICIENT_DATA

## Ranking Rules

Rank by status priority, score descending, net PnL descending, win rate descending, then stable strategy and symbol labels.

## Optimization Candidates

- sample_size
- entry_filter
- reward_risk_threshold
- drawdown_control
- loss_sample
- walk_forward_candidate

## Demo Command

```powershell
python -m automation.forex_engine.run_strategy_comparison_demo
```

## Validation

```powershell
python -m pytest tests/forex_engine
python -m automation.forex_engine.run_strategy_comparison_demo
python -m automation.forex_engine.run_confidence_demo
python -m automation.forex_engine.run_signal_rules_demo
python -m automation.forex_engine.run_backtest_demo
python -m automation.forex_engine.run_market_data_demo
python -m automation.forex_engine.run_paper_demo
```

## Safety Boundary

- Sprint 6 is PAPER_ONLY.
- No broker execution.
- No API ingestion.
- No network ingestion.
- No credentials.
- No live order path.
- No profitability claim.

## Known Limitations

- Fixture data is fake.
- Sample size is tiny.
- Scorecard is deterministic scaffold only.
- No real historical data yet.
- No walk-forward validation yet.
- No spread.
- No slippage.
- No commissions.
- No swaps.
- No pip-value correctness.
- No XAUUSD tick-value correctness.
- No live readiness.

## Success Criteria

- Strategy comparison module exists.
- Scorecards exist.
- Optimization candidates exist.
- Ranking works.
- Comparison demo runs.
- Confidence demo still runs.
- Signal rules demo still runs.
- Backtest demo still runs.
- Market data demo still runs.
- Paper demo still runs.
- All forex_engine tests pass.
- No live execution path exists.
- No network ingestion exists.

## Next Sprint

Sprint 7 should add walk-forward validation scaffolding and out-of-sample split logic, still PAPER_ONLY.
