# Phase 16.2 Dispatcher Display Scripts

## Purpose

Phase 16.2 adds read-only display scripts for the AI_OS orchestration backbone.

The scripts help a beginner operator inspect the example dispatcher queue and example worker lock state without creating assignments or launching workers.

## Files Added

- `automation/orchestration/show-dispatcher-queue.ps1`
- `automation/orchestration/show-worker-status.ps1`
- `docs/AI_OS/orchestration/PHASE_16_2_DISPATCHER_DISPLAY_SCRIPTS.md`
- `Reports/checkpoints/CHECKPOINT_PHASE_16_2_DISPATCHER_DISPLAY_SCRIPTS.md`

## Script Behavior

`show-dispatcher-queue.ps1` reads:

- `automation/orchestration/packet_queue.example.json`
- `automation/orchestration/assignment_locks.example.json`

It prints packet status, assignment status, matching lock status, allowed paths, blocked paths, approval requirements, and validator requirements.

`show-worker-status.ps1` reads:

- `automation/orchestration/packet_queue.example.json`
- `automation/orchestration/assignment_locks.example.json`

It prints worker lock status, claimed or unclaimed state, collision status, matching packet status, allowed paths, blocked paths, approval requirements, and validator requirements.

## Safety Boundary

These scripts are display-only.

They do not:

- modify files
- create locks
- launch workers
- edit dashboard files
- connect to a broker
- connect to OANDA
- use API keys
- place orders
- enable live trading
- commit
- push

## Validation

Run:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/show-dispatcher-queue.ps1
pwsh -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/show-worker-status.ps1
git status --short --branch
```

Expected result:

- Both scripts print beginner-readable status.
- Both scripts complete without creating files or locks.
- Git status shows only the approved Phase 16.2 files as uncommitted changes.

## Next Safe Action

Review the display output and checkpoint, then decide whether to approve a separate selective commit prompt.
