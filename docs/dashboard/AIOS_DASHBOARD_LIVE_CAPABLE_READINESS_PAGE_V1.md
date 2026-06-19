# AIOS Dashboard Live-Capable Readiness Page V1

## Status

Status: DASHBOARD_DISPLAY_CONTRACT

Zone: DASHBOARD

Human Owner: Anthony Meza

## Scope

This document defines the Minimal Operator Dashboard page for live-capable execution readiness.

It does not authorize live trading, broker writes, order placement, live close-trade actions, secret reads, API-token handling, account identifier handling, transaction identifier handling, package changes, runtime connector changes, commits, pushes, PR creation, or merge activity.

## Page Purpose

The page gives the operator one read-only place to see whether AIOS can progress from dashboard review toward governed execution readiness.

It must show:

- `LIVE_READY: false` by default
- blocked reason list
- next safe action
- live data readiness
- broker state readiness
- signal readiness
- risk readiness
- exit readiness
- trading history writeback readiness

## Dashboard Rules

The dashboard displays truth. It does not create truth.

Navigation and page controls may request local read-model projections. They must not place trades, close trades, read secrets, arm broker execution, approve risk, approve signals, or write trading history.

Dashboard buttons remain read-only unless future readiness gates are green and a separate packet authorizes the exact non-live or live action. This page must not add a live BUY/SELL button.

## Visual Rules

- Top shell page identity uses the existing icon-only rendering.
- The page identity strip remains icon-only.
- Lower page content uses text labels and status values only.
- No duplicate icon/text identity is added to the page header.
- Source, freshness, and live-trading permission labels remain visible.

## Display Model

The page must display these overall fields:

```text
LIVE_READY:
ACTION_MODE:
LIVE_BUY_SELL_BUTTON:
NEXT_SAFE_ACTION:
```

The page must also display each readiness section with a status and block reason when not ready.

## Blocked Default

The default page state is:

```text
LIVE_READY: false
ACTION_MODE: READ_ONLY
LIVE_BUY_SELL_BUTTON: NOT_PRESENT
NEXT_SAFE_ACTION: Connect permitted read-only data and broker reconciliation in a later packet, then run paper signal execution before any live arming gate.
```

## Stop Conditions

Stop future dashboard work if it would:

- add a live BUY/SELL control
- add live close-trade behavior
- call broker write APIs
- read secrets or `.env` files
- display account IDs, API tokens, raw broker payloads, private order identifiers, or transaction identifiers
- imply fixture, delayed, demo, stale, or unverified data is live-tradable
- bypass risk, exit, P/L truth, history writeback, source, secret, broker, or Human Owner approval gates
