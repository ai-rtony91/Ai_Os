# AIOS Dashboard Symmetry And Watchlist Compression V1

## Status

APPLIED_UI_REFINEMENT

## Purpose

This packet refines the existing Minimal Operator Dashboard so the read-only operator view feels more balanced, compact, comfortable, and easier to scan.

## Files Changed

- `apps/dashboard/src/MinimalOperatorDashboard.jsx`
- `apps/dashboard/src/MinimalOperatorDashboard.css`
- `docs/dashboard/AIOS_DASHBOARD_SYMMETRY_AND_WATCHLIST_COMPRESSION_V1.md`

## Watchlist Compression Changes

- Replaced the wide spreadsheet-style watchlist table with a compact selectable watchlist list.
- Kept pair, rank, opportunity score, confidence, trend, fixture price, volatility, Supertrend, last update, and source status visible.
- Reduced repeated row label noise by showing source status as a compact row-level status line.
- Kept pair selection as local read-only UI state only.
- Avoided horizontal scrolling for the watchlist at normal desktop widths.

## Symmetry And Layout Changes

- Rebalanced the primary dashboard columns so the watchlist is compact and the selected-pair analysis area has more room.
- Added safe/blocked status and next action to the top status strip for faster operator scanning.
- Preserved the lower balanced safety row for Risk/P&L, Exit Readiness, and Bridges/Safety.
- Kept spacing, card padding, and row rhythm consistent with the existing Minimal Operator Dashboard layout.

## Safety Labels Preserved

The dashboard must continue to visibly preserve:

- `READ_ONLY`
- `FIXTURE_NOT_LIVE`
- `BLOCKED` when relevant
- `LIVE_TRADING_ALLOWED_FROM_THIS_DATA: false`

This packet does not change data meaning, trading behavior, source truth, broker readiness, or live-trading permission.

## Validation Run

Required validation for this packet:

- `npm run build --prefix apps/dashboard`
- `git diff --check`
- `git status --short --branch`

## Remaining UI Polish Candidates

- Browser-review the compressed watchlist at desktop, tablet, and mobile widths.
- Tune the number of watchlist metrics shown per row if future live data adds more fields.
- Consider a future purely visual screenshot QA packet after dashboard layout expectations stabilize.
