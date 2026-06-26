# AI_OS Safe Repair And Recovery Standard

Status: canonical workflow

## Purpose

This document defines the AI_OS standard for safe repair, rollback planning, recovery, collision handling, and post-repair validation.

The goal is to make repairs controlled, scoped, reviewable, and reversible before deeper orchestration or automation integration occurs.

## Authority Boundary

Repair and recovery output is evidence and planning. It is not approval.

This standard does not authorize APPLY, rollback, file deletion, file movement, file rename, broad checkout, reset, cleanup, commit, push, merge, deployment, broker execution, live trading, secret handling, or uncontrolled repair automation.

Only the user can approve APPLY, rollback, commit, push, merge, or any protected action.

## Repair Scope Classification

Every repair must be classified before fixing begins.

Use the most specific applicable category:

- `UI_ONLY`: visible layout, labels, spacing, icons, clutter, or readability.
- `LOGIC_ONLY`: state changes, button behavior, panel state, route behavior, or other bounded logic.
- `MOCK_DATA_ONLY`: fixture data, sample JSON, example status values, or non-production mock state.
- `TRADING_LAB_ONLY`: Trading Lab paper/simulation docs, mock signals, risk gates, scorecards, broker-gate checks, or paper simulation boundaries.
- `CONNECTOR_API_ONLY`: planned integration boundary, connector design, API planning, or external service interface review.
- `VALIDATOR_GAP`: missing, weak, malformed, or absent validation.
- `MIXED_SCOPE`: more than one unrelated area is touched.
- `UNKNOWN`: the category cannot be verified from current evidence.

A repair may have one primary category only. If more than one unrelated category is required, split the work before APPLY.

## UNKNOWN Scope Handling

If repair scope is unclear, mark the category `UNKNOWN`.

`UNKNOWN` repair scope must not proceed to APPLY. The next safe action must be an inspection, classification, ownership check, or user clarification step.

Do not invent missing ownership, affected paths, blocked paths, validators, or rollback plans to make an `UNKNOWN` repair look ready.

## Owner-Routing Requirements

Before APPLY, each repair must identify:

- problem statement.
- repair category.
- current owner or lane.
- likely affected files or folders.
- blocked files or folders.
- validator checks.
- repair type.
- rollback plan.
- approval requirement.
- next safe action.

Ownership must be scoped to the current AI_OS repo structure and active authority. Legacy role names may inform routing, but they do not become active AI_OS worker authority unless current governance explicitly defines them.

If owner or lane cannot be identified, stop and mark the repair `UNKNOWN` or `BLOCKED`.

## Collision Detection Rules

A collision exists when a repair package mixes unrelated work, unrelated file trees, or unrelated ownership lanes.

Collision examples include:

- UI repair plus Trading Lab changes.
- mock-data repair plus dashboard code changes.
- validator repair plus UI behavior changes.
- connector planning plus credential or token handling.
- documentation repair plus runtime or automation changes.

When a collision appears:

1. Stop.
2. Mark the package `MIXED_SCOPE`.
3. List the unrelated scopes.
4. Split the work into smaller repair requests.
5. Route each request through its own approval and validation path.

Mixed-scope repair must not proceed to APPLY.

## Blocked File Handling

Each repair must name blocked files or blocked folders before APPLY.

Blocked files include:

- files outside the approved repair scope.
- protected root governance files unless explicitly scoped.
- `.codex_backups/`.
- secrets, credentials, tokens, private keys, and recovery keys.
- broker, OANDA, live trading, real order, or real webhook paths.
- runtime, automation, orchestration, dashboard, telemetry, or trading paths unless explicitly approved for the repair.

If a blocked file enters scope, stop and report the conflict. Do not continue by broadening the repair.

## Rollback Planning Requirements

Every APPLY repair should include a rollback or recovery note before mutation.

The rollback plan should identify:

- exact files that would need restoration.
- known source of restoration, such as a commit, backup, or prior reviewed state, when known.
- risk of rollback.
- validation needed after rollback.
- approval required before rollback.

If the rollback source is unknown, mark it `UNKNOWN` and do not invent one.

## Rollback Approval Requirements

Rollback is a protected action.

Rollback requires explicit human approval before changing files. Approval should identify the exact files, intended recovery action, expected validation, and stop condition.

Rollback approval for one file or package does not approve broad repo reset, cleanup, delete, move, rename, commit, push, merge, or unrelated restoration.

## Scoped APPLY Repair Rules

