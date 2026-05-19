# Validator Implementation Plan

## Purpose

This package defines the first docs-only runtime validator implementation plan for AI_OS.

It does not create enforcement scripts. It explains what future validators must check, what result they must report, and what the operator should do next.

## Scope

Allowed documentation path:

`docs/AI_OS/dispatcher/runtime/validators/`

Allowed report example path:

`Reports/dispatcher/runtime/validators/`

No files outside those paths belong to this package.

## Runtime Validator Goal

The runtime validator chain protects AI_OS work from unsafe routing mistakes before the work reaches commit packaging.

The validator chain must answer five beginner-readable questions:

1. Is this work approved for the current phase and stage?
2. Are all changed files inside the approved paths?
3. Are blocked or protected files untouched?
4. Are runtime report examples valid JSON?
5. Is stale worker, stale lock, or dirty repo state blocking the next action?

## Result Statuses

Use only these statuses for validator findings:

| Status | Meaning | Operator action |
| --- | --- | --- |
| `PASS` | The check found no blocker. | Continue to the next validator. |
| `FAIL` | The check found a real problem in the approved scope. | Fix the issue before continuing. |
| `BLOCKED` | The check found an unsafe or disallowed condition. | Stop and request human review. |
| `REVIEW_REQUIRED` | The check found state that may be valid but needs a human decision. | Review evidence before continuing. |

## Phase 15.6 DRY_RUN Findings Used

The Phase 15.6 DRY_RUN validator findings are carried forward into this package:

- exact-file staging is required
- `git add .` and `git add -A` are not allowed
- dirty repo state does not block DRY_RUN
- dirty repo state blocks commit packaging unless every changed file is reviewed
- untracked files require review
- allowed paths must be checked before APPLY
- blocked paths must stop the package
- protected root files must stop the package
- changed JSON examples must parse
- stale workers and stale locks require review before reassignment or override
- interrupted APPLY state must be reviewed before resume
- orphan packets must be reconciled before new APPLY work starts
- validators report findings only; they do not stage, commit, push, approve, or edit files

## Validator Chain

Future implementation should route validators in this order:

1. Read `git status --short --branch`.
2. Check stage requirements.
3. Check allowed paths.
4. Check blocked paths.
5. Check protected root files.
6. Check broker, OANDA, API key, live trading, and webhook boundaries.
7. Check dirty repo state.
8. Parse changed JSON files.
9. Run `git diff --check`.
10. Confirm changed files match approved files.
11. Confirm exact-file staging instructions.
12. Check stale worker state.
13. Check stale lock state.
14. Check interrupted APPLY and orphan packet recovery state.
15. Write a local validator result report.

## Human Control Rule

Validators must not:

- edit files
- stage files
- commit
- push
- approve APPLY
- approve stale lock override
- approve stale worker reassignment
- connect to brokers
- place orders
- trigger webhooks

## Next Safe Action Examples

Use short next actions that tell the operator exactly what to do.

Examples:

- `Run git status --short --branch and review unrelated changes before commit packaging.`
- `Fix JSON parse errors before continuing.`
- `Stop. This package touches a protected root file and needs a new approval.`
- `Stage exact approved files only after human commit approval.`
- `Review stale worker ownership before reassignment.`
- `Stop. Reconcile the orphan packet before assigning new APPLY work.`
- `Review interrupted APPLY evidence before resuming or reassigning the packet.`
