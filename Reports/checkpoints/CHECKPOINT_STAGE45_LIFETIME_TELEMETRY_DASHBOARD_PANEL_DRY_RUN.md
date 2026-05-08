# AI_OS Stage 45 Lifetime Telemetry Dashboard Panel DRY_RUN

Status: Draft
Mode: DRY_RUN placement and mapping report
Date: 2026-05-08

## 1. Purpose

Plan a fixture-only Lifetime Telemetry panel for the static AI_OS dashboard.

This stage does not edit dashboard HTML, JavaScript, CSS, React files, fixtures, APIs, secrets, deployment, broker/trading execution, live AI execution, or real telemetry collectors.

## 2. Current Branch Status

Observed at Stage 45 start:

`## main...origin/main`

Latest pushed lifetime telemetry commit:

`922fa44 Add AI_OS Stage 44 lifetime telemetry push readiness`

## 3. Existing Dashboard Placement

The static dashboard already contains a status panel system:

- `apps/dashboard/AIOS_STATIC_PREVIEW.html`
- Status panel tab root: `.status-panel-tabs`
- Panel frame: `.status-panel-frame`
- Existing tabs include `Status`, `Progress`, `Validator`, `Checkpoint`, `Safety`, `AI Assistance`, `Work Table AI`, and `Next Action`.

Recommended placement:

- Add `Lifetime Telemetry` immediately after `Progress` and before `Validator`.
- Add matching panel `data-status-card="lifetimeTelemetry"` and `data-status-panel="lifetimeTelemetry"`.

This placement matches `docs/AI_OS/dashboard/AIOS_DASHBOARD_LIFETIME_TELEMETRY_PANEL_PLAN_DRAFT.md`.

## 4. Fixture Source

Fixture-only source:

`mock-data/lifetime-telemetry-fixture.example.json`

Backing file:

`apps/dashboard/mock-data/lifetime-telemetry-fixture.example.json`

The dashboard must not use live telemetry collectors or external services.

## 5. Proposed Fields To Display

Evidence-backed totals:

- Evidence scope.
- Commit count.
- Tracked file count.
- Git numstat file-change rows.
- Insertions.
- Deletions.
- Checkpoint file count.
- Daily report file count.
- Progress file count.
- Dashboard mock-data file count.
- Partial duration minutes.
- Partial duration row count.

UNKNOWN boundaries:

- Complete lifetime minutes.
- Complete lifetime hours.
- Complete lifetime bytes changed.
- Complete lifetime KB changed.
- Complete lifetime MB changed.

Quality and readiness:

- Validator evidence signal.
- QA evidence signal.
- Push evidence signal.
- Blocker history status.
- Recovery note history status.
- Latest lifetime telemetry checkpoint reference.
- Safety status for APIs, secrets, deployment, broker/trading execution, live AI execution, and real telemetry collectors.

## 6. Proposed Fallback

Fallback text:

`Lifetime telemetry fixture unavailable — mock data only.`

## 7. Proposed Stage 46 Files

Edit only:

- `apps/dashboard/AIOS_STATIC_PREVIEW.html`
- `apps/dashboard/js/aios-static-preview.js`
- `apps/dashboard/css/aios-static-preview.css`

No React files are approved for this block.

## 8. Risk Check

Risk: dashboard tab count increases from eight to nine.

Mitigation:

- Update status tab CSS to use responsive grid behavior that can wrap safely.
- Keep the panel read-only.
- Use existing theme tokens.

Risk: unsupported lifetime telemetry values could appear definitive.

Mitigation:

- Render complete lifetime time and size totals as `UNKNOWN`.
- Keep fixture notes visible.
- Do not infer historical time from commits.

Risk: telemetry display could be mistaken for telemetry collection.

Mitigation:

- Display fixture-only and real collector blocked safety status.
- Do not add writers, collectors, network calls, account calls, or execution buttons.

## 9. Safety Boundaries

Confirmed for the planned APPLY:

- No APIs.
- No secrets.
- No installs.
- No deployment.
- No React edits.
- No broker/trading execution.
- No live AI execution.
- No real telemetry collectors.
- No historical time invention.

## 10. Stage 46 APPLY Recommendation

Proceed with Stage 46 if the working tree is clean and the edit scope remains limited to the three static dashboard files.
