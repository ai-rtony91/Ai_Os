# AI_OS Night Supervisor Approval Queue Workflow

Status: v1 workflow

## What It Is

The Night Supervisor Approval Queue is a read-only projection over local Relay approval evidence.

It helps Anthony see:

- what needs review
- what is already approved
- what is rejected
- what is stale
- what is unsafe and blocked
- what is already handled
- what needs more context
- what to do next

## What It Does Not Do

The queue does not:

- approve or reject anything
- move Relay approval files
- replace the canonical approval inbox
- replace the worker task lifecycle standard
- stage files
- commit
- push
- merge
- open PRs
- launch workers
- touch broker, OANDA, API key, webhook, real order, secret, or live trading paths

## Inputs

The queue reads local evidence from:

- `relay/approvals/`
- `relay/approvals/approved/`
- `relay/approvals/rejected/`
- current `git status --short --branch` captured by the runner

Missing folders are allowed. Missing evidence is projected as `UNKNOWN`, not guessed.

## Outputs

DRY_RUN prints counts and next safe action.

Future APPLY output may write generated local evidence:

- `telemetry/night_supervisor/APPROVAL_QUEUE_STATE.json`
- `telemetry/morning_digest/APPROVAL_QUEUE_SUMMARY.md`

These runtime outputs are evidence only and should not be staged unless a later packet explicitly promotes them.

## Status Model

Projection statuses:

- `WAITING_REVIEW`
- `APPROVED`
- `REJECTED`
- `STALE`
- `UNSAFE_BLOCKED`
- `ALREADY_HANDLED`
- `NEEDS_MORE_CONTEXT`
- `UNKNOWN`

This is not the canonical task lifecycle. It is only a Night Supervisor operator view.

## Review Rules

Anthony reviews unsafe and waiting items first.

Stale dirty-repo approvals are marked `STALE` when current Git evidence is clean.

Live trading, broker, OANDA, API key, real webhook, real order, or secret language is marked `UNSAFE_BLOCKED`.

Commit, push, merge, and PR requests remain human-gated. The queue may surface them, but it cannot approve them.

## Dashboard Use

The dashboard can consume a compact card with:

- title
- status
- waiting count
- stale count
- unsafe blocked count
- approved count
- rejected count
- next safe action
- details ref

UI wiring requires a separate approved dashboard lane.

## Run DRY_RUN

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/night_supervisor/Invoke-AiOsApprovalQueue.DRY_RUN.ps1
```

## Run APPLY

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/night_supervisor/Invoke-AiOsApprovalQueue.DRY_RUN.ps1 -Apply -InspectionOnly
```

## Validate

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File automation/status/Test-AiOsNightSupervisorApprovalQueue.DRY_RUN.ps1
```

## Next Safe Action

Run DRY_RUN, review the queue, then use a separate exact-scope packet for any APPLY, commit, push, merge, PR, worker launch, or approval mutation.
