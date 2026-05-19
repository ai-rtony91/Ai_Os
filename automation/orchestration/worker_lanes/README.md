# AI_OS Worker Lane Status DRY_RUN

This folder contains a read-only worker lane status checker.

Purpose:

- Show which worker lane appears active.
- Show current branch and git clean or dirty status.
- Show untracked files.
- Give beginner-readable lane status and next safe action.
- Warn when more than one lane has dirty-file evidence.

Covered lanes:

- `CODEX_01`
- `CODEX_02`
- `CLAUDE_01`
- `MAIN_CONTROL`

Safety rules:

- DRY_RUN only.
- No commits.
- No pushes.
- No runtime edits.
- No dispatcher edits.
- No schema edits.
- No edits outside this folder.

Example commands:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\worker_lanes\Get-AiOsWorkerLaneStatus.DRY_RUN.ps1
```

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\worker_lanes\Get-AiOsWorkerLaneStatus.DRY_RUN.ps1 -OutputJson
```

Next safe action: run the checker before assigning work to a lane or before asking a worker to APPLY changes.
