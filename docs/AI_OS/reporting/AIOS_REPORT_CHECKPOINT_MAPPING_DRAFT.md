# AIOS Report Checkpoint Mapping Draft

Status: Draft planning doc
Stage: 12.3

## Purpose

Plan how reports and checkpoints should map to each workload.

## Mapping Rules

- Every DRY_RUN should have a daily report and checkpoint.
- Every APPLY should have a daily report and checkpoint.
- Missing pairings must be listed as gaps.
- Conflicting pairings must be marked MISMATCH.

## Boundary

Mapping is informational and does not modify existing reports or checkpoints.
