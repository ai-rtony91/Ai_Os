# AIOS Checkpoint Driven Autonomy Draft

Stage: 11.4
Status: Draft planning doc

## Purpose

Tie autonomous work to checkpoint files so every phase has a recoverable state.

## Rules

- Every major DRY_RUN creates a checkpoint.
- Every APPLY creates a checkpoint.
- Checkpoints must include next safe action.
- Missing checkpoint is BLOCKED.

## Boundary

Checkpoint-driven autonomy reports state; it does not bypass approval.
