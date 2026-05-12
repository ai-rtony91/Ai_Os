# AI_OS Trading Lab Core Kit

Local paper-only research kit for importing market data, receiving mock signal payloads, storing records in SQLite, and running paper backtests.

## Safety Boundary

- Paper trading only.
- No OANDA live API integration.
- No broker keys.
- No live order placement.
- No real webhook execution.
- No AI_OS dashboard UI changes.

Any live broker call must use `trading_lab.execution.live_broker_stub`, which raises:

```text
LIVE_BROKER_DISABLED: paper mode only
```

## Database

Default SQLite path:

```text
apps/trading_lab/data/trading_lab.db
```

Override with:

```text
TRADING_LAB_DB_URL=sqlite:///path/to/trading_lab.db
```

## CLI

Run from `apps/trading_lab`:

```powershell
python -m trading_lab.cli init-db
python -m trading_lab.cli import-file .\data\raw\candles.csv
python -m trading_lab.cli backtest --symbol EUR_USD --timeframe M5
python -m trading_lab.cli walk-forward --symbol EUR_USD --timeframe M5
python -m trading_lab.cli serve-webhooks
python -m trading_lab.cli report
```

## Data Flow

CSV/XLSX candles -> SQLite candles -> paper signal intake -> risk gate -> paper broker -> backtest results -> reports.

Live execution remains blocked.
