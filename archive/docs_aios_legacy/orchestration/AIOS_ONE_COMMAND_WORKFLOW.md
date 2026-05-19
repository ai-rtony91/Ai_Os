# AI_OS One Command Workflow

`Start-AiOsWork.ps1` is the primary operator entrypoint for daily AI_OS work.

It consolidates status, validation, work packets, routing, Daily Start, worker profile resolution, guard checks, and later save/PR preview into one operator-friendly report.

## Command

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Start-AiOsWork.ps1 -Intent "choose next AI_OS work"
```

## Parameters

- `-Intent`
- `-MaxTabs 3`
- `-LaunchManualShells`
- `-Apply`

Preview is default. `-LaunchManualShells` is explicit and still routes through the existing Daily Start launch path. `-Apply` is reserved for approved non-destructive state updates; the current workflow does not mutate state.

## What It Runs

- `git status --short --branch`
- `Test-AiOsWorkspaceBootstrap.DRY_RUN.ps1`
- `Get-AiOsWorkPacketState.ps1`
- `Route-AiOsWorkPacket.DRY_RUN.ps1`
- `Start-AiOsDay.ps1`
- `Resolve-AiOsNeededWorkers.DRY_RUN.ps1`

## Output

The workflow prints:

- `WHERE TO RUN NEXT`
- visible tab/window
- path
- branch
- worker
- packet
- validator
- guard check
- exact Codex prompt when Codex work is needed
- exact save command for later save/PR preview

## Safety Rules

- No commits.
- No pushes.
- No PR creation.
- No merge.
- No Codex auto-launch.
- No scheduled/startup tasks.
- No broker/API/live trading.
- No destructive actions.
- Do not open all workers.
- Do not create new worktrees unless explicitly approved.

## Next Safe Action

WHERE: visible tab/window `SAVE · git`

Path: repo root

Run:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Start-AiOsWork.ps1 -Intent "choose next AI_OS work"
```
