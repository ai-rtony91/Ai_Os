# Checkpoint: Phase 16.71-80 Supervisor Simple Mode

## Task

Make the active supervisor dashboard default to simple mode and move full details behind `-Detailed`.

## Files Changed

- `automation/orchestration/supervisor/Show-AiOsSupervisorDashboard.ps1`
- `automation/orchestration/supervisor/README_AIOS_ACTIVE_SUPERVISION.md`
- `docs/AI_OS/orchestration/PHASE_16_71_80_SUPERVISOR_SIMPLE_MODE.md`
- `Reports/checkpoints/CHECKPOINT_PHASE_16_71_80_SUPERVISOR_SIMPLE_MODE.md`

## Safety Rules

- No dashboard edits.
- No protected root edits.
- No broker, OANDA, API, webhook, or live trading work.
- No startup tasks.
- No scheduled tasks.
- No Codex auto-launch.
- No commit.
- No push.

## Validation Plan

```powershell
powershell -NoProfile -Command "[scriptblock]::Create((Get-Content -Raw -Path 'automation/orchestration/supervisor/Show-AiOsSupervisorDashboard.ps1')) | Out-Null"
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/supervisor/Show-AiOsSupervisorDashboard.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/supervisor/Show-AiOsSupervisorDashboard.ps1 -Detailed
git diff --check
git status --short --branch
```

## Next Safe Action

Run simple mode first. Use `-Detailed` only when the operator needs the full repo, GitHub, validation, stale, and blocked-action breakdown.
