# AIOS Dashboard Read-Only Live Data Bridge V1

## Status

Status: DASHBOARD_DISPLAY_CONTRACT

Zone: DASHBOARD

Human Owner: Anthony Meza

## Scope

This document defines how the Minimal Operator Dashboard displays read-only live data bridge status.

It does not authorize browser-side broker calls, live trading, BUY, SELL, close trade, order placement, broker write calls, secret reads, account ID display, token display, order ID display, transaction ID display, package changes, commits, pushes, PR creation, or merge activity.

## Dashboard Rule

The dashboard displays sanitized read-model truth. It never creates broker truth, account truth, order truth, approval truth, signal truth, P/L truth, or history truth.

## Visible Bridge Status

Dashboard pages may display:

- source type
- freshness
- broker reachable
- positions reconciled
- P/L available
- trading history available
- live execution allowed: `false`
- next safe action
- block reason

The display must remain read-only and text-only in lower page content.

## Page Coverage

The bridge status can appear on:

- System
- Watchlist
- Position
- Risk / P&L
- Exit
- Trading History
- Execution Readiness

Home and Forex navigation remain icon-first. Page identity remains emoji-only where already built.

## No Browser Broker Calls

The dashboard must not call OANDA, read environment variables, read `.env`, request API tokens, request account IDs, or connect to broker endpoints.

The runtime script produces sanitized report/read-model evidence for operator review. Future dashboard wiring may consume a sanitized generated artifact only after a separate packet defines the safe file path and load mechanism.

## Default Display

When no generated read-model is available, the dashboard displays:

```text
READ_ONLY
LIVE_READY: false
SOURCE: FIXTURE_NOT_LIVE or NO_READ_MODEL_AVAILABLE
NEXT SAFE ACTION: run read-only live data bridge
```

## Execution Still Blocked

Read-only bridge status does not approve trading. Live execution stays blocked until the future paper signal loop, live micro-trade arming gate, and separate Human Owner approval for broker write behavior.
