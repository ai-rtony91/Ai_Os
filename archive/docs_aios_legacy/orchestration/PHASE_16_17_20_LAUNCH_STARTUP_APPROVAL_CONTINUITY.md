# Phase 16.17-20 Launch Startup Approval Continuity

## Purpose

Phase 16.17-20 designs the first orchestration startup and continuity management layer for AI_OS.

The layer moves AI_OS from manual startup and temporary orchestration toward structured orchestration continuity while remaining display-only.

## Files Added

- `automation/orchestration/launch_supervisor.v1.example.json`
- `automation/orchestration/startup_orchestration.v1.example.json`
- `automation/orchestration/approval_inbox.v1.example.json`
- `automation/orchestration/session_continuity.v1.example.json`
- `automation/orchestration/show-launch-supervisor.ps1`
- `automation/orchestration/show-startup-orchestration.ps1`
- `automation/orchestration/show-approval-inbox-v1.ps1`
- `automation/orchestration/show-session-continuity.ps1`
- `docs/AI_OS/orchestration/PHASE_16_17_20_LAUNCH_STARTUP_APPROVAL_CONTINUITY.md`
- `Reports/checkpoints/CHECKPOINT_PHASE_16_17_20_LAUNCH_STARTUP_APPROVAL_CONTINUITY.md`

## Design Scope

This phase covers:

- launch supervisor
- startup orchestration
- approval inbox
- session continuity
- recovery-safe startup
- read-only display scripts

## Safety Boundary

This phase is display-only.

It does not:

- edit dashboard files
- edit protected root files
- connect to a broker
- connect to OANDA
- use API keys
- call webhooks
- place orders
- enable live trading
- create scheduled tasks
- create startup tasks
- launch workers
- launch packets
- approve packets
- run validators
- merge pull requests
- restore sessions
- restore queue state
- switch branches
- commit
- push

## Validation

Run:

```powershell
powershell -NoProfile -Command "Get-Content -Raw -Path 'automation/orchestration/launch_supervisor.v1.example.json' | ConvertFrom-Json | Out-Null"
powershell -NoProfile -Command "Get-Content -Raw -Path 'automation/orchestration/startup_orchestration.v1.example.json' | ConvertFrom-Json | Out-Null"
powershell -NoProfile -Command "Get-Content -Raw -Path 'automation/orchestration/approval_inbox.v1.example.json' | ConvertFrom-Json | Out-Null"
powershell -NoProfile -Command "Get-Content -Raw -Path 'automation/orchestration/session_continuity.v1.example.json' | ConvertFrom-Json | Out-Null"
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/show-launch-supervisor.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/show-startup-orchestration.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/show-approval-inbox-v1.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/show-session-continuity.ps1
git diff --check
git status --short --branch
```

Expected result:

- JSON files parse.
- Display scripts print launch, startup, approval, and continuity status.
- Display scripts modify nothing and launch nothing.
- Git status shows only approved Phase 16.17-20 files unless unrelated changes exist.

## Next Safe Action

Review all four displays and the checkpoint, then decide whether to approve a separate selective commit prompt.
