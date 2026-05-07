# AI_OS Master Validator Execution Standard Draft

Status: DRAFT
Phase: Phase 12 Pack C
Stage: 12.11 - Master Validator Operationalization

## Purpose

Define the operating standard for running AI_OS DRY_RUN validators across Stage 7 through Stage 12 before APPLY, checkpoint, commit, or dashboard handoff work.

## Execution Rule

The master validator runner must remain read-only. It may inspect files, report missing paths, run existing `.DRY_RUN.ps1` validators, and emit terminal status. It must not create, overwrite, delete, move, rename, deploy, connect brokers, place trades, add secrets, or edit dashboard code.

## Required Operator Flow

1. Confirm the repo root is the active AI_OS repository.
2. Run `git status --short --branch`.
3. Run the master validator script.
4. Review PASS, WARN, FAIL, and SKIPPED results.
5. Stop if any FAIL result touches protected files, secrets, broker execution, live trading, deployment, or dashboard code.
6. Create or update a report only during an approved APPLY workload.

## Output Format

Each validator result should include:

- Validator name
- Validator path
- Scope
- Status: PASS, WARN, FAIL, or SKIPPED
- Evidence path
- Required next action

## Inventory Rule

The validator inventory must be updated whenever a new approved `.DRY_RUN.ps1` validator is added under `automation`. Missing validators must be reported as WARN unless the stage requires them for safety enforcement, in which case they must be reported as FAIL.

## No-Write Guarantee

The master validator must not write output files during ordinary DRY_RUN execution. Future health report output must require explicit APPLY approval.

