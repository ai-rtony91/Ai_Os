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

## Operator Intent Protection Doctrine

AI_OS workflow guidance must protect the operator's intent before solving the technical task.

The operator-visible success condition must be defined before implementation. A change is not complete just because code was edited, validation passed, or a command succeeded. A change is complete only when the operator's real workflow behaves as intended.

Before a work batch begins, identify:

- What the operator is trying to do.
- What the operator should visibly see when it works.
- What should remain unchanged.
- What system component is responsible.
- What assumptions are being made.
- What should be inspected before action.

Workflow rules:

1. Do not solve from the first symptom alone.
   Inspect the responsible boundary before changing files or behavior.

2. Use precise operational language.
   "Exit," "disable," "pause," "close," "hide," "launch," and "remove" are not interchangeable.

3. Define visible success.
   Examples:
   - The tray icon disappears.
   - The terminal opens in the expected repo.
   - The PR shows the expected files.
   - The game launches while the helper is no longer running.
   - Only one helper icon exists.

4. Change one behavior at a time.
   Avoid stacking multiple fixes before testing the operator-visible outcome.

5. Protect do-not-touch boundaries.
   Each task should state what must not be edited, deleted, committed, pushed, recreated, or automated.

6. Separate task classes.
   Repo features, local machine tools, launcher behavior, documentation, temporary workarounds, and operator preferences must not be mixed unless explicitly approved.

7. Stop on drift.
   If the operator says the direction is wrong, stop and realign. Do not defend the current design or add more workarounds.

8. Prefer the smallest safe change.
   Avoid new scripts, watchdogs, dependencies, repo features, or automation layers unless they are required by the operator-visible success condition.

This doctrine applies globally to AI_OS work, Codex prompts, assistant guidance, local tooling, repo edits, automation planning, and troubleshooting.

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
