# AI_OS Worktree Lanes

This document records the manual AI_OS worktree lane layout used to restore operator windows across sessions.

## Safety Boundary

- No Codex auto-launch.
- No startup tasks.
- No scheduled tasks.
- No windows open automatically in default mode.
- No commits or pushes.
- No broker, OANDA, API, webhook, or live trading behavior.

## Registry

The canonical lane registry is:

```text
automation/orchestration/terminal_workstations/AIOS_WORKTREE_LANE_REGISTRY.json
```

## Lanes

| ID | Name | Role | Path | Branch | Codex |
| --- | --- | --- | --- | --- | --- |
| `main_control` | AI_OS MAIN CONTROL | repo control, orchestration, merges, launcher, supervisor | `C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN` | `main` | false |
| `build_engine_git` | AI_OS BUILD ENGINE GIT | git commands, validators, staging, commits | `C:\Users\mylab\OneDrive\GitHub\aios-worker-mission-json` | `phase-221-260-mission-json-dashboard-ready` | false |
| `build_engine_codex` | AI_OS BUILD ENGINE CODEX | APPLY work, planning, code edits, architecture work | `C:\Users\mylab\OneDrive\GitHub\aios-worker-mission-json` | `phase-221-260-mission-json-dashboard-ready` | manual only |
| `validation` | AI_OS VALIDATION | read-only audits, validators, cleanup reports | `C:\Users\mylab\OneDrive\GitHub\aios-worker-validation` | `phase-validation-cleanup` | manual only |

## Print Registry

Default mode is read-only and prints the registry plus `git worktree list`:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\terminal_workstations\Show-AiOsWorktreeLaneRegistry.ps1
```

## Manual Shell Restore

Only use this when you intentionally want PowerShell windows opened:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\terminal_workstations\Show-AiOsWorktreeLaneRegistry.ps1 -LaunchManualShells
```

This opens PowerShell shells only. It does not launch Codex.
