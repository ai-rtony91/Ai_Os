# AIOS Dashboard Watchlist No Overlap Fix V1

## Status

APPLIED_UI_BUGFIX

## Purpose

This packet fixes compact watchlist row containment so row text, badges, source labels, and action pills stay readable and do not collide with neighboring dashboard content.

## Files Changed

- `apps/dashboard/src/MinimalOperatorDashboard.css`
- `docs/dashboard/AIOS_DASHBOARD_WATCHLIST_NO_OVERLAP_FIX_V1.md`

## Overlap Fixed

- Added explicit watchlist row grid areas for rank, pair, metrics, source status, and action.
- Let watchlist metadata wrap inside each row instead of forcing crowded inline columns.
- Added `min-width: 0`, row overflow containment, and responsive grid fallbacks for watchlist children.
- Kept source labels visible while allowing the long `LIVE_TRADING_ALLOWED_FROM_THIS_DATA: false` line to wrap within the row.
- Preserved selected row highlighting and local read-only pair selection behavior.

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

- Browser-review the watchlist at desktop, tablet, and mobile widths.
- Tune the number of visible watchlist metrics if future live data adds more fields.
- Consider removing obsolete table-specific CSS in a separate cleanup packet if the table presentation does not return.
