> Historical/reference-only legacy AI_OS document.
>
> This file is not active AI_OS_V2 authority. Current operating authority is `AGENTS.md`; current V2 front-door/context authority is `README.md`; current source-of-truth mapping lives under `docs/governance/`.
>
> Preserve this file for historical context and durable-rule extraction only. Do not follow stale repo paths, CLEAN-era ACTIVE_REPO references, or `docs/AI_OS` authority claims unless a future approved V2 canonical document explicitly promotes them.

# AI_OS Worktree Worker Architecture

## Purpose

This document defines the planned architecture for supervised Codex worker lanes using git worktrees. The goal is to let multiple workers investigate or apply scoped changes without editing the controlled integration repo directly.

## Integration Lane

The main repo remains the controlled integration lane.

- It is the source of truth for validation.
- It runs Work Intelligence checks.
- It reads worker reports.
- It detects file ownership conflicts.
- It decides whether a worker lane is blocked, ready for DRY_RUN review, or eligible for a later operator-approved APPLY.

Workers must not edit the main repo directly.

## Worker Worktrees

Each worker should use a separate git worktree and a separate branch.

Recommended pattern:

```text
ACTIVE_REPO/
worktrees/
  worker-01-dashboard-ui/
  worker-02-tradingview/
  worker-03-traderspost/
```

Each worktree should map to one worker lane and one branch. The branch naming rules are defined in a later phase.

## Worker Scope

Worktrees are for:

- DRY_RUN inspection.
- scoped APPLY only after operator approval.
- isolated validation before returning evidence to the integration lane.

Worktrees are not for uncontrolled merges, protected root edits, live trading changes, broker integration, API keys, or real order logic.

## Worker Reports

Worker reports remain mandatory evidence.

Each worker report must declare:

- worker identity
- lane
- mode
- files planned
- files deleted
- validation commands
- summary

The integration lane reads these reports before any merge or APPLY review. Planned files must be declared before APPLY.

## Conflict Handling

If multiple worker reports declare the same planned file, Work Intelligence must treat the overlap as a blocked conflict.

Conflicts remain queue items, not approvals.

Expected blocked queue item:

```text
WI-WORKER-FILE-CONFLICT
```

The operator must resolve file ownership before any merge or APPLY action continues.

## Merge Boundary

Phase 20 does not introduce automated merge behavior.

- No automatic merge.
- No automatic rollback.
- No worker count expansion.
- No direct worker write to main.
- No bypass of validation.

Merge validation and rollback behavior are planned for later phases.

## Safety Rules

- No commit is performed by this architecture.
- No push is performed by this architecture.
- No `git add .`.
- No protected root file edits.
- No dashboard edits.
- No broker, OANDA, API key, live execution, or real order logic.
- Main repo validation remains required before any integration decision.

## Validation

Run from the main repo:

```powershell
powershell -ExecutionPolicy Bypass -File automation/work_intelligence/Test-AiOsWorkIntelligenceScan.ps1
powershell -ExecutionPolicy Bypass -File automation/operator/Test-AiOsParallelWorkerReports.ps1
git diff --check
git status --short --branch
```
