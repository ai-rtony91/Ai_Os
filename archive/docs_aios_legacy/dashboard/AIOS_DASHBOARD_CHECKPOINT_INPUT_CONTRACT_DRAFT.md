# AI_OS Dashboard Checkpoint Input Contract Draft

Status: DRAFT
Phase: Phase 12 Pack C
Stage: 12.12 - Dashboard Status Wiring Readiness

## Purpose

Define how a future dashboard may read checkpoint status from Reports/checkpoints.

## Required Checkpoint Fields

- Date
- Mode
- Phase or stage
- Summary
- Safety status
- Next safe action

## Display Rules

- Prefer the newest checkpoint file by LastWriteTime.
- Show the checkpoint filename and linked report path if present.
- Mark missing safety status as UNKNOWN.
- Mark conflicting checkpoint and report evidence as MISMATCH.

## Boundary

This is a planning contract only. No dashboard code edits are authorized.

