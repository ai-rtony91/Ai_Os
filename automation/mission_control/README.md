# AIOS Mission Control v1

Mission Control turns one human goal into a repo-safe development mission. It creates a mission folder with a structured plan, Codex-ready worker prompts, validation steps, merge order, and a dashboard/status file.

## Files

- `New-AiOsMissionPlan.ps1` - DRY_RUN-first mission generator.
- `Update-AiOsMissionStatusRefresh.ps1` - DRY_RUN-first local status refresher for `mission_dashboard.md`.
- `AIOS_MISSION_TEMPLATE.json` - safety and output template metadata.
- `missions/` - generated mission folders. Created only with `-Apply`.

## DRY_RUN

Preview a mission without writing files:

```powershell
powershell -ExecutionPolicy Bypass -File automation/mission_control/New-AiOsMissionPlan.ps1 -Goal "Build safe repo telemetry dashboard" -MissionName "Safe Telemetry Dashboard" -WorkerCount 4 -Preset compact
```

Expected result:

- Mode reports `DRY_RUN`.
- Planned mission folder is printed.
- No files are created.
- Next safe action asks for explicit APPLY approval.

## APPLY

Create the mission files after approval:

```powershell
powershell -ExecutionPolicy Bypass -File automation/mission_control/New-AiOsMissionPlan.ps1 -Goal "Build safe repo telemetry dashboard" -MissionName "Safe Telemetry Dashboard" -WorkerCount 4 -Preset compact -Apply
```

Generated files:

- `mission_plan.json`
- `codex_tasks.md`
- `validation_plan.md`
- `merge_order.md`
- `mission_dashboard.md`

## Mission Runner

List the next safe action for an existing mission:

```powershell
powershell -ExecutionPolicy Bypass -File automation/mission_control/Get-AiOsMissionNextAction.ps1 -MissionPath automation/mission_control/missions/improve-aios-runtime-automation
```

Show the copy/paste prompt for `MC-01`:

```powershell
powershell -ExecutionPolicy Bypass -File automation/mission_control/Get-AiOsMissionNextAction.ps1 -MissionPath automation/mission_control/missions/improve-aios-runtime-automation -TaskId MC-01 -ShowPrompt
```

Show a specific task prompt:

```powershell
powershell -ExecutionPolicy Bypass -File automation/mission_control/Get-AiOsMissionNextAction.ps1 -MissionPath automation/mission_control/missions/improve-aios-runtime-automation -TaskId MC-03 -ShowPrompt
```

## Mission Progress Report Updater

Preview a progress report update for an opened PR:

```powershell
powershell -ExecutionPolicy Bypass -File automation/mission_control/Update-AiOsMissionProgressReport.ps1 -MissionPath automation/mission_control/missions/improve-aios-runtime-automation -TaskId MC-01 -Status PR_OPENED -PullRequest "PR #146" -ValidationResult "PASS"
```

Apply a progress report update for an opened PR:

```powershell
powershell -ExecutionPolicy Bypass -File automation/mission_control/Update-AiOsMissionProgressReport.ps1 -MissionPath automation/mission_control/missions/improve-aios-runtime-automation -TaskId MC-01 -Status PR_OPENED -PullRequest "PR #146" -ValidationResult "PASS" -Apply
```

Apply a merged update:

```powershell
powershell -ExecutionPolicy Bypass -File automation/mission_control/Update-AiOsMissionProgressReport.ps1 -MissionPath automation/mission_control/missions/improve-aios-runtime-automation -TaskId MC-01 -Status MERGED -PullRequest "PR #146" -ValidationResult "PASS" -NextSafeAction "Run the next Mission Runner task." -Apply
```

Apply a blocked update with blocker text:

```powershell
powershell -ExecutionPolicy Bypass -File automation/mission_control/Update-AiOsMissionProgressReport.ps1 -MissionPath automation/mission_control/missions/improve-aios-runtime-automation -TaskId MC-01 -Status BLOCKED -Blocker "Validation proof is missing." -NextSafeAction "Attach validation proof before APPLY." -Apply
```

## Mission Status Refresh

Preview the local Mission Control status refresh without writing files:

```powershell
powershell -ExecutionPolicy Bypass -File automation/mission_control/Update-AiOsMissionStatusRefresh.ps1 -MissionPath automation/mission_control/missions/improve-aios-runtime-automation
```

Expected result:

- Mode reports `DRY_RUN`.
- Mission, proof, git, runtime, packet, blocker, and next safe action summaries are printed.
- `mission_dashboard.md` is not changed.
- No GitHub, network, commit, push, merge, broker, secret, startup task, or scheduled task action runs.

Apply the local status refresh after approval:

```powershell
powershell -ExecutionPolicy Bypass -File automation/mission_control/Update-AiOsMissionStatusRefresh.ps1 -MissionPath automation/mission_control/missions/improve-aios-runtime-automation -Apply
```

Apply result:

- Only `automation/mission_control/missions/improve-aios-runtime-automation/mission_dashboard.md` is updated.
- `mission_plan.json` is not changed.
- No GitHub, network, commit, push, merge, broker, secret, startup task, or scheduled task action runs.

## Safety

The script is repo-scoped and file-generation only. It does not commit, push, merge, create scheduled tasks, create startup tasks, call external networks, touch secrets, call brokers, or perform trading actions.

Next safe action: run DRY_RUN first, review the planned folder and prompts, then approve APPLY only for the mission folder you expect.
