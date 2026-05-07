# AIOS Progress Ledger Append Rules Draft

Status: Draft planning doc
Stage: 12.4

## Purpose

Define safe rules for future progress ledger append behavior.

## Rules

- DRY_RUN previews must not append rows.
- APPLY append requires explicit approval.
- Required CSV header must match the progress schema.
- Missing commit hash is UNKNOWN.
- Blocked status requires a blocker and next_action.

## Boundary

This document does not write to any ledger.
