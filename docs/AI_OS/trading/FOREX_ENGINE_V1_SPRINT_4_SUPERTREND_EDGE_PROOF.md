# Forex Engine v1 Sprint 4 Supertrend Edge Proof

## Scope

Sprint 4 adds a PAPER_ONLY Supertrend edge-research harness. It is local evidence tooling only. It does not claim an earning system, it does not approve live use, and it does not connect to any broker, API, webhook, credential, or network market feed.

## What Was Added

- True range, ATR, Supertrend band, and Supertrend direction calculations.
- `supertrend_pullback_v1` paper-only strategy candidate.
- Conservative cost assumptions for spread, slippage, and commission.
- Edge metrics for expectancy R, profit factor, drawdown, losing streak, and no-trade reasons.
- Local CSV import support for manually exported candles.
- Sequential walk-forward evidence.
- Daily edge report preview.
- Edge gate policy that can classify only research states.

## Manual CSV Intake

Anthony can manually place exported candle CSV files under `data/forex_engine/`. Required columns:

```text
timestamp,open,high,low,close
```

Optional columns:

```text
volume,symbol,timeframe
```

The loader validates sorted timestamps, duplicate timestamps, missing OHLC values, positive prices, and whether high/low contain open/close. It does not download data and does not call a broker.

## Strategy Candidate

`supertrend_pullback_v1` requires:

- Supertrend direction alignment.
- Close confirmation.
- Body/range strength.
- ATR volatility adequacy.
- Repeated flip/chop blocking.
- Entry distance limit from the Supertrend band.
- Minimum reward:risk.

Blocked setups emit explicit `NO_TRADE` reasons.

## Evidence Gate

The edge gate can classify:

- `FAIL`
- `WATCHLIST`
- `PAPER_FORWARD_READY`

The daily report maps output to:

- `REJECTED`
- `NEEDS_MORE_DATA`
- `CANDIDATE`
- `PAPER_FORWARD_READY`

It never emits `LIVE_READY`.

## Validation

```powershell
python -m pytest tests/forex_engine
python -m automation.forex_engine.run_supertrend_edge_demo
python -m automation.forex_engine.run_supertrend_walk_forward_demo
python -m automation.forex_engine.run_daily_edge_report
```

## Safety Boundary

- PAPER_ONLY.
- No broker integration.
- No OANDA integration.
- No credentials.
- No real orders.
- No webhooks.
- No network ingestion.
- No scheduler or daemon.
- No live execution.

Future promotion discussion requires larger local data, passing walk-forward evidence, costed metrics, operator review, and separate protected approval.
