# AI_OS Dashboard Theme Selector Guide Draft

Status: Draft
Mode: Local static dashboard guidance

## Purpose

Document the Stage 17 static dashboard theme selector and the safety boundaries that keep it local-only.

## Selector Behavior

The selector is a visual preference control in:

`apps/dashboard/AIOS_STATIC_PREVIEW.html`

It is wired by:

`apps/dashboard/js/aios-static-preview.js`

It is styled by:

`apps/dashboard/css/aios-static-preview.css`

The selector does not call external services, account systems, execution services, deployment tools, live AI systems, broker systems, or trading systems.

## Default Theme

The default option is `Default AI_OS Dark`.

When selected, the dashboard removes all flavor classes from `<body>`:

- `theme-terminal-green`
- `theme-cyan-command`
- `theme-amber-warning`
- `theme-high-contrast`

The default visual baseline remains the semantic token set under `:root`.

## Flavor Profiles

Flavor profiles are body classes only:

- `body.theme-terminal-green`
- `body.theme-cyan-command`
- `body.theme-amber-warning`
- `body.theme-high-contrast`

Each flavor class overrides semantic CSS tokens only. It does not change dashboard data behavior, fixture loading, routing, file access, automation execution, or approval rules.

## Local Preference Storage

The selector may use `localStorage` only for local visual preference.

Allowed stored value:

- selected dashboard theme name

Blocked stored values:

- credentials
- account identifiers
- API keys
- private tokens
- trading data
- broker data
- live AI execution state

## Safety Confirmation

The selector is local-only:

- No APIs.
- No account calls.
- No secrets.
- No deployment.
- No broker or trading execution.
- No live AI execution.
- No execution buttons.
- No React integration.

## Safe Future Upgrade Path

Future theme selector changes should follow this order:

1. CSS token changes first.
2. HTML placement changes second.
3. JavaScript preference toggle changes only for local visual preference.
4. No cloud sync until a separate DRY_RUN, approval, validator, and checkpoint exist.

## Validator

Theme selector safety is checked by:

`automation/status/Test-AiOsDashboardThemeSelector.DRY_RUN.ps1`

The validator confirms the selector markup, local-only JavaScript references, matching CSS flavor classes, and forbidden selector-specific additions.
