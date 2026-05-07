# AI_OS Dashboard Data Adapter Boundary Draft

Status: DRAFT
Phase: Phase 12
Stage: 12.14 - Dashboard Status Implementation Readiness

## Purpose

Define the boundary for a future read-only dashboard data adapter that can prepare AI_OS status data for dashboard display.

## Boundary

The dashboard data adapter may read approved local AI_OS artifacts and convert them into display-ready status objects. It must not write to source reports, modify ledgers, change checkpoint files, edit dashboard code, deploy assets, connect brokers, read secrets, or perform live trading actions.

## Allowed Behavior

- Read approved report, checkpoint, progress, and health files.
- Normalize status fields into dashboard-friendly data.
- Mark missing data as UNKNOWN.
- Mark conflicting evidence as MISMATCH.
- Mark stale files as STALE instead of silently treating them as current.

## Blocked Behavior

- No writes to source data.
- No credential or secret reads.
- No broker, trading, or deployment calls.
- No direct dashboard HTML, CSS, or JavaScript edits from the adapter.
- No automatic repair or cleanup.

## Human Approval Rule

Any adapter implementation must be approved in a later APPLY stage after this planning boundary is reviewed.

