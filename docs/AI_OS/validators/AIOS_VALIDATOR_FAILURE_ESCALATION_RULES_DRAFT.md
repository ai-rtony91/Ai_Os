# AI_OS Validator Failure Escalation Rules Draft

Status: DRAFT
Phase: Phase 12 Pack C
Stage: 12.11 - Master Validator Operationalization

## Purpose

Define how AI_OS handles failed DRY_RUN validators before APPLY, commit, push, dashboard handoff, productization work, or autonomous workflow planning.

## Failure Categories

- SAFETY_FAIL: secrets, broker access, live trading, protected file edits, destructive actions, deployment, or dashboard code edits detected outside approval.
- COVERAGE_FAIL: required report, checkpoint, validator, progress, or README purpose file is missing.
- STRUCTURE_FAIL: required folder or source-of-truth planning path is absent.
- DATA_FAIL: report content conflicts with terminal output or file evidence.
- SCRIPT_FAIL: validator execution failed or returned invalid output.

## Escalation Rules

- SAFETY_FAIL blocks APPLY immediately.
- COVERAGE_FAIL blocks commit until reviewed or documented as deferred.
- STRUCTURE_FAIL requires a DRY_RUN gap plan before APPLY.
- DATA_FAIL must be marked as MISMATCH or INVALID DATA in the current report.
- SCRIPT_FAIL must be rerun once after checking path and execution policy. If it fails again, document the failure and stop.

## Required Failure Record

Every failed validator must report:

- Validator path
- Failure category
- Evidence path
- Impacted stage
- Protected action involved: YES or NO
- Required operator approval
- Next safe action

## Recovery Boundary

Validators may recommend repair work, but must not perform automatic repair. Repair APPLY requires a separate approved prompt.

