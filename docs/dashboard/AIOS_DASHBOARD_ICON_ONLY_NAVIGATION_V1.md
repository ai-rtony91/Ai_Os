# AIOS Dashboard Icon Only Navigation V1

## Status

APPLIED_UI_NAV_READABILITY_PASS

## Purpose

This packet converts the Minimal Operator Dashboard primary navigation controls to icon-only visible navigation while preserving accessible names through `aria-label` and `title` attributes.

This is a visual UX pass only. It does not change routing behavior, fixture data, broker/API behavior, secret handling, or live-trading permissions.

## Files Changed

- `apps/dashboard/src/MinimalOperatorDashboard.jsx`
- `apps/dashboard/src/MinimalOperatorDashboard.css`
- `docs/dashboard/AIOS_DASHBOARD_ICON_ONLY_NAVIGATION_V1.md`

## Icon-Only Navigation Changes

- Home navigation cards now show only destination emoji for Forex Bot, System, Safety, and Settings.
- Forex Bot hub navigation cards now show only destination emoji for Watchlist, Position, Risk / P&L, and Exit.
- Watchlist row detail buttons now show only the Pair Detail emoji and expose pair-specific labels such as `View EUR/USD details`.
- Back buttons now show only `←` and expose `Back` through `aria-label` and `title`.
- Breadcrumb buttons for known destinations now use icon-first navigation, with pair names preserved where they identify the selected detail context.

## Text Removed

- Visible `Open` text was removed from clickable navigation tiles.
- Visible destination labels were removed from primary navigation tiles.
- Visible `View` text was removed from watchlist row detail buttons.
- Visible `Back` text was removed from back buttons.
- Status badges were removed from primary navigation tiles to keep those controls icon-only.

## Text Preserved

Text remains visible where it carries operational or safety meaning:

- page headings
- pair names
- field labels and values
- risk/P&L values
- source truth labels
- `LIVE_TRADING_ALLOWED_FROM_THIS_DATA: false`
- `READ_ONLY`
- `BLOCKED`
- `FIXTURE_NOT_LIVE`
- safety explanations
- chart, analytics, exit, and decision content

## Routing Preserved

The existing React state routing remains unchanged:

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

## Safety Boundary

The dashboard remains display-only for fixture data. This packet does not add live broker calls, API calls, secret reads, `.env` access, order routing, or live-trading behavior.

## Validation

Required validation for this packet:

- `npm run build --prefix apps/dashboard`
- `git diff --check`
- `git status --short --branch`
