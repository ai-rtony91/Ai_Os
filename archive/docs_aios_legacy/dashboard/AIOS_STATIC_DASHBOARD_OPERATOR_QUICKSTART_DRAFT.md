# AI_OS Static Dashboard Operator Quickstart Draft

Status: Draft
Mode: Local static dashboard operator guide
Date: 2026-05-08

## Purpose

Provide a short operator guide for opening the static AI_OS dashboard, checking repository state, testing the theme selector, and staying inside fixture-only safety boundaries.

## Open The Static Dashboard

From PowerShell, run:

```powershell
Start-Process "C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN\apps\dashboard\AIOS_STATIC_PREVIEW.html"
```

Expected result:

The local static dashboard preview opens in the default browser.

Stop condition:

Stop if the file does not open or the path is not found. Verify the active repo path before continuing.

## Check Git Status Before Working

From the active repo root:

```powershell
git status --short --branch
```

Expected clean state:

```text
## main...origin/main
```

If the branch is ahead of origin or files are modified, stop and identify the local changes before starting new APPLY work.

## Test The Theme Selector

In the dashboard top status strip, use the `Theme` selector.

Test each option:

- Default AI_OS Dark
- Terminal Green
- Cyan Command
- Amber Warning
- High Contrast

Expected behavior:

- Default AI_OS Dark removes all theme flavor classes.
- Terminal Green applies `theme-terminal-green`.
- Cyan Command applies `theme-cyan-command`.
- Amber Warning applies `theme-amber-warning`.
- High Contrast applies `theme-high-contrast`.
- The dashboard changes visual flavor only.
- No execution, account, API, deployment, broker, trading, or live AI action starts.

## Fixture-Only Meaning

Fixture-only means the dashboard reads local example/mock files and static page state only.

Fixture-only does not mean:

- Live API connection.
- Account connection.
- Credential use.
- Broker connection.
- Trading execution.
- Cloud deployment.
- Live AI execution.

The static dashboard is a local visual/control surface preview, not a production service.

## Normal Local Warnings

When opened directly from the local file path, some browser behavior can vary:

- Local fixture fetches may show unavailable messages.
- Browser dropdown styling may vary by browser.
- Local visual preference may persist in browser `localStorage`.
- Browser security rules may differ from a future hosted preview.

These warnings are normal for local static preview work unless they block the dashboard from rendering or create misleading readiness status.

## What Not To Do

Do not:

- Connect APIs.
- Read or store secrets.
- Install software.
- Deploy infrastructure.
- Connect accounts.
- Connect brokers.
- Place trades.
- Enable trading execution.
- Run live AI execution.
- Edit React files unless explicitly approved.

## Next Safe Verification

Run:

```powershell
git status --short --branch
```

Stop if the working tree is not in the expected state.
