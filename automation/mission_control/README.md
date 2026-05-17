# AIOS Mission Control v1

Mission Control turns one human goal into a repo-safe development mission. It creates a mission folder with a structured plan, Codex-ready worker prompts, validation steps, merge order, and a dashboard/status file.

## Files

- `New-AiOsMissionPlan.ps1` - DRY_RUN-first mission generator.
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

## Safety

The script is repo-scoped and file-generation only. It does not commit, push, merge, create scheduled tasks, create startup tasks, call external networks, touch secrets, call brokers, or perform trading actions.

Next safe action: run DRY_RUN first, review the planned folder and prompts, then approve APPLY only for the mission folder you expect.
