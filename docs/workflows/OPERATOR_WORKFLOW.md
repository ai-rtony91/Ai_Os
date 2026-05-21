# AI_OS Operator Workflow

Status: canonical workflow
Sources: `docs/AI_OS/operator`, `docs/AI_OS/operator_workflows`, `docs/workflows/aios-operator-workflows.md`

## Purpose

This workflow defines the human-controlled AI_OS operating loop. It does not approve commits, pushes, merges, deployments, worker launches, broker execution, or live trading.

## Standard Loop

1. Inspect current state.
2. Confirm branch and working tree.
3. Classify the task as DRY_RUN or APPLY.
4. Identify allowed paths, blocked paths, validation, and stop point.
5. Produce a DRY_RUN plan when scope is unclear or risky.
6. Wait for explicit human approval before APPLY.
7. Make exact scoped edits only.
8. Run required validation.
9. Report files changed, validation, commit status, push status, and next safe action.

## Git Status Checkpoint Discipline

AI_OS guidance should avoid repetitive status checks after every minor step.

Status checks should be used at major checkpoints only:

- start of a work batch
- pre-commit
- post-push or post-merge
- error recovery
- lane switch
- session shutdown

This protects operator focus, reduces unnecessary interruptions, and keeps guided work grouped into practical mission blocks.

## Human Approval Gates

Explicit approval is required before:

- APPLY.
- Protected root edits.
- Move, delete, rename, overwrite, reset, or clean.
- Commit.
- Push.
- Merge.
- Deployment.
- Credential, secret, broker, webhook, OANDA, or live trading work.

## Clean Stop Conditions

Stop and report when:

- Current branch is wrong.
- Working tree has unexplained changes.
- Requested scope touches blocked paths.
- Required facts are `UNKNOWN`.
- Evidence conflicts and must be marked `MISMATCH` or `INVALID DATA`.
- Validation fails.
- A protected action lacks approval.

## Final Report Contract

Every substantial workflow report should include:

- Task.
- Files inspected.
- Files changed.
- Validation result.
- Errors.
- Unknowns.
- Commit status.
- Push status.
- Next safe action.