APPLY repair may occur only after explicit approval.

A scoped APPLY repair must:

- match the approved problem category.
- edit only approved files.
- avoid blocked files.
- stay inside one repair type.
- preserve unrelated work.
- avoid broad cleanup.
- avoid automatic repair approval.
- avoid uncontrolled automation.
- run or identify required validation.
- report exact files changed.

If the repair needs a larger scope than approved, stop and request a new scoped approval.

## Post-APPLY Validation Requirements

After APPLY and before commit readiness, the repair report must verify:

- problem category was named.
- owner or lane was named.
- approved files were followed.
- blocked files were not touched.
- repair type stayed isolated.
- required validators passed or unresolved validators were reported.
- no secrets were touched.
- no connector/API activation happened without approval.
- no broker, OANDA, live trading, real webhook, or real order path was added.
- rollback note exists.
- commit package contains only related files.
- `git add .` was not used.

Failed or missing validation blocks commit readiness.

## Repair Evidence Requirements

Repair evidence should include:

- problem statement.
- classification.
- owner or lane.
- allowed files.
- blocked files.
- commands run.
- files changed.
- validation result.
- rollback note.
- errors.
- unknowns.
- commit status.
- push status.
- next safe action.

Evidence must be exact enough for the user or next worker to verify.

## Repair Escalation Rules

Escalate or stop when:

- repair category is `UNKNOWN`.
- repair category is `MIXED_SCOPE`.
- ownership is unclear.
- allowed files are missing or vague.
- blocked files are touched or requested.
- rollback plan is missing for APPLY repair.
- validation is missing, stale, or failed.
- protected actions enter scope.
- evidence conflicts with repo state.
- a worker or validator attempts auto-repair.
- next safe action is missing.

Escalation output must include what was attempted, what was expected, what happened, and one next safe recovery step.

## Prohibited Recovery Behaviors

The following are prohibited unless a future explicit user approval names the exact action and scope:

- `git reset --hard`.
- `git clean`.
- broad checkout of unrelated files.
- deleting files.
- moving files.
- renaming files.
- touching `.codex_backups/`.
- overwriting unrelated work.
- broad repo cleanup.
- automatic rollback.
- automatic repair approval.
- repair loops.
- uncontrolled repair automation.

These actions must never be used as default recovery behavior.

## Relationship To Validator Execution Standard

This standard supports `docs/workflows/VALIDATOR_EXECUTION_STANDARD.md`.

Validators may inspect repair scope, allowed files, blocked files, validation evidence, rollback notes, and post-APPLY readiness. Validators may recommend repair but must not perform repair, rollback, staging, commit, push, merge, deployment, broker action, live trading, secret handling, or protected actions.

## Relationship To Worker Lifecycle Standard

This standard supports `docs/workflows/WORKER_TASK_LIFECYCLE_STANDARD.md`.

Repair work must pass through classification, ownership check, blocked path check, runner preview when applicable, validation selection, approval request, APPLY, validation, and review. Unclear or unsafe repairs move to `deferred` or `blocked`, not APPLY.

## Relationship To Approval Model

This standard supports `docs/security/approval-model.md`.

All repair and recovery work defaults to DRY_RUN. APPLY, rollback, protected edits, commit, push, merge, deployment, broker execution, live trading, credential handling, and secret handling require explicit human approval.

## Stop Conditions

Stop and report when:

- repo root or branch cannot be verified when relevant.
- problem statement is unclear.
- repair category is `UNKNOWN`.
- repair category is `MIXED_SCOPE`.
- owner or lane is unclear.
- allowed files are not exact.
- blocked files are requested or touched.
- rollback plan is missing for APPLY repair.
- approval is missing, stale, or denied.
- validation cannot be selected.
- validation fails.
- evidence conflicts with current repo state.
- a broad rollback, reset, clean, delete, move, rename, or unrelated checkout is requested.
- a repair attempts uncontrolled automation.
- next safe action is missing.

## Next Safe Action Requirement

Every repair plan, recovery plan, rollback plan, APPLY repair report, blocked repair, mixed-scope repair, and validation result must end with one next safe action.

The next safe action should be one of:

- an exact inspection command.
- an exact validation command.
- an exact DRY_RUN prompt.
- an exact scoped APPLY prompt after approval.
- an exact rollback approval request.
- a review instruction.
- a checkpoint instruction.
- a stop point.

The next safe action must not bypass approval, validation, protected boundaries, or active authority.
