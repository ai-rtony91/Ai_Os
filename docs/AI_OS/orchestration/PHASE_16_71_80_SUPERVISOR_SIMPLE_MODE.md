# Phase 16.71-80 Supervisor Simple Mode

## Purpose

This phase makes the AI_OS active supervisor less overwhelming.

The default dashboard output is now simple. Detailed sections remain available with `-Detailed`.

## Behavior

Default mode shows:

- risk level
- recommended lane
- exact next safe action
- one short reason

Detailed mode shows:

- repo state
- GitHub state
- validation routing
- stale and approval routing
- blocked actions
- blocked files when visible

## Commands

Simple mode:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/supervisor/Show-AiOsSupervisorDashboard.ps1
```

Detailed mode:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/supervisor/Show-AiOsSupervisorDashboard.ps1 -Detailed
```

## Safety

This remains a read-only supervisor display. It does not commit, push, merge, create branches, create issues, create PRs, edit dashboard files, edit protected root files, create startup tasks, create scheduled tasks, auto-launch Codex, or touch broker/OANDA/API/webhook/live trading work.

## Validation

```powershell
powershell -NoProfile -Command "[scriptblock]::Create((Get-Content -Raw -Path 'automation/orchestration/supervisor/Show-AiOsSupervisorDashboard.ps1')) | Out-Null"
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/supervisor/Show-AiOsSupervisorDashboard.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/supervisor/Show-AiOsSupervisorDashboard.ps1 -Detailed
git diff --check
git status --short --branch
```
