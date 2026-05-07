# AI_OS Daily Development Volume Rules Draft

Status: DRAFT
Phase: Phase 12
Stage: 12.15 - Development Metrics + Completion Dashboard Readiness

## Purpose

Define how AI_OS should calculate and report daily development volume for future dashboard display.

## Counting Rules

- Count only files created or changed by the approved workload.
- Count folders only when they are newly introduced by an approved workload.
- Do not count protected root governance files unless explicitly approved and reported.
- Do not count generated temporary files unless they are intentionally retained as project artifacts.
- Treat untracked files as pending until committed or explicitly documented.

## Size Rules

- bytes_created uses raw file length in bytes.
- kb_created equals bytes_created / 1024.
- mb_created equals bytes_created / 1048576.
- Display KB and MB with reasonable rounding for dashboard readability.

## Proof Rules

Development volume should reference:

- Git status evidence.
- Daily report evidence.
- Checkpoint evidence.
- Commit hash after commit.

## Invalid Data Rules

If report counts conflict with terminal evidence, mark the metric as MISMATCH and require operator review.

