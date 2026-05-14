# AI_OS Operator Check Runtime Model

## Purpose

`automation/operator/Invoke-AIOSOperatorCheck.ps1` is a read-only operator cockpit command for AI_OS runtime work.

It gives one compact status report before APPLY, staging, commit, push, recovery resume, or worker reassignment decisions.

## Scope

The operator check reads:

- `git status --short --branch --untracked-files=all`
- `automation/dispatcher/runtime/validators/Invoke-AIOSRuntimeValidatorDryRun.ps1`
- Live runtime status files under `Reports/dispatcher/runtime/`
- Example runtime status files only when the matching live file is missing

It reports:

- repo state
- dirty and untracked counts
- dirty operator file warning
- validator state
- packet queue state
- worker state
- approval state
- commit readiness
- recovery state
- snapshot bootstrap state
- source labels: `LIVE`, `EXAMPLE_FALLBACK`, or `MISSING`
- one next safe action

## Live Runtime Inputs

The command prefers these live files:

- `Reports/dispatcher/runtime/packets/packet_runtime_table.json`
- `Reports/dispatcher/runtime/packets/packet_queue.json`
- `Reports/dispatcher/runtime/workers/active_worker_table.json`
- `Reports/dispatcher/runtime/workers/worker_heartbeat_table.json`
- `Reports/dispatcher/runtime/recovery/live_recovery_state.json`

If a live file is unavailable, the command may read the matching example fallback. Fallback or missing sources keep the result at `REVIEW_REQUIRED`.

## Safety Rules

The command must not:

- edit files
- create files
- delete files
- move files
- rename files
- stage files
- commit
- push
- create startup tasks
- create scheduled tasks
- inspect `Reports/security/` contents
- touch broker, OANDA, API key, or live trading files

`Reports/security/` is path-detected from git status only. If the path appears, the result is `REVIEW_REQUIRED`.

Dirty files under `automation/operator/` are `REVIEW_REQUIRED` unless an approved package explicitly includes them.

Missing or null worker heartbeats are `REVIEW_REQUIRED`.

Stale workers in live recovery state are `REVIEW_REQUIRED`.

## Status Rules

Overall status uses this precedence:

1. `BLOCKED`
2. `REVIEW_REQUIRED`
3. `PASS`

`FAIL` from a validator is treated as `BLOCKED`.

## Intended Operator Use

Run this command before deciding whether a worker can proceed:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File automation/operator/Invoke-AIOSOperatorCheck.ps1
```

If the report is not `PASS`, do not stage, commit, push, or resume APPLY work until the listed warning is reviewed.
