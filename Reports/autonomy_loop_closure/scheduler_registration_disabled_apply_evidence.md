# Scheduler Registration Disabled Apply Evidence

Status: TASK REGISTERED DISABLED / NO RUN

Packet: AIOS-SCHEDULER-DISABLED-REGISTRATION-SAFE-V2
Lane: scheduler-registration-disabled-safe-v2
Recorded at: 2026-06-11T14:32:43-04:00

## Task Registration

- Task name: `AIOS_Relay_Nightly`
- Registration status: registered
- Trigger: daily at `02:00` local time
- Observed start boundary: `2026-06-12T02:00:00`
- Working directory: `C:\Dev\Ai.Os`
- Action summary: Task Scheduler uses `pwsh` to launch the AI_OS night-cycle script with the approved apply flag from the disabled task definition.
- Disabled status: confirmed disabled
- Windows state: `Disabled`
- Last run time: `11/30/1999 00:00:00`
- Last task result: `267011` (`SCHED_S_TASK_HAS_NOT_RUN`)

## Query Output Summary

Task Scheduler COM query returned:

- `Enabled=false`
- `State=Disabled`
- executable matched `pwsh`
- expected arguments matched the approved scheduler review
- working directory matched `C:\Dev\Ai.Os`
- last result indicated the task has not run

## Safety Confirmations

- Task was not run.
- Task was not enabled.
- Runtime was not launched.
- Runtime was not executed.
- Queue was not mutated.
- Approval inbox was not mutated.
- Worker inbox was not mutated.
- Command queue was not mutated.
- SOS was not sent by Codex.
- Broker and live trading remained blocked.
- No credentials, tokens, ntfy topics, private URLs, or secrets were stored.
- `telemetry/runtime/` was not written.
- `apps/dashboard/` was not written.
- No destructive cleanup was performed.

## Rollback Commands

Disable rollback:

```powershell
schtasks /change /tn "AIOS_Relay_Nightly" /disable
```

Delete rollback:

```powershell
schtasks /delete /tn "AIOS_Relay_Nightly" /f
```

## Source Evidence

- `Reports/autonomy_loop_closure/scheduler_manual_registration_review_after_ntfy_sos.json`
- `automation/orchestration/work_packets/proposed/AIOS-SCHEDULER-MANUAL-REGISTRATION-APPLY-REQUEST-AFTER-NTFY-SOS.md`
- `Reports/human_gate/ntfy_remote_sos_delivery_proof_record.json`
- `Reports/autonomy_loop_closure/ntfy_remote_sos_delivery_consumption.json`

## Next Safe Action

Review the disabled registration evidence in a PR. Enabling `AIOS_Relay_Nightly` requires a separate Anthony-approved APPLY packet.
