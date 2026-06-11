# Scheduler Manual Registration Review After ntfy SOS

Packet: `AIOS-SCHEDULER-MANUAL-REGISTRATION-REVIEW-AFTER-NTFY-SOS-RUN-V1`
Status: `REVIEW_READY_ONLY`
Current main HEAD: `8b481d28622e2bced4626445eadadc90a4fd651c`

## Summary

Remote ntfy SOS delivery is confirmed for review, and the private topic, topic URL, token, credential, and secret-like routing values are not stored in the repo.

Scheduler registration is review-ready only. This packet did not register a scheduled task, modify Windows Task Scheduler, launch runtime, execute runtime, mutate queues, send SOS, touch broker paths, trade live, access credentials, delete files, push to main, merge, or close PRs.

## Evidence Files Inspected

- `automation/orchestration/work_packets/proposed/AIOS-SCHEDULER-MANUAL-REGISTRATION-REVIEW-AFTER-NTFY-SOS.md`
- `Reports/human_gate/ntfy_remote_sos_delivery_proof_record.json`
- `Reports/autonomy_loop_closure/ntfy_remote_sos_delivery_consumption.json`
- `Reports/autonomy_loop_closure/final_human_gated_runtime_blocker_review.md`
- `Reports/autonomy_loop_closure/final_blocker_matrix_after_533.md`
- `Reports/scheduler_preview/scheduler_registration_preview.json`
- `Reports/scheduler_preview/scheduler_registration_preview_summary.md`
- `automation/orchestration/scheduler/SCHEDULED_TRIGGER_PROPOSAL.md`
- `automation/orchestration/scheduler/Invoke-AiOsSchedulerPreview.DRY_RUN.ps1`
- `automation/orchestration/Invoke-AiOsNightCycle.ps1`
- `automation/orchestration/runtime/Start-AiOsPersistentRuntimeSupervisor.ps1`
- `automation/orchestration/night_supervisor/README.md`
- `aios.ps1`

## ntfy SOS Proof Status

Remote ntfy SOS delivery is `REMOTE_SOS_DELIVERY_CONFIRMED_FOR_REVIEW`. ntfy is notification-only. It does not authorize phone-to-AI_OS command execution, command response, runtime control, scheduler registration, runtime launch, runtime execution, or queue mutation.

ADB is disabled and not the final SOS path. Telegram/Tasker was not used.

## Scheduler Readiness

Classification: `REVIEW_READY_ONLY`

Reason: a candidate scheduled task, trigger, action, working directory, and rollback command are observable in the existing scheduler proposal, but Anthony has not approved scheduler registration. Runtime launch, runtime execution, queue mutation, broker action, and live trading remain blocked.

## Candidate Scheduler Target

- Task name: `AIOS_Relay_Nightly`
- Purpose: start one gated AI_OS relay/night cycle without manual launch.
- Trigger: daily at `02:00` local time.
- Run-as context: current Windows user.
- Working directory: `C:\Dev\Ai.Os`
- Action: `pwsh -NoProfile -ExecutionPolicy Bypass -File "C:\Dev\Ai.Os\automation\orchestration\Invoke-AiOsNightCycle.ps1" -Apply`
- Log path: `C:\Dev\Ai.Os\relay\logs\night_cycle.log`
- Source: `automation/orchestration/scheduler/SCHEDULED_TRIGGER_PROPOSAL.md`

## Candidate Registration Step

Status: `NOT AUTHORIZED YET`

```powershell
schtasks /create /tn "AIOS_Relay_Nightly" /tr "pwsh -NoProfile -ExecutionPolicy Bypass -File \"C:\Dev\Ai.Os\automation\orchestration\Invoke-AiOsNightCycle.ps1\" -Apply" /sc DAILY /st 02:00 /ru "%USERNAME%" /rl LIMITED /f
```

UI fallback: use Windows Task Scheduler to create a daily 02:00 task named `AIOS_Relay_Nightly` that runs the same `pwsh` action from `C:\Dev\Ai.Os`, only after Anthony separately approves the exact registration.

## Rollback Or Disable Step

Status: `NOT AUTHORIZED YET`

Disable:

```powershell
schtasks /change /tn "AIOS_Relay_Nightly" /disable
```

Delete:

```powershell
schtasks /delete /tn "AIOS_Relay_Nightly" /f
```

## Pre-Registration Validation Commands

```powershell
git status --short --branch
Test-Path C:\Dev\Ai.Os\automation\orchestration\Invoke-AiOsNightCycle.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/scheduler/Invoke-AiOsSchedulerPreview.DRY_RUN.ps1 -OutputJson
python -m json.tool Reports/human_gate/ntfy_remote_sos_delivery_proof_record.json
python -m json.tool Reports/autonomy_loop_closure/ntfy_remote_sos_delivery_consumption.json
powershell -NoProfile -ExecutionPolicy Bypass -Command "$errors = $null; [System.Management.Automation.PSParser]::Tokenize((Get-Content -Raw automation/orchestration/Invoke-AiOsNightCycle.ps1), [ref]$errors) | Out-Null; if ($errors) { $errors; exit 1 } else { 'PARSE_OK' }"
```

## Post-Registration Validation Commands

```powershell
schtasks /query /tn "AIOS_Relay_Nightly" /fo LIST /v
powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-ScheduledTask -TaskName 'AIOS_Relay_Nightly' | Select-Object TaskName,State,TaskPath"
powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-ScheduledTaskInfo -TaskName 'AIOS_Relay_Nightly' | Select-Object LastRunTime,LastTaskResult,NextRunTime"
git status --short --branch
```

## Preserved Blocks

- Scheduler registration is not authorized in this packet.
- Windows Task Scheduler mutation is blocked.
- Runtime launch and runtime execution remain blocked.
- Queue mutation remains blocked.
- Approval, worker inbox, and command queue mutation remain blocked.
- Codex SOS send remains blocked.
- Broker action and live trading remain blocked.
- Credentials, ntfy topics, tokens, topic URLs, and live notification config must not be stored in the repo.

## Next Safe Action

Review `automation/orchestration/work_packets/proposed/AIOS-SCHEDULER-MANUAL-REGISTRATION-APPLY-REQUEST-AFTER-NTFY-SOS.md`.

Only if Anthony separately approves scheduler registration should a later APPLY lane register the exact task and then validate it. This review does not grant that approval.
