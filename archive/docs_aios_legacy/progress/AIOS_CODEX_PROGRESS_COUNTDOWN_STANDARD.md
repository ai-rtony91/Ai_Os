# AIOS Codex Progress Countdown Standard

Status: Draft standard
Mode: Documentation only

## Purpose

Define the countdown standard Codex should use when reporting AI_OS workload progress.

## Step Counting

- planned_steps: total expected work units for the current workload.
- completed_steps: work units finished and verified.
- percent_complete: rounded integer percentage from completed_steps / planned_steps.

## Status Values

- DRY_RUN_PLANNED
- APPLY_READY
- APPLY_IN_PROGRESS
- VALIDATING
- BLOCKED
- COMPLETE_UNCOMMITTED
- COMPLETE_COMMITTED
- UNKNOWN

## Blocked Rules

- blocked must be YES or NO.
- blocker must be populated when blocked is YES.
- next_action must describe the exact safe action needed to proceed.

## Commit Status

Before commit, commit_hash should be UNKNOWN and git_status should reflect the current working tree evidence.

## Required Stop Condition

If progress evidence conflicts with Git, terminal output, reports, or checkpoints, mark the row MISMATCH and stop for operator review.
