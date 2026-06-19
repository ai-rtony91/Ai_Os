# AIOS Dashboard Live Micro-Trade Arming Gate V1

## Status

Status: DASHBOARD_DISPLAY_CONTRACT

Zone: DASHBOARD

Human Owner: Anthony Meza

## Scope

This document defines how the Minimal Operator Dashboard displays live micro-trade arming gate status.

It does not authorize browser-side broker calls, live trading, live buy, live sell, live close, order placement, broker write calls, secret reads, account identifier display, token display, real order identifier display, transaction identifier display, package changes, commits, pushes, PR creation, or merge activity.

## Dashboard Rule

The dashboard displays sanitized arming truth. It does not create arming truth, broker truth, account truth, order truth, approval truth, signal truth, P/L truth, or history truth.

## Visible Arming Status

Execution Readiness may display:

- `LIVE_ARMABLE`
- `LIVE_EXECUTION_ALLOWED`
- required Human Owner phrase
- blocked reasons
- next safe action
- next packet candidate

All values are display-only.

## Required Human Phrase

```text
I AUTHORIZE ONE LIVE MICRO TRADE DRY-RUN ARMING REVIEW
```

The dashboard may display this phrase as the required arming review phrase. It must not treat display of the phrase as execution approval.

## What The Dashboard Must Not Do

The dashboard must not:

- add a live trade button
- add a buy/sell button
- add live close behavior
- call OANDA or any broker endpoint
- read environment variables
- read `.env`
- request or display API tokens
- request or display account identifiers
- place, modify, cancel, or close orders

## Default Display

```text
LIVE_ARMABLE: false
LIVE_EXECUTION_ALLOWED: false
NEXT SAFE ACTION: Resolve arming blockers, review evidence, and keep live execution blocked until a separate approved one-shot execution packet exists.
NEXT PACKET CANDIDATE: AIOS-FOREX-ONE-SHOT-LIVE-MICRO-TRADE-EXECUTION-V1
```

## Why Live Execution Is Still Blocked

The arming gate is a review projection. It does not contain broker write behavior and does not authorize live execution. A future packet must separately define and approve any one-shot live micro-trade execution path.

Profitability is not guaranteed. AIOS may only prepare risk-governed, proof-based, one-shot micro-trade review after evidence is available and the Human Owner explicitly approves the next stage.
