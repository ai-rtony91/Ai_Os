# AI_OS Tool Registry Dashboard UI Wire-Up Notes Draft

Status: Draft
Mode: Static preview fixture-only

## Purpose

Document the Phase 13 Stage 13.4 and Stage 13.5 static dashboard wire-up for Tool Registry readiness display.

## Fixture Source

The dashboard reads this local mock fixture only:

`apps/dashboard/mock-data/tool-registry-status-fixture.example.json`

## Static Preview Files

The current implementation is limited to:

- `apps/dashboard/AIOS_STATIC_PREVIEW.html`
- `apps/dashboard/js/aios-static-preview.js`
- `apps/dashboard/css/aios-static-preview.css`

## Current UI Behavior

- Displays readiness cards inside the existing Tool Registry section.
- Shows tool name, detected status, category/type, notes or blocked reason, and last checked / fixture timestamp.
- Shows compact summary counts for total tools, READY, INSTALLED, MISSING, NEEDS_LOGIN, NEEDS_CONFIG, BLOCKED, and UNKNOWN.
- Shows `Tool registry fixture unavailable — mock data only.` if the fixture cannot load.

## Deferred Work

React app integration is deferred to a future approved stage.

## Blocked Integrations

The Tool Registry dashboard must not:

- Use real APIs.
- Run live detection from the browser.
- Install software.
- Connect accounts.
- Store credentials.
- Read secrets.
- Trigger OAuth or login automation.
- Connect to Azure services.
- Connect to OANDA or any broker.
- Fire webhooks.
- Enable trading execution.

## Validator Reference

Fixture contract validation is handled by:

`automation/tools/Test-AiOsToolRegistryFixtureContract.DRY_RUN.ps1`

## Next Safe Extension

Any future extension should remain fixture-first and DRY_RUN-reviewed before APPLY. Live detection, React integration, API adapters, persistence, and account-aware behavior each require separate approval.
