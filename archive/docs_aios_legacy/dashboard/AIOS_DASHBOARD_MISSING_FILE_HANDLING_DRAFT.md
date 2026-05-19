# AI_OS Dashboard Missing File Handling Draft

Status: DRAFT
Phase: Phase 12
Stage: 12.14 - Dashboard Status Implementation Readiness

## Purpose

Plan how dashboard status should behave when expected local source files are missing.

## Missing File Rules

- Missing required source file: display UNKNOWN.
- Missing latest checkpoint: display CHECKPOINT_UNKNOWN.
- Missing progress ledger: display PROGRESS_UNKNOWN.
- Missing validator health file: display VALIDATOR_HEALTH_UNKNOWN.
- Missing safety source: display SAFETY_UNKNOWN.
- Missing next action: display NEXT_ACTION_UNKNOWN.

## Blocked Inference

The dashboard must not convert missing data into PASS, COMPLETE, CLEAN, or SAFE.

## Next Action

When a source is missing, the dashboard should point to the relevant DRY_RUN validator or report workflow rather than creating or repairing files automatically.

