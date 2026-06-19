# AIOS Dashboard Missing Nested Pages Fix V1

## Status

APPLIED_UI_ROUTING_FIX

## Purpose

This packet fixes the nested Minimal Operator Dashboard so visible Home and Forex Bot cards route to real internal pages instead of acting like unclear display-only cards.

## Files Changed

- `apps/dashboard/src/MinimalOperatorDashboard.jsx`
- `apps/dashboard/src/MinimalOperatorDashboard.css`
- `docs/dashboard/AIOS_DASHBOARD_MISSING_NESTED_PAGES_FIX_V1.md`

## New Views Added

- `SYSTEM`
- `SAFETY`
- `SETTINGS`
- `POSITION`
- `RISK`
- `EXIT`

## Buttons And Cards Routed

Home now routes:

- Forex Bot -> Forex Bot
- System -> System
- Safety -> Safety
- Settings -> Settings

Forex Bot now routes:

- Watchlist -> Watchlist
- Current Position -> Current Position
- Risk / P&L -> Risk / P&L
- Exit -> Exit

Watchlist View buttons continue to open Pair Detail for the selected pair.

## Disabled And Read-Only Behavior

No live trading buttons were added. Pages that display operational state use read-only fixture/status data and show `READ_ONLY`, `BLOCKED`, `FIXTURE_NOT_LIVE`, or source labels where relevant.

## Safety Labels Preserved

The dashboard continues to visibly preserve:

- `READ_ONLY`
- `FIXTURE_NOT_LIVE`
- `BLOCKED`
- `LIVE_TRADING_ALLOWED_FROM_THIS_DATA: false`

This packet does not change fixture data, source truth, trading behavior, broker readiness, or live-trading permission.

## Validation Result

Required validation for this packet:

- `npm run build --prefix apps/dashboard`
- `git diff --check`
- `git status --short --branch`
