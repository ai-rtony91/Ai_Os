# AIOS Dashboard Single Identity Channel V1

## Status

APPLIED_UI_DEDUPLICATION

## Purpose

This packet removes duplicate visible identity presentation from the Minimal Operator Dashboard.

The UI rule for this pass is:

```text
One concept = one visible identity channel.
```

This is a visual UI pass only. It does not change routing, fixture data, broker/API behavior, secret handling, or live-trading permissions.

## Files Changed

- `apps/dashboard/src/MinimalOperatorDashboard.jsx`
- `apps/dashboard/src/MinimalOperatorDashboard.css`
- `docs/dashboard/AIOS_DASHBOARD_SINGLE_IDENTITY_CHANNEL_V1.md`

## Duplicate Identity Removed

- Page and section headings now use text titles only.
- Navigation tiles remain emoji-only.
- Status badges now use text-only safety/status labels.
- Panel headings now use text-only labels such as `Price`, `Chart`, `Analytics`, `Risk`, `Exit`, and `Decision`.
- Pair Detail keeps the specific pair text context, such as `EUR/USD`, without repeating the Pair Detail icon.
- Unused icon-label helper styling was removed from the dashboard CSS.

## Emoji/Text Rule Applied

- Header/page identity: visible text only.
- Navigation controls: visible emoji only with `aria-label` and `title`.
- Detail/status rows: visible text labels only.
- Specific pair context: visible text preserved.
- Safety/source truth: visible text preserved.

## Routing Preserved

The existing navigation targets and click handlers remain unchanged:

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
