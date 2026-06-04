# AI_OS Dispatch Route Decision Rules

Purpose:
Define route decisions for future OpenAI-produced packet drafts.

## Routes

- `BLOCKED`
- `READ_ONLY_RECON`
- `DOCS_ONLY`
- `FIXTURE_ONLY`
- `DRY_RUN_IMPLEMENTATION`
- `APPLY_HUMAN_APPROVED`
- `PR_VALIDATION`
- `MERGE_HUMAN_APPROVED`
- `NIGHT_SUPERVISOR_PREVIEW`
- `NIGHT_SUPERVISOR_RUNTIME_PENDING_APPROVAL`

## Route Ownership

The dispatcher owns route selection. AI_OS Manager owns final approval, safety, profitability priority, and stop point.

## Night Supervisor Rules

`NIGHT_SUPERVISOR_PREVIEW` is report-only. It cannot start runtime, write telemetry, write locks, write control state, write approval inbox state, or launch a 12h Paper SOS run.

`NIGHT_SUPERVISOR_RUNTIME_PENDING_APPROVAL` is not runtime permission. It means the packet needs a separate human-approved runtime-start packet and context precheck before any supervisor run.

## Fail-Closed Rules

Route `BLOCKED` if a packet requests live OpenAI calls, secrets, `.env`, package install, network, broker/OANDA/live trading, Pi GPIO/motor, Night Supervisor runtime start, telemetry write, control write, approval inbox write, commit, push, merge, rebase, or force push.
