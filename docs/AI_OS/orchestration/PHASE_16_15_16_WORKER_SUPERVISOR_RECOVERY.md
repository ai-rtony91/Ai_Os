# Phase 16.15-16 Persistent Worker Supervisor + Recovery Bootstrap

## Purpose

Phase 16.15-16 designs the first persistent worker supervision and orchestration recovery layer for AI_OS.

The layer moves AI_OS from temporary orchestration state toward persistent orchestration awareness while remaining display-only.

## Files Added

- `automation/orchestration/persistent_worker_supervisor.v1.example.json`
- `automation/orchestration/recovery_bootstrap_supervisor.v1.example.json`
- `automation/orchestration/show-persistent-worker-supervisor.ps1`
- `automation/orchestration/show-recovery-bootstrap-supervisor.ps1`
- `docs/AI_OS/orchestration/PHASE_16_15_16_WORKER_SUPERVISOR_RECOVERY.md`
- `Reports/checkpoints/CHECKPOINT_PHASE_16_15_16_WORKER_SUPERVISOR_RECOVERY.md`

## Design Scope

This phase covers:

- persistent worker supervisor
- recovery bootstrap supervisor
- recovery telemetry
- read-only worker supervisor display
- read-only recovery bootstrap display
- orchestration continuity model

## Worker Supervision Model

The worker supervisor tracks:

- worker IDs
- worker roles
- worker health
- heartbeat timestamps
- stale worker visibility
- inactive worker visibility
- assigned packet visibility
- worker branch visibility

It does not update heartbeats, assign packets, switch branches, or launch workers.

## Recovery Bootstrap Model

The recovery bootstrap supervisor tracks:

- active branch visibility
- queue restore visibility
- worker restore visibility
- packet restore visibility
- recovery checkpoints
- orchestration continuity state

It does not restore queue state, restart workers, reassign packets, or modify git state.

## Telemetry Model

Recovery telemetry tracks example counts for:

- active workers
- stale workers
- inactive workers
- recovery checkpoints
- restore backlog
- interrupted sessions
- queue restore state
- worker restore count
- packet restore count

Telemetry is local-only and display-only.

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
- restore queue state
- reassign packets
- update heartbeats
- modify git state
- commit
- push

## Validation

Run:

```powershell
powershell -NoProfile -Command "Get-Content -Raw -Path 'automation/orchestration/persistent_worker_supervisor.v1.example.json' | ConvertFrom-Json | Out-Null"
powershell -NoProfile -Command "Get-Content -Raw -Path 'automation/orchestration/recovery_bootstrap_supervisor.v1.example.json' | ConvertFrom-Json | Out-Null"
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/show-persistent-worker-supervisor.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/show-recovery-bootstrap-supervisor.ps1
git diff --check
git status --short --branch
```

Expected result:

- JSON files parse.
- Display scripts print worker supervision and recovery bootstrap visibility.
- Display scripts modify nothing and launch nothing.
- Git status shows only approved Phase 16.15-16 files unless unrelated changes exist.

## Next Safe Action

Review both displays and the checkpoint, then decide whether to approve a separate selective commit prompt.
