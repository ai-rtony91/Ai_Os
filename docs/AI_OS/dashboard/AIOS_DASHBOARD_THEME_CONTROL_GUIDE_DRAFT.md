# AI_OS Dashboard Theme Control Guide Draft

Status: Draft
Mode: Local static dashboard guidance

## Purpose

Define how future dashboard theme and flavor changes should be made safely without changing dashboard data behavior, APIs, credentials, deployment, or trading execution boundaries.

## Default Theme

The default AI_OS dark theme lives in `:root` inside:

`apps/dashboard/css/aios-static-preview.css`

The default theme should remain the baseline dashboard style unless a future approved stage explicitly activates a flavor class.

## Inactive Theme Classes

The static dashboard CSS includes inactive flavor classes:

- `body.theme-terminal-green`
- `body.theme-cyan-command`
- `body.theme-amber-warning`
- `body.theme-high-contrast`

These classes override semantic CSS tokens only. They are not active unless a future approved HTML or JavaScript change applies the class to `<body>`.

## Preferred Change Order

Future flavor changes should prefer CSS tokens first:

1. Adjust semantic tokens.
2. Avoid component-level rewrites unless a token cannot safely express the visual change.
3. Keep default `:root` stable unless the default AI_OS dark style is intentionally changed.
4. Validate desktop and mobile readability before commit.

## Safe Edit Levels

### CSS Token Change

Scope: visual flavor only.

Allowed examples:

- Adjust `--accent-primary`.
- Adjust `--surface-panel`.
- Adjust `--state-warn`.
- Adjust `--shadow-panel-hover`.

### HTML Class Activation

Scope: selected static theme.

Example:

`<body class="theme-cyan-command">`

This requires a separate approved APPLY stage because it changes the active visual flavor.

### JavaScript Toggle

Scope: future local-only preference.

A future toggle must remain local-only and must not connect to APIs, accounts, telemetry persistence, cloud services, or live AI services. Any preference storage requires a separate DRY_RUN and approval.

## Blocked Actions

Dashboard theme work must not:

- Connect APIs.
- Read or store secrets.
- Deploy.
- Connect brokers.
- Place trades.
- Enable trading execution.
- Run live AI execution.
- Install software.
- Modify React files unless explicitly approved.

## Validation Checklist

Before committing theme work:

- Confirm only approved files changed.
- Run `git diff --name-only`.
- Run `git diff --check`.
- Run `git status --short --branch`.
- Confirm no API, secret, deployment, broker, trading, or live AI execution path was introduced.

## Next Safe Extension

The next safe extension is a DRY_RUN-only validator that checks for required theme tokens and inactive flavor classes without modifying files.
