# Phase 16.12 Worker Registry + Packet Queue

## Purpose

Phase 16.12 adds v1 example ledgers and read-only displays for worker registry, packet queue, and assignment locking.

The goal is to make worker-to-packet state beginner-readable before any real assignment or launch workflow exists.

## Files Added

- `automation/orchestration/worker_registry.v1.example.json`
- `automation/orchestration/packet_queue_ledger.v1.example.json`
- `automation/orchestration/assignment_locks.v1.example.json`
- `automation/orchestration/show-packet-queue-ledger.ps1`
- `automation/orchestration/show-worker-registry-v1.ps1`
- `docs/AI_OS/orchestration/PHASE_16_12_WORKER_REGISTRY_PACKET_QUEUE.md`
- `Reports/checkpoints/CHECKPOINT_PHASE_16_12_WORKER_REGISTRY_PACKET_QUEUE.md`

## Design Scope

This phase covers:

- worker registry
- packet queue ledger
- assignment locking
- queue display script
- worker registry display script
- validation plan
- safety rules

## Script Behavior

`show-packet-queue-ledger.ps1` reads:

- `automation/orchestration/packet_queue_ledger.v1.example.json`
- `automation/orchestration/assignment_locks.v1.example.json`

It prints packet status, assigned worker, lock status, collision status, approval requirement, validator requirement, allowed paths, and blocked paths.

`show-worker-registry-v1.ps1` reads:

- `automation/orchestration/worker_registry.v1.example.json`
- `automation/orchestration/packet_queue_ledger.v1.example.json`
- `automation/orchestration/assignment_locks.v1.example.json`

It prints worker status, assigned packet, matching packet status, matching lock status, missing packet assignments, stale lock assignments, allowed paths, and blocked paths.

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
- create real assignment locks
- modify queue records
- commit
- push

## Validation

Run:

```powershell
powershell -NoProfile -Command "Get-Content -Raw -Path 'automation/orchestration/worker_registry.v1.example.json' | ConvertFrom-Json | Out-Null"
powershell -NoProfile -Command "Get-Content -Raw -Path 'automation/orchestration/packet_queue_ledger.v1.example.json' | ConvertFrom-Json | Out-Null"
powershell -NoProfile -Command "Get-Content -Raw -Path 'automation/orchestration/assignment_locks.v1.example.json' | ConvertFrom-Json | Out-Null"
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/show-packet-queue-ledger.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/show-worker-registry-v1.ps1
git diff --check
git status --short --branch
```

Expected result:

- JSON files parse.
- Display scripts print queue and worker registry status.
- Display scripts modify nothing and launch nothing.
- Git status shows only approved Phase 16.12 files unless unrelated changes exist.

## Next Safe Action

Review both displays and the checkpoint, then decide whether to approve a separate selective commit prompt.
