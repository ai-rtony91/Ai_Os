# AI_OS Mission Control

Mission Control is the unified read-only operations layer for AI_OS.

It connects launcher, supervisor, routing, validation, repo risk, queue awareness, recovery awareness, telemetry readiness, and dashboard-ready state without changing the repo.

## Commands

Simple mission status:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/mission_control/Start-AiOsMissionControl.ps1
```

Detailed mission status:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/mission_control/Show-AiOsMissionStatus.ps1 -Detailed
```

JSON mission state:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/mission_control/Export-AiOsMissionState.ps1
```

## Simple View

Mission Control shows:

- risk
- recommended lane
- exact next safe action
- one short reason
- current repo state
- current GitHub state

## Detailed View

Detailed mode adds validation state, routing state, stale state, approval state, queue awareness, recovery awareness, blocked state, telemetry readiness, and dashboard readiness.

## Safety

Mission Control is read-only. It does not commit, push, merge, create branches, create issues, create PRs, edit dashboards, create startup tasks, create scheduled tasks, auto-launch Codex, or touch broker/OANDA/API/webhook/live trading.
