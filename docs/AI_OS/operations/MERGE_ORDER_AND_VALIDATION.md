# Merge Order And Validation

Status: CURRENT
Mode: Operations documentation

## Purpose

This document defines the current merge review order for AI_OS operations.

Merge is always a MAIN CONTROL decision. Worker lanes may prepare evidence, but they do not merge.

## Merge Order

1. Confirm objective and completed packet.
2. Confirm worker report and exact files changed.
3. Run worker lane governance.
4. Run file isolation check for proposed paths.
5. Run relevant validators.
6. Run `git diff --check`.
7. Run merge readiness check.
8. Review protected paths and blocked actions.
9. MAIN CONTROL decides whether PR or merge review may proceed.
10. Commit, push, PR, and merge require separate explicit approval.

## Current Validation Commands

Run from repo root:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\workers\Get-AiOsWorkerLanes.ps1
powershell -ExecutionPolicy Bypass -File scripts\workers\Test-AiOsWorkerIsolation.ps1 -ProposedPaths docs/AI_OS/operations
git diff --check
powershell -ExecutionPolicy Bypass -File scripts\workers\Get-AiOsMergeReadiness.ps1
git status --short --branch
```

Use actual proposed paths in the isolation check.

## Merge Readiness Inputs

`scripts/workers/Get-AiOsMergeReadiness.ps1` checks:

- current branch
- base branch
- git status
- changed files against base
- protected paths
- `git diff --check`
- merge risk list

If this script fails, merge readiness is not proven.

## Required Evidence Before PR Or Merge

- Worker lane and branch.
- Changed file list.
- Validation commands and results.
- `git diff --check` result.
- Protected path review.
- Queue or packet completion state.
- No unexpected dirty files.
- No live trading, broker, OANDA, API key, secret, webhook, or real order changes.

## Blocked Conditions

Merge review is blocked when:

- current branch is `main`, unless the operator explicitly authorizes main review
- worktree is dirty with unexpected files
- protected paths changed without approval
- validator failed
- merge readiness failed or errored
- worker lane is unregistered and not reviewed
- changed files overlap another active worker's scope
- code touches runtime, dashboard, policy, telemetry internals, or worker scripts without explicit scope

## Next Safe Action

Treat merge readiness as `REVIEW_REQUIRED` until every validator and file-scope check is understood.
