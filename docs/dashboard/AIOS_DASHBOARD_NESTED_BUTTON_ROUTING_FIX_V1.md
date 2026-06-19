# AIOS Dashboard Nested Button Routing Fix V1

## Status

APPLIED_UI_BUGFIX

## Purpose

This packet fixes the Minimal Operator Dashboard nested-flow route cards so route actions are explicit child buttons instead of making the whole card a native button container.

## Files Changed

- `apps/dashboard/src/MinimalOperatorDashboard.jsx`
- `apps/dashboard/src/MinimalOperatorDashboard.css`
- `docs/dashboard/AIOS_DASHBOARD_NESTED_BUTTON_ROUTING_FIX_V1.md`

## Routing Fix Applied

- Converted `DoorCard` from conditional `button` / `div` output to a stable `article` card.
- Added a dedicated `.doorCardAction` button for navigable cards.
- Preserved the existing Home -> Forex Bot -> Watchlist -> Pair Detail state flow.
- Kept non-route cards display-only.

## Safety Boundary Preserved

This packet does not change fixture data, source truth, trading behavior, broker readiness, live-trading permission, runtime mutation, secrets, or external API calls.

## Validation Run

Required validation for this packet:

- `npm run build --prefix apps/dashboard`
- `git diff --check`
- `git status --short --branch`
