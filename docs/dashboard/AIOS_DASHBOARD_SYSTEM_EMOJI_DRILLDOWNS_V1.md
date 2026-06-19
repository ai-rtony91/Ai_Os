# AIOS Dashboard System Emoji Drilldowns V1

## Status

APPLIED_UI_SYSTEM_DRILLDOWN_PASS

## Purpose

This packet converts the Minimal Operator Dashboard System status tiles into emoji-only clickable controls. The visible System selection layer now shows only emoji controls, and each control opens a text-only detail panel where operational labels, values, source truth, freshness, and live-trading permission are displayed.

This is a visual UX pass only. It does not change fixture data, broker/API behavior, secret handling, package dependencies, or live-trading permissions.

## Files Changed

- `apps/dashboard/src/MinimalOperatorDashboard.jsx`
- `apps/dashboard/src/MinimalOperatorDashboard.css`
- `docs/dashboard/AIOS_DASHBOARD_SYSTEM_EMOJI_DRILLDOWNS_V1.md`

## System Selection Layer

The System page selection controls are emoji-only:

- Dashboard
- Mode
- Data
- Broker
- Live APIs

Visible text labels are not rendered on the selection controls. Accessible names remain available through `aria-label` and `title`.

## Detail Panels

Each emoji opens a text-only detail panel:

- `DASHBOARD` -> `READY`
- `MODE` -> `READ_ONLY`
- `DATA` -> `FIXTURE_NOT_LIVE`
- `BROKER` -> `BLOCKED`
- `LIVE APIS` -> `BLOCKED`

Every detail panel also displays:

- `SOURCE`
- `FRESHNESS`
- `LIVE_TRADING_ALLOWED_FROM_THIS_DATA`

## Safety Boundary

Preserved safety/source truth values:

- `READ_ONLY`
- `BLOCKED`
- `FIXTURE_NOT_LIVE`
- `LIVE_TRADING_ALLOWED_FROM_THIS_DATA: false`

This packet does not add live broker calls, API calls, secret reads, `.env` access, order routing, package changes, or live-trading behavior.

## Validation

Required validation for this packet:

- `git diff --check`
- `git status --short --branch`
