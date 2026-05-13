# AI_OS Master Validator Execution Standard Draft

Status: DRAFT
Phase: Phase 12 Pack C
Stage: 12.11 - Master Validator Operationalization
Phase 45 update: minimal reuse-first validator-chain behavior

## Purpose

Define the operating standard for running AI_OS DRY_RUN validators before APPLY, checkpoint, merge readiness review, commit, push, or dashboard handoff work.

## Execution Rule

The master validator runner must remain read-only. It may inspect files, report missing paths, run existing `.DRY_RUN.ps1` validators, and emit terminal status. It must not create, overwrite, delete, move, rename, deploy, connect brokers, place trades, add secrets, edit dashboard code, auto-repair findings, execute merges, commit, push, or run autonomous loops.

Validators may report and recommend only. Validators must not repair automatically, stage files, execute merge actions, start background work, run startup tasks, or convert a recommendation into approval.

## Canonical Validator Chain

The validator chain must run in this order when a grouped validation review is requested:

1. ownership
2. conflict
3. stale worker
4. merge package
5. dashboard integrity
6. protected file boundary
7. approval readiness

Validators may be grouped for operator readability, but grouped output must preserve this canonical order.

## Severity Values

Validator output must use only these severity values:

- PASS
- REVIEW
- WARNING
- BLOCKED
- UNKNOWN

Invalid severity values block merge readiness until corrected by an approved APPLY task.

## Required Operator Flow

1. Confirm the repo root is the active AI_OS repository.
2. Run `git status --short --branch`.
3. Run the master validator script.
4. Review PASS, REVIEW, WARNING, BLOCKED, and UNKNOWN results.
5. Stop if any BLOCKED result touches protected files, secrets, broker execution, live trading, deployment, dashboard code, unresolved conflicts, stale evidence, missing next safe action, missing blocked reason, invalid severity, or missing approval readiness.
6. Create or update a report only during an approved APPLY workload.

## Output Format

Each validator result should include:

- Validator name
- Validator path
- Scope
- Result: PASS, REVIEW, WARNING, BLOCKED, or UNKNOWN
- Blocked reason, required when result is BLOCKED
- Evidence path
- Required next safe action
- Timestamp
- Worker reference, or UNKNOWN

## Merge Readiness Rule

Merge readiness is BLOCKED by unresolved conflict, stale required evidence, protected file violation attempt, missing next safe action, missing blocked reason, invalid severity value, missing approval readiness, or any validator result that cannot be verified from exact-file evidence.

Merge readiness may be REVIEW only when all required blockers are absent but operator confirmation is still needed. Merge readiness may be PASS only when every required validator has current exact-file evidence and no protected boundary, conflict, stale evidence, or approval readiness issue exists.

Merge-ready output must remain BLOCKED when any required validation packet is missing, malformed, stale, or uses a severity outside PASS, REVIEW, WARNING, BLOCKED, or UNKNOWN.

## Inventory Rule

The validator inventory must be updated whenever a new approved `.DRY_RUN.ps1` validator is added under `automation`. Missing validators must be reported as WARNING unless the stage requires them for safety enforcement, in which case they must be reported as BLOCKED.

## No-Write Guarantee

The master validator must not write output files during ordinary DRY_RUN execution. Future health report output must require explicit APPLY approval.

## Phase 45 Reuse Boundary

Phase 45 reuses the existing validator chain, failure escalation rules, validation packet standard, and dashboard mock-data fixtures. It must not create duplicate validator-chain files when the existing standards already cover the required behavior.
