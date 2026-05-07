# AI_OS Dashboard Next Action Input Contract Draft

Status: DRAFT
Phase: Phase 12 Pack C
Stage: 12.12 - Dashboard Status Wiring Readiness

## Purpose

Define how the dashboard may identify the next safe operator action from approved AI_OS reports and checkpoints.

## Source Priority

1. Latest checkpoint next safe action
2. Latest daily report next safe action
3. Latest progress ledger next_action column
4. UNKNOWN if none can be verified

## Display Rules

- Show one concise next action.
- Include the evidence file path.
- Do not generate commands that were not present in a report, checkpoint, or approved operator workflow.
- Mark conflicts as MISMATCH.

## Boundary

The dashboard may display a next action later, but must not execute it.

