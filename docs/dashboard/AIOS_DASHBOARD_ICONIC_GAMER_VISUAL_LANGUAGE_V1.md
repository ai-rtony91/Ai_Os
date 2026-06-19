# AIOS Dashboard Iconic Gamer Visual Language V1

## Status

APPLIED_UI_READABILITY_PASS

## Purpose

This packet updates the Minimal Operator Dashboard visual language so the operator can identify cards, pages, badges, and panels faster through compact icon plus label treatment.

This is a UI readability pass only. It does not change dashboard routing, fixture data, broker behavior, API behavior, secret handling, or live-trading permissions.

## Files Changed

- `apps/dashboard/src/MinimalOperatorDashboard.jsx`
- `apps/dashboard/src/MinimalOperatorDashboard.css`
- `docs/dashboard/AIOS_DASHBOARD_ICONIC_GAMER_VISUAL_LANGUAGE_V1.md`

## Icon And Label Changes

- Home cards now show icon plus short label for Forex Bot, System, Safety, and Settings.
- Forex Bot cards now show icon plus short label for Watchlist, Position, Risk / P&L, and Exit.
- Page headings now include matching icons for faster scan recognition.
- Panel headings now include compact icons for Price, Chart, Analytics, Risk, Exit, Decision, and block reason.
- Status badges now preserve the original text and add semantic icons for ready, blocked, fixture, locked, read-only, and hidden/no-secret states.
- Back buttons now use `← Back`; open and view actions remain short.

## Routing Preserved

The existing React state routing remains unchanged:

```text
Home -> Forex Bot -> Watchlist -> Pair Detail
Home -> System
Home -> Safety
Home -> Settings
Forex Bot -> Position
Forex Bot -> Risk / P&L
Forex Bot -> Exit
```

## Safety Labels Preserved

The dashboard continues to visibly preserve:

- `READ_ONLY`
- `BLOCKED`
- `FIXTURE_NOT_LIVE`
- `LIVE_TRADING_ALLOWED_FROM_THIS_DATA: false`

The dashboard still treats fixture data as display-only and does not add live broker, API, secret, or trading execution behavior.

## Validation

Required validation for this packet:

- `npm run build --prefix apps/dashboard`
- `git diff --check`
- `git status --short --branch`
