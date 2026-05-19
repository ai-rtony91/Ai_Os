# Phase 16.13 Orchestration Control Layer

## Purpose

Phase 16.13 designs the first active orchestration control layer for AI_OS while keeping implementation display-only.

This upgrades the orchestration model from example ledgers and display scripts toward basic coordination control logic.

## Files Added

- `automation/orchestration/assignment_lock_controller.v1.example.json`
- `automation/orchestration/orchestration_control_state.v1.example.json`
- `automation/orchestration/show-assignment-lock-controller.ps1`
- `automation/orchestration/show-orchestration-control-state.ps1`
- `docs/AI_OS/orchestration/PHASE_16_13_ORCHESTRATION_CONTROL_LAYER.md`
- `Reports/checkpoints/CHECKPOINT_PHASE_16_13_ORCHESTRATION_CONTROL_LAYER.md`

## Design Scope

This phase covers:

- assignment lock controller
- worker heartbeat tracking
- queue health display
- validator routing preparation
- orchestration telemetry expansion
- PR workflow integration

## Control Model

The control layer is a read-only model of active coordination.

It can show:

- duplicate packet ownership
- packet conflicts
- stale lock visibility
- lock release rules
- worker heartbeat states
- stale and inactive workers
- queue pressure
- blocked assignments
- validation backlog
- PR-required packet states

It cannot change those states.

## Script Behavior

`show-assignment-lock-controller.ps1` reads:

- `automation/orchestration/assignment_lock_controller.v1.example.json`

It prints duplicate ownership, packet conflicts, stale locks, release rules, and blocked actions.

`show-orchestration-control-state.ps1` reads:

- `automation/orchestration/orchestration_control_state.v1.example.json`

It prints worker heartbeat status, queue health, validator routing preparation, telemetry counters, PR workflow state, and blocked actions.

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
- run validators
- create or release locks
- commit
- push

## Validation

Run:

```powershell
powershell -NoProfile -Command "Get-Content -Raw -Path 'automation/orchestration/assignment_lock_controller.v1.example.json' | ConvertFrom-Json | Out-Null"
powershell -NoProfile -Command "Get-Content -Raw -Path 'automation/orchestration/orchestration_control_state.v1.example.json' | ConvertFrom-Json | Out-Null"
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/show-assignment-lock-controller.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/show-orchestration-control-state.ps1
git diff --check
git status --short --branch
```

Expected result:

- JSON files parse.
- Display scripts print lock controller and control state status.
- Display scripts modify nothing and launch nothing.
- Git status shows only approved Phase 16.13 files unless unrelated changes exist.

## Next Safe Action

Review both displays and the checkpoint, then decide whether to approve a separate selective commit prompt.
