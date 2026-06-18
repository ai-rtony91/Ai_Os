# AIOS Dashboard Layout Density Cleanup V1

## Status

APPLIED_UI_REFINEMENT

## Purpose

This packet tightens the existing Minimal Operator Dashboard vertical slice so the read-only operator view is easier to scan and has less unused dark space.

## Files Changed

- `apps/dashboard/src/MinimalOperatorDashboard.jsx`
- `apps/dashboard/src/MinimalOperatorDashboard.css`
- `docs/dashboard/AIOS_DASHBOARD_LAYOUT_DENSITY_CLEANUP_V1.md`

## Layout Improvements

- Grouped the dashboard into a primary operator work area, a safety work area, and a compact workflow area.
- Kept the watchlist on the left and the selected-pair, chart, and opportunity explanation stack together on the right.
- Moved risk/P/L, exit readiness, and bridge safety into a tighter lower safety strip.
- Reduced header height, page padding, panel padding, card gaps, table spacing, chart height, and field spacing.
- Converted the workflow from a tall report-style list into a compact scan strip on wide viewports.
- Preserved the existing read-only dashboard behavior and did not change fixture data, trading logic, broker logic, or dashboard data semantics.

## Safety Labels Preserved

The UI must continue to display the required safety labels:

- `READ_ONLY`
- `FIXTURE_NOT_LIVE`
- `LIVE_TRADING_ALLOWED_FROM_THIS_DATA: false`
- `BLOCKED`

This cleanup only changes layout density and visual balance. It does not imply live market data, live trade permission, or broker readiness.

## Validation Run

Required validation for this packet:

- `npm run build --prefix apps/dashboard`
- `git diff --check`
- `git status --short --branch`

## Remaining UI Cleanup Candidates

- Review the dashboard in a browser at desktop and mobile widths after the build passes.
- Tune the watchlist table columns if horizontal scrolling remains too heavy.
- Consider making the workflow strip collapsible after the operator control flow stabilizes.
- Add visual screenshot validation in a future dashboard QA packet if the repo adopts that workflow.
