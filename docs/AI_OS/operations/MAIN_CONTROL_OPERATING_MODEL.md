# MAIN CONTROL Operating Model

Status: CURRENT
Mode: Operations documentation

## Purpose

MAIN CONTROL is the human-owned control lane for AI_OS operations. It decides what work is allowed, which worker lane may handle it, whether APPLY is approved, and whether save, PR, merge, or recovery actions may proceed.

MAIN CONTROL is not a normal worker lane. It is the operating authority that keeps runtime work, queue work, audit work, validation, and governance aligned.

## Operating Rule

Use this sequence for substantial AI_OS work:

1. Define objective and scope.
2. Inspect current files and runtime state.
3. Produce DRY_RUN findings.
4. Approve exact APPLY scope if needed.
5. Run validators.
6. Review git status and merge readiness.
7. Approve exact save, PR, merge, or recovery action only when evidence is complete.

## MAIN CONTROL Owns

- Final APPLY permission.
- Worker lane assignment.
- Queue and packet escalation decisions.
- Protected path approval.
- Runtime start and stop approval.
- Validation checklist acceptance.
- Selective staging decisions.
- Commit, push, PR, and merge approval.
- Recovery resume and stale worker decisions.

## MAIN CONTROL Does Not Do

- Auto-launch Codex workers.
- Bypass DRY_RUN.
- Approve broad edits such as "fix everything".
- Edit secrets, credentials, tokens, broker keys, private keys, or recovery keys.
- Enable live trading, broker execution, OANDA, real webhooks, or real orders.
- Allow worker lanes to edit outside approved paths.
- Treat Reports output as current policy unless explicitly marked CURRENT.

## Evidence Sources

MAIN CONTROL uses these local evidence sources:

- `scripts/control/Get-AiOsRuntimeStatus.ps1`
- `scripts/control/Get-AiOsRuntimeHealth.ps1`
- `scripts/control/Get-AiOsAutomationQueue.ps1`
- `scripts/workers/Get-AiOsWorkerLanes.ps1`
- `scripts/workers/Test-AiOsWorkerIsolation.ps1`
- `scripts/workers/Get-AiOsMergeReadiness.ps1`
- `telemetry/runtime/runtime_state.json`
- `telemetry/runtime/runtime_heartbeat.json`
- `telemetry/work_ledger.jsonl`
- `automation/orchestration/queue/DISPATCHER_QUEUE.json`
- `automation/orchestration/terminal_workstations/AIOS_WORKTREE_LANE_REGISTRY.json`
- `automation/orchestration/workers/AIOS_WORKER_REGISTRY.json`

## Current Control Commands

Run from the repo root:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\control\Get-AiOsRuntimeStatus.ps1
powershell -ExecutionPolicy Bypass -File scripts\control\Get-AiOsRuntimeHealth.ps1
powershell -ExecutionPolicy Bypass -File scripts\control\Get-AiOsAutomationQueue.ps1
powershell -ExecutionPolicy Bypass -File scripts\workers\Get-AiOsWorkerLanes.ps1
```

## Stop Conditions

Stop and return to MAIN CONTROL review when:

- Runtime status is `degraded`, `blocked`, `failed`, `UNKNOWN`, or heartbeat is missing.
- Queue state is stale, contradictory, or has unknown workers.
- Worker lane is unregistered or overlaps another lane.
- A protected path appears in proposed or dirty files.
- Validation fails.
- Git status shows unexpected files.
- Merge readiness reports `BLOCKED` or `REVIEW_REQUIRED`.

## Next Safe Action

Run runtime health, queue, and worker lane checks before assigning any APPLY work.
