# AI_OS Dashboard Status Card Insertion Plan Draft

Status: DRAFT
Phase: Phase 12
Stage: 12.16 - Dashboard Read-Only Mock Status Wiring

## Purpose

Plan where dashboard status cards should appear in the static preview during a future approved implementation.

## Proposed Card Set

- Overall status
- Development metrics
- Phase completion
- Validator health
- Checkpoint status
- Safety status
- Next action

## Proposed Placement

Primary option:

- Insert a compact status section after the existing `status-strip` and before the current `command-stage`.

Fallback option:

- Insert a compact first row inside the existing `command-stage` while preserving the current work-table and assistant rail.

## Placement Rules

- Safety and blocked states must appear before neutral progress data.
- Existing work-table cards must remain available.
- Existing assistant rail and console behavior must remain intact.
- Cards must use stable IDs or data attributes for future JavaScript rendering.

## Blocked Insertions

- No broker controls.
- No trade controls.
- No credential fields.
- No forms that submit data.
- No external API elements.

