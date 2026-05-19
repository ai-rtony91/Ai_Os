# AI_OS Dashboard Progress Ledger Input Contract Draft

Status: DRAFT
Phase: Phase 12 Pack C
Stage: 12.12 - Dashboard Status Wiring Readiness

## Purpose

Define the proposed progress ledger fields the dashboard can read in a later approved implementation.

## Required Columns

```csv
date,time,stage,task_id,task_name,planned_steps,completed_steps,percent_complete,status,blocked,blocker,next_action,checkpoint_file,commit_hash,git_status,notes
```

## Display Rules

- Show the latest row by date and time when available.
- If time is UNKNOWN, sort by file modified time as a fallback.
- Show blocked status as a visible safety state.
- Never infer commit cleanliness if `git_status` is missing.
- Treat missing required columns as INVALID DATA.

## Boundary

This contract does not create live dashboard code and does not write to the progress ledger.

