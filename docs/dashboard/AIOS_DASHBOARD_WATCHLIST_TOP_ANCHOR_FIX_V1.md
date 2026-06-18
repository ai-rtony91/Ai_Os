# AIOS Dashboard Watchlist Top Anchor Fix V1

## Status

APPLIED_UI_BUGFIX

## Purpose

This packet fixes the watchlist panel so compact pair rows start directly under the Watchlist heading instead of sitting lower in a mostly empty card.

## Files Changed

- `apps/dashboard/src/MinimalOperatorDashboard.css`
- `docs/dashboard/AIOS_DASHBOARD_WATCHLIST_TOP_ANCHOR_FIX_V1.md`

## Root Cause Found

The watchlist panel was allowed to stretch vertically with the surrounding primary dashboard grid. Because the panel itself is a CSS grid, that extra height could stretch the internal heading/list tracks and leave a large blank area between the Watchlist heading and the first pair row.

## Spacing And Top-Anchor Fix Applied

- Changed the watchlist panel from vertical stretch behavior to top-aligned behavior.
- Added explicit `align-content: start` and `justify-content: stretch` on the watchlist panel.
- Added explicit top alignment on the watchlist list and panel heading.
- Kept the compact list-card watchlist layout and selected-row highlight.
- Preserved the previous no-overlap row containment behavior.

## Safety Labels Preserved

The dashboard must continue to visibly preserve:

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

- Browser-review the first viewport to confirm the first watchlist row appears immediately under the panel heading.
- Tune panel heights only after visual inspection confirms the top anchor is stable.
- Remove obsolete table CSS in a separate cleanup packet if the compact list remains the canonical watchlist presentation.
