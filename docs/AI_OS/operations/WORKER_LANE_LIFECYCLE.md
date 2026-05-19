# Worker Lane Lifecycle

Status: CURRENT
Mode: Operations documentation

## Purpose

Worker lanes let AI_OS split work across controlled paths and branches while MAIN CONTROL keeps final authority.

Workers inspect, plan, validate, and report. They do not own final approval, staging, commit, push, PR creation, merge, or recovery decisions.

## Lifecycle

1. MAIN CONTROL defines the objective.
2. MAIN CONTROL identifies the lane and allowed paths.
3. Worker runs DRY_RUN inspection.
4. Worker reports planned files, blockers, validators, and next action.
5. MAIN CONTROL checks lane isolation.
6. MAIN CONTROL approves exact APPLY scope, if needed.
7. Worker edits only approved files.
8. Worker runs relevant validators.
9. MAIN CONTROL reviews git status and merge readiness.
10. Save, PR, and merge remain separately approved actions.

## Required Lane Evidence

Before APPLY, a lane should have:

- worker ID
- lane ID
- repo path
- branch
- allowed paths
- blocked paths
- assigned packet or task
- planned file list
- validator list
- report output

## Lane Check Commands

Run from the repo root:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\workers\Get-AiOsWorkerLanes.ps1
powershell -ExecutionPolicy Bypass -File scripts\workers\Test-AiOsWorkerIsolation.ps1 -ProposedPaths docs/AI_OS/operations
```

Use the proposed paths that match the actual APPLY scope.

## Worker States

- `unassigned`: no packet or task is approved.
- `dry_run`: worker may inspect and report only.
- `apply_approved`: worker may edit exact approved files only.
- `validation`: worker or validator lane runs approved checks.
- `review_required`: MAIN CONTROL must review evidence before more work.
- `blocked`: work stops until the blocker is resolved.
- `complete`: worker has reported final state and no further action is implied.

## Worker Lane Rules

- One worker owns one active APPLY scope at a time.
- Do not edit protected root files unless explicitly approved.
- Do not edit dashboard code, runtime code, policy code, telemetry internals, or worker scripts unless the task explicitly approves those paths.
- Do not edit secrets or credentials.
- Do not mix AI_OS operations docs with trading execution logic.
- Do not continue beyond the approved stop point.

## Stale or Unregistered Lanes

A lane needs MAIN CONTROL review when it is unregistered, dirty, missing a worktree, missing from the lane registry, or has stale evidence.

Closing, deleting, pruning, renaming, or merging stale lanes requires explicit operator approval.

## Next Safe Action

Run worker lane governance before assigning APPLY work, then run isolation against the exact proposed file paths.
