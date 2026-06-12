# Proposed Request Packet: Scheduler Manual Registration Apply Request After ntfy SOS

Status: PROPOSED / REVIEW-ONLY / REQUEST-ONLY
This file is not an executable Codex packet and does not authorize scheduler registration, Task Scheduler mutation, runtime launch, runtime execution, queue mutation, approval mutation, worker inbox mutation, command queue mutation, SOS send by Codex, broker action, live trading, credential access, deletion, push to main, merge, or PR closure.

## Purpose

Request a separate human-approved APPLY lane for manual scheduler registration now that remote ntfy SOS delivery is confirmed for review.

## Human Approval Requirement

Anthony must separately approve scheduler registration before any command below is run. This proposed packet is only a request and review artifact.

## Exact Candidate Registration Details

- Task name: `AIOS_Relay_Nightly`
- Trigger: daily at `02:00` local time
- Action: `pwsh -NoProfile -ExecutionPolicy Bypass -File "C:\Dev\Ai.Os\automation\orchestration\Invoke-AiOsNightCycle.ps1" -Apply`
- Working directory: `C:\Dev\Ai.Os`
- Log path: `C:\Dev\Ai.Os\relay\logs\night_cycle.log`
- Rollback disable command: `schtasks /change /tn "AIOS_Relay_Nightly" /disable`
- Rollback delete command: `schtasks /delete /tn "AIOS_Relay_Nightly" /f`

Candidate registration command, not authorized yet:

```powershell
schtasks /create /tn "AIOS_Relay_Nightly" /tr "pwsh -NoProfile -ExecutionPolicy Bypass -File \"C:\Dev\Ai.Os\automation\orchestration\Invoke-AiOsNightCycle.ps1\" -Apply" /sc DAILY /st 02:00 /ru "%USERNAME%" /rl LIMITED /f
```

## Critical Boundary

Scheduler registration must not imply runtime execution approval. The scheduled action includes `-Apply` and would start a future gated night cycle when the schedule fires, so the later APPLY lane must explicitly state whether registration-only is approved, whether the task should remain disabled after creation, and what validation proves no protected runtime or queue path was touched during registration.

Queue mutation, broker action, live trading, credential storage, ntfy topic storage, token storage, private URL storage, and live notification config remain blocked.

## Allowed Paths For A Future Review Lane

- `Reports/human_gate/`
- `Reports/autonomy_loop_closure/`
- `automation/orchestration/work_packets/proposed/`

## Forbidden Paths For This Proposed Packet

- `automation/orchestration/work_packets/active/`
- `automation/orchestration/work_packets/blocked/`
- `automation/orchestration/work_packets/complete/`
- `automation/orchestration/workers/inbox/`
- `automation/orchestration/command_queue/`
- `automation/orchestration/approval_inbox/`
- `telemetry/runtime/`
- `services/runtime/`
- `services/dispatcher/`
- `services/orchestrator/`
- `services/policy/`
- `scripts/control/`
- `tools/android/`
- `apps/trading_lab/`
- `aios/modules/trader/`
- `.github/`
- `.git/`
- `secrets`
- `credentials`
- `.env`
- `broker files`
- `live trading paths`

## Validation Chain For A Future APPLY Lane

- `git status --short --branch`
- `Test-Path C:\Dev\Ai.Os\automation\orchestration\Invoke-AiOsNightCycle.ps1`
- `powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/scheduler/Invoke-AiOsSchedulerPreview.DRY_RUN.ps1 -OutputJson`
- `python -m json.tool Reports/human_gate/ntfy_remote_sos_delivery_proof_record.json`
- `python -m json.tool Reports/autonomy_loop_closure/ntfy_remote_sos_delivery_consumption.json`
- PowerShell parser validation for `automation/orchestration/Invoke-AiOsNightCycle.ps1`
- Post-registration query of `AIOS_Relay_Nightly`
- `git status --short --branch`

## Stop Point

Stop before any scheduler registration unless Anthony explicitly approves the exact registration action in a separate APPLY packet.

## Safe Next Action

Anthony reviews the scheduler registration request. If approved, generate a separate executable APPLY packet that names the exact task, trigger, action, working directory, log path, rollback command, validation chain, and whether the task must be created disabled.
