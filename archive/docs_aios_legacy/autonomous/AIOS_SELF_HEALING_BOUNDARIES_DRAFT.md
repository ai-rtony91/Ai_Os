# AIOS Self-Healing Boundaries Draft

Stage: 11.3
Status: Draft planning doc

## Purpose

Define safe boundaries for future AI_OS self-healing workflows.

## Allowed Self-Healing Scope

- Detect missing files.
- Detect stale reports.
- Detect failed validators.
- Propose repair steps.
- Recommend rollback checkpoints.
- Create DRY_RUN repair reports after approval for planning.

## Blocked Self-Healing Scope

- Automatic delete, move, rename, overwrite, reset, clean, merge, or push.
- Secret changes.
- Broker connections.
- Live trading code.
- Trade placement.
- Protected root governance edits.

## Rule

Self-healing must stop at proposal generation unless a human approves APPLY.
