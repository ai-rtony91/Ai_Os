# AI_OS Operator Check Runtime Model

## Purpose

`automation/operator/Invoke-AIOSOperatorCheck.ps1` is a read-only operator cockpit command for AI_OS runtime work.

It gives one compact status report before APPLY, staging, commit, push, recovery resume, or worker reassignment decisions.

## Scope

The operator check reads:

- `git status --short --branch --untracked-files=all`
- `automation/dispatcher/runtime/validators/Invoke-AIOSRuntimeValidatorDryRun.ps1`
- Runtime status examples under `Reports/dispatcher/runtime/`

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
- one next safe action

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

