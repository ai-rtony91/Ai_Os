# AI_OS Tool Registry Dashboard Status Contract Draft

## Purpose

Define the local mock-data contract for rendering Tool Registry readiness in the dashboard.

## Fixture Path

`apps/dashboard/mock-data/tool-registry-status-fixture.example.json`

## Required Fields

- `tool_id`
- `label`
- `category`
- `desired_status`
- `detected_status`
- `installed`
- `command`
- `version`
- `path_hint`
- `needs_login`
- `needs_config`
- `blocked_reason`
- `last_checked`
- `notes`

## Display Rules

- The dashboard should show the label and detected status.
- The static preview should show tool name, status, category/type, notes or blocked reason, and last checked / fixture timestamp when available.
- The static preview may show summary counts derived from fixture `detected_status` values.
- Missing tools should show MISSING, not trigger install.
- Login-required tools should show NEEDS_LOGIN and remain manual.
- Internal repo modules should show INTERNAL_MODULE.
- Blocked actions should show BLOCKED with reason text.
- Fixture load failure should show: `Tool registry fixture unavailable — mock data only.`

## Safety Boundary

The dashboard reads local fixture data only. It must not run detection commands from the browser or connect directly to external services.

## Static Preview Wiring

Stage 13.4 and Stage 13.5 wire the fixture into the static preview only:

- `apps/dashboard/AIOS_STATIC_PREVIEW.html`
- `apps/dashboard/js/aios-static-preview.js`
- `apps/dashboard/css/aios-static-preview.css`

React app integration is deferred. Real API calls, live detection, account integration, credential handling, OANDA, broker paths, and trading execution are excluded.

## Validator Reference

Fixture contract validation is handled by:

`automation/tools/Test-AiOsToolRegistryFixtureContract.DRY_RUN.ps1`
