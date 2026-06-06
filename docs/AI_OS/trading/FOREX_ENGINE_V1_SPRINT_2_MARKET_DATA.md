# AI_OS Forex Engine v1 — Sprint 2 Market Data

## Objective

Add local candle data ingestion and validation for PAPER_ONLY forex research.

## Scope

Included:

- Candle model
- Local CSV candle loader
- Local fake fixture data
- Candle validation
- Sequence validation
- Multi-symbol fixture loading
- Market data demo command
- Tests

Excluded:

- Backtesting engine
- Strategy optimization
- Live broker connector
- Broker API ingestion
- TradingView webhook
- MT5 integration
- OANDA integration
- Scheduler
- Telegram
- UI
- Hardware features

## Current Defaults

- Mode: PAPER_ONLY
- Symbols: EURUSD, GBPUSD, USDJPY, XAUUSD
- Fixture timeframe: 5m
- Fixture source: local fake sample CSV files
- No network or broker data source

## Files Added

- `automation/forex_engine/market_data.py`
- `automation/forex_engine/run_market_data_demo.py`
- `automation/forex_engine/fixtures/README.md`
- `automation/forex_engine/fixtures/EURUSD_5m_sample.csv`
- `automation/forex_engine/fixtures/GBPUSD_5m_sample.csv`
- `automation/forex_engine/fixtures/USDJPY_5m_sample.csv`
- `automation/forex_engine/fixtures/XAUUSD_5m_sample.csv`
- `tests/forex_engine/test_market_data.py`

## CSV Format

```text
timestamp,symbol,timeframe,open,high,low,close,volume
```

## Candle Model

`Candle` fields:

- symbol
- timeframe
- timestamp
- open
- high
- low
- close
- volume
- source

## Validation Rules

- Symbol must be configured.
- Timeframe must be configured.
- Prices must be positive.
- High must be greater than or equal to open, low, and close.
- Low must be less than or equal to open, high, and close.
- Timestamp must not be empty.
- Volume must be zero or positive.
- Source must not be empty.
- Candle sequences must be non-empty, single-symbol, single-timeframe, unique, and sorted ascending.

## Fixture Data

Fixture data is fake sample data for local tests and demos only.

## Demo Command

```powershell
python -m automation.forex_engine.run_market_data_demo
```

## Test Command

```powershell
python -m pytest tests/forex_engine
```

## Safety Boundary

- Sprint 2 is `PAPER_ONLY`.
- No broker data ingestion exists.
- No API ingestion exists.
- No network ingestion exists.
- No live execution exists.
- No credentials or tokens are used.
- No scheduler authority exists.
- No Telegram sending exists.

## Known Limitations

- Fixture data is fake sample data.
- No broker data ingestion exists.
- No API ingestion exists.
- No live execution exists.
- No backtesting loop exists yet.
- Sprint 3 should add backtest runner.

## Next Sprint

Add a local backtest runner using only local fixture or operator-provided paper research data.
