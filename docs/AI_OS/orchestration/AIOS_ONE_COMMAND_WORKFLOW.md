# AI_OS One Command Workflow

`Start-AiOsWork.ps1` is the primary operator entrypoint for daily AI_OS work.

It consolidates status, validation, work packets, routing, Daily Start, worker profile resolution, guard checks, PR/branch awareness, freshness checks, and later save/PR preview into one operator-friendly report.

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

Optional connectors are checked before command recommendations. If guard, save automation, or worker profile scripts are missing, the cockpit prints a warning and continues preview-only when core safety can still be checked.

## Output

The workflow prints these short sections:

- `STATUS`
- `PACKETS`
- `WORKER`
- `GUARD`
- `NEXT COMMAND`
- `STOP CONDITION`

It includes visible tab/window, path, branch, worker, packet, validator, guard check, exact Codex prompt when Codex work is needed, and exact save command for later save/PR preview.

## Gap Handling

- Main freshness: checks local `main` versus `origin/main` and prints the exact pull command when behind.
- Missing scripts: prints `STOP` for missing core scripts before recommending commands.
- No active packet: reports `No active packet.` and suggests creating a packet, continuing brainstem maintenance, or cleanup.
- Packet mismatch: reports folder/status mismatches and prints a repair suggestion only.
- Guard: prints the guard command when available, otherwise `Guard unavailable`.
- Save: prefers `Submit-AiOsWork.ps1 -Preview`; if missing, prints fallback manual git commands.
- PR awareness: checks `gh pr view` when `gh` is available and prints the PR URL or merged cleanup note.
- Cleanup: suggests cleanup only; no branch or worktree deletion is performed.

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

Progress note scripts are intentionally deferred. The cockpit remains a lightweight orchestrator instead of adding another file-based subsystem in this patch.

## Next Safe Action

WHERE: visible tab/window `SAVE · git`

Path: repo root

Run:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Start-AiOsWork.ps1 -Intent "choose next AI_OS work"
```
