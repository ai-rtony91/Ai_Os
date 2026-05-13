# AI_OS Validator Failure Escalation Rules Draft

Status: DRAFT
Phase: Phase 12 Pack C
Stage: 12.11 - Master Validator Operationalization
Phase 45 update: validator-chain failure gates

## Purpose

Define how AI_OS handles blocked or unsafe DRY_RUN validator findings before APPLY, merge readiness review, commit, push, dashboard handoff, productization work, or autonomous workflow planning.

## Failure Categories

- SAFETY_FAIL: secrets, broker access, live trading, protected file edits, destructive actions, deployment, or dashboard code edits detected outside approval.
- COVERAGE_FAIL: required report, checkpoint, validator, progress, or README purpose file is missing.
- STRUCTURE_FAIL: required folder or source-of-truth planning path is absent.
- DATA_FAIL: report content conflicts with terminal output or file evidence.
- SCRIPT_FAIL: validator execution failed or returned invalid output.
- TRANSITION_FAIL: merge-ready state was reached despite unresolved conflict, stale evidence, protected file violation attempt, missing next safe action, missing blocked reason, invalid severity, or missing approval readiness.

## Escalation Rules

- SAFETY_FAIL blocks APPLY immediately.
- COVERAGE_FAIL blocks commit until reviewed or documented as deferred.
- STRUCTURE_FAIL requires a DRY_RUN gap plan before APPLY.
- DATA_FAIL must be marked as MISMATCH or INVALID DATA in the current report.
- SCRIPT_FAIL must be rerun once after checking path and execution policy. If it fails again, document the failure and stop.
- TRANSITION_FAIL blocks merge readiness, commit, and push until an operator approves a separate correction task.
- AUTO_REPAIR_ATTEMPT blocks merge readiness immediately. Validators may recommend correction work only.

## Required Failure Record

Every failed validator must report:

- Validator path
- Failure category
- Evidence path
- Impacted stage
- Protected action involved: YES or NO
- Required operator approval
- Next safe action
- Result: PASS, REVIEW, WARNING, BLOCKED, or UNKNOWN
- Blocked reason when result is BLOCKED

## Merge Readiness Blockers

Merge readiness must remain BLOCKED when any of these are present:

- unresolved conflict
- stale required evidence
- protected file violation attempt
- missing next safe action
- missing blocked reason
- invalid severity value
- missing approval readiness
- unverifiable exact-file evidence
- automatic repair attempt
- merge execution attempt

## Recovery Boundary

Validators may recommend repair work, but must not perform automatic repair. Repair APPLY requires a separate approved prompt. Validators must not run autonomous loops, execute merges, commit, push, or stage files.

Validators must preserve human approval. A validator result is evidence only; it is not approval to merge, commit, push, repair, or execute.
