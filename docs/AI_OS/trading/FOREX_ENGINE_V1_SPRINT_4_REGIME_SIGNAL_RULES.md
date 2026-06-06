# AI_OS Forex Engine v1 — Sprint 4 Regime + Signal Rules

## Objective

Sprint 4 creates the first local PAPER_ONLY regime and signal rule layer for intraday research.

## Why This Sprint Matters

Sprint 1 proved paper trade accounting.
Sprint 2 proved local candle loading.
Sprint 3 proved local backtesting.
Sprint 4 begins structured trading-intelligence research.

## Scope

Included:

- Regime classification
- Volatility classification
- Signal candidates
- Trend-follow rule v1
- Signal conversion to ForexSignal
- Signal rules demo
- Tests
- Documentation

Excluded:

- Profitability claims
- Live trading
- Broker APIs
- External data download
- Optimization
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

- `automation/forex_engine/signal_rules.py`
- `automation/forex_engine/run_signal_rules_demo.py`
- `tests/forex_engine/test_signal_rules.py`

## Regime Classification

- TRENDING_UP
- TRENDING_DOWN
- RANGING
- UNKNOWN

## Volatility Classification

- LOW_VOLATILITY
- NORMAL_VOLATILITY
- HIGH_VOLATILITY
- UNKNOWN

## Signal Rule Flow

1. Local candles
2. Validate sequence
3. Assess regime
4. Generate candidate
5. Apply quality blocks
6. Convert to ForexSignal
7. Optional backtest path
8. PAPER_ONLY result

## Trend-Follow Rule v1

- TRENDING_UP creates BUY candidate.
- TRENDING_DOWN creates SELL candidate.
- RANGING blocks trend-follow candidate.
- Low/high volatility blocks Sprint 4 trend-follow candidates.

## Blocked Conditions

- Ranging regime
- Low volatility
- High volatility
- Invalid stop distance
- Invalid take profit
- Insufficient candles
- Unknown regime

## Backtest Compatibility

Sprint 4 signal rules are directly selectable in `BacktestEngine` by using `BacktestConfig.strategy_name = "sprint_4_intraday_rules_v1"`.

The Sprint 3 demo strategy remains available as the default compatibility path.

## Demo Command

```powershell
python -m automation.forex_engine.run_signal_rules_demo
```

## Validation

```powershell
python -m pytest tests/forex_engine
python -m automation.forex_engine.run_signal_rules_demo
python -m automation.forex_engine.run_backtest_demo
python -m automation.forex_engine.run_market_data_demo
python -m automation.forex_engine.run_paper_demo
```

## Safety Boundary

- Sprint 4 is PAPER_ONLY.
- No broker execution.
- No API ingestion.
- No network ingestion.
- No credentials.
- No live order path.

## Known Limitations

- Fixture data is fake.
- Regime logic is simple.
- Volatility thresholds are simple.
- No spread.
- No slippage.
- No commissions.
- No swaps.
- No pip-value correctness.
- No XAUUSD tick-value correctness.
- No optimized thresholds.
- No ML.
- No profitability claim.
- No live readiness.

## Success Criteria

- Signal rules module exists.
- Regime classification works.
- Signal candidates are generated.
- Ranging conditions can be blocked.
- Signals can convert to ForexSignal.
- Signal rules demo runs.
- Existing backtest demo still runs.
- Existing market data demo still runs.
- Existing paper demo still runs.
- All forex_engine tests pass.
- No live execution path exists.
- No network ingestion exists.

## Next Sprint

Sprint 5 should improve confidence scoring and setup quality grading using Sprint 4 regime/signal metadata, still PAPER_ONLY.
