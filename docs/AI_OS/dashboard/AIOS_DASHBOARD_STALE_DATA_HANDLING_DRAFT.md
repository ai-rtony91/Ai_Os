# AI_OS Dashboard Stale Data Handling Draft

Status: DRAFT
Phase: Phase 12
Stage: 12.14 - Dashboard Status Implementation Readiness

## Purpose

Plan how the dashboard should handle old or potentially stale AI_OS status files.

## Stale Data Signals

- No checkpoint exists for the current workload.
- The latest progress ledger row references an older checkpoint.
- Validator health is older than the latest APPLY report.
- Daily report status conflicts with git status evidence.
- File timestamps are newer than their internal reported date.

## Display Rules

- Show STALE rather than PASS when freshness cannot be proven.
- Include the evidence file path.
- Show the last known timestamp if available.
- Keep the next safe action visible even when status is stale.

## Operator Rule

Stale status should trigger a DRY_RUN refresh or validator run before APPLY, commit, push, or dashboard implementation work.

