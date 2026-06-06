# AI_OS Forex Engine v1 — Sprint 3 Backtest Runner

## Objective

Sprint 3 creates a local PAPER_ONLY backtest runner that connects local candle fixtures to the paper execution engine.

## Why This Sprint Matters

Sprint 1 proved trade accounting.
Sprint 2 proved local candle loading.
Sprint 3 connects candles to simulated paper trades.

## Scope

Included:

- Backtest engine
- Backtest models
- Demo strategy
- Stop/target evaluation
- End-of-backtest close handling
- Backtest demo
- Tests
- Documentation

Excluded:

- Live trading
- Broker APIs
- External data download
- Optimization
- Advanced regime detection
- ML training
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

- `automation/forex_engine/backtest.py`
- `automation/forex_engine/run_backtest_demo.py`
- `tests/forex_engine/test_backtest.py`

## Backtest Flow

1. Local candles
2. Validate sequence
3. Generate demo signal
4. Score confidence
5. Apply risk
6. Open paper trade
7. Evaluate stop/target on later candles
8. Close trade
9. Journal event
10. Summarize analytics

## Demo Strategy

- Close up = BUY
- Close down = SELL
- Flat = no signal

This is not a profitable strategy claim. It only proves plumbing.

## Trade Close Rules

BUY:

- Candle low at or below stop-loss closes at stop-loss.
- Candle high at or above take-profit closes at take-profit.

SELL:

- Candle high at or above stop-loss closes at stop-loss.
- Candle low at or below take-profit closes at take-profit.

## Conservative Same-Candle Rule

If stop and target are both touched in one candle, assume stop-loss first.

## Data Source

- Local fixture CSVs only.
- Fake sample data only.
- No broker/API/network data.

## Validation

```powershell
python -m pytest tests/forex_engine
python -m automation.forex_engine.run_backtest_demo
python -m automation.forex_engine.run_market_data_demo
python -m automation.forex_engine.run_paper_demo
```

## Safety Boundary

- Sprint 3 is PAPER_ONLY.
- No broker execution.
- No API ingestion.
- No network ingestion.
- No credentials.
- No live order path.

## Known Limitations

- Fixture data is fake.
- Backtest uses simplified candle assumptions.
- No spread.
- No slippage.
- No commissions.
- No swaps.
- No pip-value correctness.
- No XAUUSD tick-value correctness.
- No intrabar sequencing except conservative stop-first rule.
- Demo strategy is not an edge.
- No optimization.
- No live readiness.
- No broker integration.

## Success Criteria

- Backtest runner exists.
- Backtest demo runs.
- Backtest tests pass.
- Existing Sprint 1 and Sprint 2 demos still run.
- All forex_engine tests pass.
- No live execution path exists.
- No network ingestion exists.

## Next Sprint

Sprint 4 should add regime and signal rules for intraday research, still PAPER_ONLY.
