# AIOS Dashboard Nested Minimal Forex Flow V1

## Status

APPLIED_UI_REFACTOR

## Purpose

This packet refactors the Minimal Operator Dashboard from an all-at-once dashboard into a nested operator flow for the AIOS forex engine.

## Files Changed

- `apps/dashboard/src/MinimalOperatorDashboard.jsx`
- `apps/dashboard/src/MinimalOperatorDashboard.css`
- `docs/dashboard/AIOS_DASHBOARD_NESTED_MINIMAL_FOREX_FLOW_V1.md`

## New Nested Flow

The dashboard now uses internal React state for four screens:

- Home
- Forex Bot
- Watchlist
- Pair Detail

The user flow is:

```text
Home -> Forex Bot -> Watchlist -> Pair Detail
```

The Pair Detail screen contains chart, price, analytics, risk, exit readiness, safe/blocked state, and next action.

## What Was Simplified

- Home shows only entry cards for Forex Bot, System, Safety, and Settings.
- Forex Bot is now a hub with Watchlist, Current Position, Risk/P&L, and Exit cards.
- Watchlist shows compact pair rows only: pair, score, confidence, trend, data label, and View.
- Pair Detail is the only screen that shows chart, explanation, risk, exit, decision, and next action.
- The prior report-dump layout was removed from the default operator path.

## Safety Labels Preserved

The dashboard continues to visibly preserve:

- `READ_ONLY`
- `FIXTURE_NOT_LIVE`
- `BLOCKED` when relevant
- `LIVE_TRADING_ALLOWED_FROM_THIS_DATA: false`

This packet does not change fixture data, source truth, trading behavior, broker readiness, or live-trading permission.

## Validation Run

Required validation for this packet:

- `npm run build --prefix apps/dashboard`
- `git diff --check`
- `git status --short --branch`

## Remaining UI Polish Candidates

- Browser-review the nested flow at desktop, tablet, and mobile widths.
- Tune the Pair Detail density after visual review.
- Consider separate lightweight views for System, Safety, and Settings after their authority contracts exist.
