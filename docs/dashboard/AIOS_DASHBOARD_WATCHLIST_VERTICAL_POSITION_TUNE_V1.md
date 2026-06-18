# AIOS Dashboard Watchlist Vertical Position Tune V1

## Status

APPLIED_UI_REFINEMENT

## Purpose

This packet moves the compact watchlist higher in the Minimal Operator Dashboard so the operator sees ranked pairs immediately after the compact header.

## Files Changed

- `apps/dashboard/src/MinimalOperatorDashboard.jsx`
- `apps/dashboard/src/MinimalOperatorDashboard.css`
- `docs/dashboard/AIOS_DASHBOARD_WATCHLIST_VERTICAL_POSITION_TUNE_V1.md`

## Watchlist Position Change

- Moved the existing dashboard status summary from above the full dashboard body into the right-side analysis stack.
- Kept the watchlist as the first panel in the primary dashboard content.
- Reduced header height and top-level gaps so the watchlist begins closer to the top of the viewport.
- Kept the selected-pair, chart, and opportunity explanation area aligned beside the watchlist.

## Safety Labels Preserved

The dashboard must continue to visibly preserve:

- `READ_ONLY`
- `FIXTURE_NOT_LIVE`
- `BLOCKED` when relevant
- `LIVE_TRADING_ALLOWED_FROM_THIS_DATA: false`

This packet does not change fixture data, data labels, trading behavior, source truth, broker readiness, or live-trading permission.

## Validation Run

Required validation for this packet:

- `npm run build --prefix apps/dashboard`
- `git diff --check`
- `git status --short --branch`

## Remaining UI Polish Candidates

- Browser-review the first viewport after build validation can run in the local environment.
- Tune header copy or badge placement if the first viewport still feels too tall.
- Revisit chart height only if the watchlist and selected-pair panels feel visually mismatched after browser review.
