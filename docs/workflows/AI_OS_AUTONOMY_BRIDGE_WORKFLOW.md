# AI_OS Autonomy Bridge Workflow

Status: v1 workflow

## What It Does

Autonomy Bridge v1 connects local Relay evidence to Night Supervisor review, Morning Digest output, and dashboard-readable state.

Flow:

1. Relay output is read from local `relay/` evidence.
2. Night Supervisor evidence is read from local supervisor and telemetry paths.
3. Items are classified as `PASS`, `WARN`, `BLOCKED`, `NEEDS_APPROVAL`, or `UNKNOWN`.
4. A compact Morning Digest Markdown report is generated when APPLY is used.
5. A dashboard-readable JSON state is generated when APPLY is used.
6. Raw evidence paths are preserved for review.

## What It Does Not Do

The bridge does not:

- approve APPLY
- launch workers
- move packets
- mutate approvals
- stage files
- commit
- push
- open or merge PRs
- call the internet
- handle API keys or secrets
- run broker, OANDA, webhook, live trading, or real order paths

## Outputs

DRY_RUN prints planned outputs only.

APPLY writes:

- `telemetry/night_supervisor/AUTONOMY_BRIDGE_STATE.json`
- `telemetry/morning_digest/MORNING_DIGEST_STATE.json`
- `telemetry/morning_digest/MORNING_DIGEST_LATEST.md`

Dashboard fixture:

- `apps/dashboard/mock-data/autonomy_bridge_state.sample.json`

The telemetry files are runtime evidence. Review before deciding whether any should be committed.

## How Night Supervisor Uses It

Night Supervisor can run the bridge after Relay work has produced local evidence. The bridge summarizes what happened, what is blocked, what needs approval, and what Anthony should review next.

## How Dashboard Reads It

The dashboard can consume the `dashboard_cards` array from the bridge state. A later dashboard UI lane can add a compact mission card using:

- title
- status
- summary
- metrics
- next_action
- details_ref

## Morning Review

Anthony reviews:

- What happened
- What needs approval
- What was blocked
- What changed
- What to do next

Start with `telemetry/morning_digest/MORNING_DIGEST_LATEST.md` after an APPLY run.

## Blocked

Stop and escalate if the bridge detects:

- non-main branch without explicit override
- forbidden output path
- live trading, broker, OANDA, API key, real webhook, real order, or secret scope
- missing bridge module
- invalid JSON output
- validator failure

## Run DRY_RUN

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/night_supervisor/Invoke-AiOsAutonomyBridge.DRY_RUN.ps1
```

## Run APPLY

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/night_supervisor/Invoke-AiOsAutonomyBridge.DRY_RUN.ps1 -Apply
```

## Validate

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File automation/status/Test-AiOsAutonomyBridge.DRY_RUN.ps1
```

## Next Safe Action

Run DRY_RUN first. If the planned output paths are correct, run APPLY, then run the validator before any commit review.
