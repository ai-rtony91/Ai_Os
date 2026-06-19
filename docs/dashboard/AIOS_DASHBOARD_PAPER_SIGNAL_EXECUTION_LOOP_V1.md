# AIOS Dashboard Paper Signal Execution Loop V1

## Status

Status: DASHBOARD_DISPLAY_CONTRACT

Zone: DASHBOARD

Human Owner: Anthony Meza

## Scope

This document defines how the Minimal Operator Dashboard displays the paper signal execution loop status.

It does not authorize browser-side broker calls, live trading, live order placement, live close behavior, broker write calls, secret reads, account identifier display, token display, real order identifier display, transaction identifier display, package changes, commits, pushes, PR creation, or merge activity.

## Dashboard Rule

The dashboard displays sanitized read-model truth. It never creates broker truth, account truth, order truth, approval truth, signal truth, P/L truth, or history truth.

Paper loop status is display-only. It may show whether a sanitized paper loop result exists and what the last paper result reported.

## Visible Paper Loop Status

Trading History and Execution Readiness may display:

- `PAPER_LOOP_AVAILABLE`
- last paper signal
- last paper trade status
- last paper realized P/L
- history writeback status
- live execution allowed: `false`
- next safe action

When no generated paper read-model is loaded, the dashboard must show paper loop availability as `false` and direct the operator to run the paper signal execution loop.

## Trading History Behavior

If no real closed-trade history exists, Trading History may display paper evidence status as a separate paper-only panel.

Paper evidence must remain distinct from real closed-trade history. Paper evidence cannot prove live profitability and cannot make fixture or paper data live-tradable.

## Execution Readiness Behavior

Execution Readiness may display paper loop status next to the live-readiness blockers.

Live readiness remains blocked unless all future live gates are satisfied and the Human Owner explicitly arms execution in a later packet.

## Browser Boundary

The dashboard must not call OANDA, read environment variables, read `.env`, request API tokens, request account identifiers, connect to broker endpoints, place orders, modify orders, cancel orders, or close trades.

The dashboard consumes only sanitized fixture/read-model fields. Runtime scripts produce evidence outside the browser.

## Default Display

```text
PAPER_LOOP_AVAILABLE: false
LAST PAPER SIGNAL: UNAVAILABLE
LAST PAPER TRADE STATUS: NO_PAPER_LOOP_READ_MODEL
HISTORY WRITEBACK STATUS: PAPER_HISTORY_UNAVAILABLE
LIVE EXECUTION ALLOWED: false
NEXT SAFE ACTION: run paper signal execution loop
```

## Stop Conditions

Stop future dashboard work if it would:

- add a live buy/sell control
- add live close behavior
- call broker write APIs
- read secrets or `.env` files
- display account identifiers, API tokens, raw broker payloads, private order identifiers, or transaction identifiers
- imply paper evidence is live-tradable
- bypass risk, exit, P/L truth, history writeback, source, secret, broker, or Human Owner approval gates
