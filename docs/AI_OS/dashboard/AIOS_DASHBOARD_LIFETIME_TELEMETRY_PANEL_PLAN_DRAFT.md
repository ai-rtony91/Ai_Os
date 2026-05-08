# AI_OS Dashboard Lifetime Telemetry Panel Plan Draft

Status: Draft
Mode: Placement plan only
Date: 2026-05-08

## Purpose

Define the future static dashboard placement for a fixture-only Lifetime Telemetry panel without wiring UI behavior yet.

## Proposed Placement

Place the future `Lifetime Telemetry` panel in the existing status panel area near:

- `Progress`
- `Telemetry`
- `Validator`
- `Checkpoint`

Recommended tab order:

1. Status
2. Progress
3. Lifetime Telemetry
4. Validator
5. Checkpoint
6. Safety
7. AI Assistance
8. Work Table AI
9. Next Action

This keeps development telemetry close to progress and validation rather than mixing it into execution surfaces.

## Fixture-Only Data Source

Future fixture path:

`apps/dashboard/mock-data/lifetime-telemetry-fixture.example.json`

The panel must use local fixture data only.

No real telemetry collectors, background services, APIs, account connections, secrets, deployment, broker/trading execution, or live AI execution are allowed.

## Fields To Display

Recommended display fields:

- Evidence scope.
- Git commit count.
- Tracked file count.
- Checkpoint file count.
- Daily report count.
- Progress file count.
- Dashboard mock-data file count.
- Partial duration minutes.
- Complete lifetime time spent: `UNKNOWN`.
- Complete lifetime bytes/KB changed: `UNKNOWN`.
- Validator status.
- Safety status.

## Fallback Message

Fallback text:

`Lifetime telemetry fixture unavailable — mock data only.`

## No UI APPLY Yet

This stage does not approve editing:

- `apps/dashboard/AIOS_STATIC_PREVIEW.html`
- `apps/dashboard/js/aios-static-preview.js`
- `apps/dashboard/css/aios-static-preview.css`
- React files

UI wire-up should happen only after a future DRY_RUN with exact file scope and visual placement.

## Validation Expectations For Future UI Wire-Up

Future UI wire-up should validate:

- Fixture fetch path is local-only.
- No external URL is introduced.
- Unsupported time and byte totals remain `UNKNOWN`.
- Fallback message is present.
- Mobile layout does not overflow.
- Theme flavors remain readable.

## Safety Boundary

Lifetime Telemetry is an evidence display, not a telemetry collector.
