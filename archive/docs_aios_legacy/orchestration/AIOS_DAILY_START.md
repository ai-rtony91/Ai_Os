# AI_OS Daily Start

Daily Start is the preview-first route for the AI_OS brainstem:

- Rulebook: durable operator rules.
- Intent Router: maps today's goal to locked lane IDs.
- Supervisor: previews one-worker assignments, validators, approvals, and next action.
- Worker Profiles: map packets and intent to standing worker IDs, paths, branches, guard checks, and later save/PR commands.

## Command

WHERE: visible tab/window `SAVE · git`

Path: repo root

Run:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Start-AiOsDay.ps1 -Intent "complete brainstem daily start route" -MaxTabs 3
```

For the full daily operator flow, prefer:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Start-AiOsWork.ps1 -Intent "choose next AI_OS work"
```

## Behavior

- Preview is default.
- `-Intent` accepts today's goal.
- `-MaxTabs 3` limits manual tab launch count.
- `-LaunchManualShells` is optional and opens Windows Terminal tabs only.
- No Codex auto-launch.
- No commit or push.
- No scheduled/startup tasks.
- No broker/API/live trading.

## Output

Daily Start prints:

- CONTROL git status.
- Workspace intent route.
- Supervisor assignment preview.
- Work packet summary.
- Worker profile resolution.
- Primary worker recommendation.
- Guard check recommendation.
- Later save/PR automation command.
- Suggested lanes.
- Suggested validators.
- `WHERE TO RUN NEXT`.

## Launch Rule

Only use launch after preview confirms the lane, path, branch, and validator route:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Start-AiOsDay.ps1 -Intent "complete brainstem daily start route" -MaxTabs 3 -LaunchManualShells
```

The launch path still opens shell tabs only. It prints manual Codex commands but does not start Codex.

## Next Safe Action

WHERE: visible tab/window `SAVE · git`

Path: repo root

Run:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Test-AiOsWorkspaceBootstrap.DRY_RUN.ps1
```
