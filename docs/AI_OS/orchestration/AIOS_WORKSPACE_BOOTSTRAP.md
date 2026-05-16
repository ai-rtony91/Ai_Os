# AI_OS Workspace Bootstrap

Issue #60 creates a preview-first workspace bootstrap and lane recovery system.

The source of truth for lane role, path, branch, and restart command is:

```text
automation/orchestration/terminal_workstations/AIOS_WORKTREE_LANE_REGISTRY.json
```

## Safety Rules

- Preview mode is the default.
- No Codex auto-launch.
- No scheduled tasks.
- No startup tasks.
- No broker, API, webhook, real order, or live trading integration.
- No destructive action.
- No commit or push from bootstrap scripts.
- `git worktree list` is printed during bootstrap, lane open, save, restore, and validation.

## Files

- `automation/orchestration/bootstrap/Start-AiOsWorkspace.ps1`
- `automation/orchestration/bootstrap/Open-AiOsLane.ps1`
- `automation/orchestration/bootstrap/Save-AiOsSession.ps1`
- `automation/orchestration/bootstrap/Restore-AiOsSession.ps1`
- `automation/orchestration/bootstrap/Test-AiOsWorkspaceBootstrap.DRY_RUN.ps1`
- `automation/orchestration/terminal_workstations/AIOS_SESSION_STATE.example.json`

## Preview Workspace

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Start-AiOsWorkspace.ps1
```

Expected result:

- Prints safety rules.
- Runs `git worktree list`.
- Prints each lane role, path, branch, and restart command.
- Prints session save and restore commands.
- Opens no windows.

## Open Workspace Lanes

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Start-AiOsWorkspace.ps1 -OpenLanes
```

Expected result:

- Opens manual PowerShell lane shells only.
- Does not launch Codex.
- Does not create scheduled or startup tasks.

## Preview One Lane

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Open-AiOsLane.ps1 -LaneId validation
```

Expected result:

- Prints the selected lane role, path, branch, and restart command.
- Opens no window unless `-Open` is passed.

## Save Session

Preview only:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Save-AiOsSession.ps1
```

Write a new local session file only when approved:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Save-AiOsSession.ps1 -Apply
```

The save script refuses to overwrite an existing session state file.

## Restore Session

Preview only:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Restore-AiOsSession.ps1
```

Open manual lane shells only when approved:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Restore-AiOsSession.ps1 -OpenLanes
```

If no local session state exists, restore preview reads `AIOS_SESSION_STATE.example.json`.

## DRY_RUN Validator

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Test-AiOsWorkspaceBootstrap.DRY_RUN.ps1
```

The validator checks:

- Required files exist.
- PowerShell files parse.
- JSON files parse.
- Lane registry has lane role, path, branch, and restart command.
- `git worktree list` runs.
- Workspace bootstrap preview runs without opening windows.

## Next Safe Action

Run the DRY_RUN validator before opening lanes:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Test-AiOsWorkspaceBootstrap.DRY_RUN.ps1
```
