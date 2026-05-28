# AI_OS Night Supervisor V1

Night Supervisor V1 is a read-only operational intelligence layer for AI_OS.

It observes queues, work packets, locks, approvals, gate evidence, worker files, hard-stop state, and repo state. It writes local reports only.

## Reads

- `automation/orchestration/work_packets/`
- `automation/orchestration/locks/`
- `automation/orchestration/approval_inbox/`
- `automation/orchestration/gates/`
- `automation/orchestration/safety/Test-AiOsHardStop.ps1`
- `automation/orchestration/workers/`
- configured telemetry read models when present

## Writes

- `telemetry/night_supervisor/NIGHT_SUPERVISOR_REPORT_<timestamp>.json`
- `telemetry/night_supervisor/MORNING_BRIEF_<timestamp>.md`
- `telemetry/night_supervisor/BLOCKER_SUMMARY_<timestamp>.json`
- `telemetry/night_supervisor/NEXT_SAFE_ACTION_<timestamp>.json`

## Never Does

- no packet movement
- no lock release
- no approval changes
- no gate approval
- no staging, commit, push, merge, rebase, or reset
- no broker, OANDA, live trading, API key, or secret handling
- no dashboard UI work
- no scheduled task, service, startup, or background worker installation

## Safe Usage

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/night_supervisor/Start-AiOsNightSupervisor.DRY_RUN.ps1
```

Quiet JSON without report files:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/night_supervisor/Start-AiOsNightSupervisor.DRY_RUN.ps1 -QuietJson -NoTelemetry
```

## Limitations

Night Supervisor classifies from existing metadata quality. Missing or malformed packet, approval, lock, or gate fields are reported as warnings or follow-up items, not repaired automatically.

## Next Planned Phases

- terminal launcher
- gate decision audit persistence
- approval inbox enforcement review
- richer worker state telemetry
