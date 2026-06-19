# AIOS Dashboard Page Identity Emoji Strip V1

## Objective

Apply a single visible identity channel to Minimal Operator Dashboard pages:

- Top page identity strip uses emoji only.
- Lower content, panels, and tables use text only.
- Body content does not repeat the page title.
- Body content does not repeat the page emoji.

## Applied Scope

- `ShellHeader` now renders the current page identity as an emoji-only heading with `aria-label` and `title` for accessibility.
- Repeated body page titles were removed from Forex Bot, Watchlist, and simple status pages.
- Pair Detail keeps the selected pair text because it is specific context, not a duplicate page title.
- Home and Forex icon navigation targets remain emoji-only and clickable.

## Preserved Safety Boundary

- Routing and click handlers were not changed.
- Navigation `aria-label` and `title` attributes were preserved.
- Source truth labels remain visible.
- `READ_ONLY`, `BLOCKED`, and `FIXTURE_NOT_LIVE` meanings remain visible where represented by existing status text.
- `LIVE_TRADING_ALLOWED_FROM_THIS_DATA: false` remains visible where applicable.
- No broker, API, secret, or live trading behavior was added.

## Validation

- Run `git diff --check`.
- Run `git status --short --branch`.
- Do not run `npm build` if the sandbox launcher reports `CreateProcessAsUserW failed: 1312`.
