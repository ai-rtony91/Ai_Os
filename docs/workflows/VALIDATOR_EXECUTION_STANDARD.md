# AI_OS Validator Execution Standard

Status: canonical workflow

## Purpose

This document defines how AI_OS validators must behave when they inspect repo state, review readiness, or report safety issues.

Validators exist to provide evidence. They do not approve APPLY, commit, push, merge, deployment, broker execution, live trading, secret handling, or any protected action.

## Authority Boundary

Validator output is evidence for the operator and the active workflow. It is not authorization.

Validators may:

- inspect files and repo state.
- run approved read-only checks.
- report missing paths, malformed evidence, unsafe scope, or failed checks.
- recommend the next safe action.

Validators must not:

- create, overwrite, delete, move, or rename files.
- stage files.
- commit, push, merge, deploy, or release.
- connect brokers, place trades, enable OANDA, or handle secrets.
- start background work, startup tasks, or autonomous loops.
- convert a recommendation into approval.

## Single Live Micro-Trade Exception Boundary

For any future Single Live Micro-Trade Exception, validator output remains evidence only. A validator `PASS`, clean validator chain, missing blocker report, confidence score, recommendation, or generated validation receipt cannot approve, arm, extend, retry, re-enter, execute, release credential handles, or satisfy the exception.

The exception must remain governed by `RISK_POLICY.md`. Approval must be explicit, Human Owner-bound, one-shot, non-transferable, expiring, packet-bound, and compliant with every required `RISK_POLICY.md` exception gate.

Generic approval-like fields such as `approval_status`, `approved_by_human`, `APPROVED`, or `approval_granted` are not sufficient to satisfy a live micro-trade exception. Validators must treat those fields as evidence to inspect, not as authority.

Validator evidence for this exception must not contain credentials, broker order IDs, account identifiers, live payloads, private account data, or secret values.

## Read-Only Validator Rule

Validators default to read-only DRY_RUN behavior.

A validator may write a report only when a separate APPLY task explicitly approves that exact output path and scope. Ordinary validation must not create or update files.

## Validator Severity Values

Validator results must use only these severity values:

- `PASS`
- `REVIEW`
- `WARNING`
- `BLOCKED`
- `UNKNOWN`

Any other severity value is invalid and must be treated as `BLOCKED` until corrected by a separate approved task.

## Validation Packet Requirements

Each validator result should include:

- validator name.
- validator path or command.
- scope inspected.
- result: `PASS`, `REVIEW`, `WARNING`, `BLOCKED`, or `UNKNOWN`.
- blocked reason when result is `BLOCKED`.
- exact-file evidence paths when available.
- next safe action.
- timestamp when available.
- worker or session reference, or `UNKNOWN`.

Identity-spine validators should also report:

- packet ID.
- supervisor identity.
- worker identity.
- zone.
- lane.
- mode.
- approval authority.
- validator chain.
- lock ID when APPLY or shared paths are involved.
- stop point.

Missing identity-spine fields must be reported as `BLOCKED` for APPLY readiness.

## Blocked Result Requirements

A `BLOCKED` result must include:

- the blocked reason.
- the protected action or unsafe condition.
- the evidence path, command output, or observed state that caused the block.
- the required operator approval or recovery step.
- one next safe action.

Missing blocked reason, missing next safe action, or unverifiable evidence keeps the result `BLOCKED`.

## Failure Categories

Validator failures should be classified with the most specific applicable category:

- `SAFETY_FAIL`: secrets, broker access, live trading, protected file edits, destructive actions, deployment, dashboard code edits, or other protected actions outside approval.
- `COVERAGE_FAIL`: required report, checkpoint, validator, progress record, or purpose file is missing.
- `STRUCTURE_FAIL`: required folder, source-of-truth path, or expected repo structure is absent.
- `DATA_FAIL`: report content conflicts with terminal output, file evidence, screenshots, or known repo state.
- `SCRIPT_FAIL`: validator execution failed, returned invalid output, or could not be verified.
- `TRANSITION_FAIL`: workflow advanced despite unresolved conflict, stale evidence, protected file violation attempt, missing next safe action, missing blocked reason, invalid severity, or missing approval readiness.
- `AUTO_REPAIR_ATTEMPT`: a validator attempted to repair, stage, merge, commit, push, or otherwise mutate state.

## Escalation Rules

- `SAFETY_FAIL` blocks APPLY immediately.
- `COVERAGE_FAIL` blocks commit until reviewed or documented as deferred.
- `STRUCTURE_FAIL` requires a DRY_RUN gap plan before APPLY.
- `DATA_FAIL` must be marked as `MISMATCH` or `INVALID DATA` in the current report.
- `SCRIPT_FAIL` may be retried once after checking path and execution policy. If it fails again, stop and report.
- `TRANSITION_FAIL` blocks merge readiness, commit, and push until the operator approves a separate correction task.
- `AUTO_REPAIR_ATTEMPT` blocks readiness immediately.

## No Auto-Repair Rule

Validators may recommend repair work, but they must not perform repair work.

Repair requires a separate approved APPLY task with exact allowed files, blocked files, validation expectations, and a stop point.

## Validation Evidence Requirements

Validation evidence must be exact enough for the operator or next worker to verify.

Acceptable evidence includes:

- exact file paths.
- exact command names.
- terminal result summaries.
- parser or validator result summaries.
- git status or diff evidence when relevant.

Unknown or unverifiable evidence must be labeled `UNKNOWN`, `MISMATCH`, or `INVALID DATA` as appropriate.

Generated reports, runtime state, telemetry, logs, and checkpoint files are evidence only. They do not become authority unless promoted through an approved governance or workflow update.

## Merge, Commit, And Push Readiness Blockers

Merge, commit, and push readiness remains blocked by:

- unresolved conflict.
- stale required evidence.
- protected file violation attempt.
- missing next safe action.
- missing blocked reason.
- invalid severity value.
- missing approval readiness.
- unverifiable exact-file evidence.
- automatic repair attempt.
- merge, commit, push, or stage attempt by a validator.
- broker execution, live trading, OANDA, real orders, real webhooks, credentials, API keys, or secrets in scope.

Validators may report that blockers are absent, but they do not approve merge, commit, push, or APPLY.

## Relationship To Approval Model

This standard supports `docs/security/approval-model.md`.

Validators help determine whether a task is safe enough for review. They do not replace human approval. Any APPLY, protected edit, commit, push, merge, deployment, secret handling, broker work, or live trading-related action still requires the approval model and active operating rules.

## Stop Conditions

A validator or validation pass must stop and report when:

- a protected action lacks approval.
- a blocked action appears in scope.
- evidence conflicts with current repo state.
- required evidence is missing or stale.
- validator output is malformed.
- severity values are invalid.
- a validator attempts to repair or mutate state.
- the current branch or repo root cannot be verified.
- the next safe action is missing.
- required identity, lane, approval, lock, validator, or stop-point fields are missing for a packet under review.

## Next Safe Action Requirement

Every validator result must provide one next safe action.

The next safe action should be one of:

- an exact validation command.
- an exact DRY_RUN prompt.
- an exact APPLY prompt after approval.
- a review instruction.
- a checkpoint instruction.
- a stop point.

The next safe action must not be commit, push, merge, deployment, live trading, broker execution, secret handling, auto-repair, or uncontrolled automation unless the user has separately approved that protected action.
