# AIOS Dashboard Remove Home Redundancy V1

## Status

APPLIED_UI_DEDUPLICATION

## Purpose

This packet removes redundant Operator/Home visual elements from the Minimal Operator Dashboard while preserving icon-only navigation, accessibility labels, safety labels, fixture labels, and routing behavior.

This is a visual UI pass only. It does not change fixture data, broker/API behavior, secret handling, or live-trading permissions.

## Files Changed

- `apps/dashboard/src/MinimalOperatorDashboard.jsx`
- `apps/dashboard/src/MinimalOperatorDashboard.css`
- `docs/dashboard/AIOS_DASHBOARD_REMOVE_HOME_REDUNDANCY_V1.md`

## Redundancy Removed

- The breadcrumb row no longer renders when Home is the only current-page crumb.
- Breadcrumbs now omit redundant current-page crumbs on non-detail pages because the header already identifies the page.
- Pair Detail keeps the selected pair context in the breadcrumb so specific context such as `EUR/USD` remains visible.
- The Home screen no longer uses the large framed `.screen` shell.
- The four Home emoji navigation targets now sit directly on the dashboard canvas.

## Navigation Preserved

The existing navigation targets remain unchanged:

```text
Home -> Forex Bot
Home -> System
Home -> Safety
Home -> Settings
Forex Bot -> Watchlist
Forex Bot -> Position
Forex Bot -> Risk / P&L
Forex Bot -> Exit
Watchlist -> Pair Detail
```

## Safety Labels Preserved

The dashboard continues to visibly preserve:

- source truth labels
- `READ_ONLY`
- `BLOCKED`
- `FIXTURE_NOT_LIVE`
- `LIVE_TRADING_ALLOWED_FROM_THIS_DATA: false`

No broker/API calls, secret handling, fixture data changes, or live-trading behavior were added.

## Validation

Required validation for this packet:

- `git diff --check`
- `git status --short --branch`

`npm run build --prefix apps/dashboard` was intentionally not run because this packet instructed Codex not to run npm build while the sandbox launcher is unstable.
