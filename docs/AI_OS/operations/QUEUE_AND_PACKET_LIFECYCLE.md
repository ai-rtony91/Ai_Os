# Queue And Packet Lifecycle

Status: CURRENT
Mode: Operations documentation

## Purpose

This document explains how AI_OS queue and packet movement should be understood by MAIN CONTROL.

There are two visible queue models:

- operator queue: `automation/orchestration/queue/DISPATCHER_QUEUE.json`
- runtime/telemetry packet state: `telemetry/work_ledger.jsonl` replayed by `services/dispatcher` and `services/telemetry`

Treat both as evidence. When they conflict, mark the state `REVIEW_REQUIRED`.

## Operator Queue

The operator queue is inspected with:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\control\Get-AiOsAutomationQueue.ps1
```

It reports:

- queue status
- item count
- status counts
- packet IDs
- priorities
- assigned workers
- titles

## Runtime Packet Flow

The dispatcher service model uses these packet statuses:

- `queued`
- `dry_run`
- `waiting_approval`
- `approved`
- `applied`
- `blocked`

High-risk packets and packets marked `requiresApproval` route to approval before APPLY-style movement.

## Queue Lifecycle

1. Packet enters queue.
2. Dispatcher or operator marks the packet ready for DRY_RUN.
3. Worker lane inspects and reports.
4. Approval is requested when required.
5. MAIN CONTROL reviews approval evidence.
6. Approved packet proceeds only within exact scope.
7. Validators run.
8. Packet is completed, blocked, or returned for review.

## Approval Boundary

Approval is required before:

- APPLY
- protected path changes
- runtime recovery resume
- lock release
- packet reassignment
- staging
- commit
- push
- PR creation
- merge

## Queue Review Rules

Use `REVIEW_REQUIRED` when:

- queue status and packet status disagree
- assigned worker is unknown
- lane is unregistered
- packet has no validator
- packet has no next action
- packet points at protected paths
- approval evidence is missing
- packet history is incomplete

## Do Not Mutate Queue Automatically

Do not automatically:

- reassign stale packets
- release locks
- retry failed packets
- advance approval state
- mark work complete
- delete queue items
- move packet files

These are MAIN CONTROL decisions.

## Next Safe Action

Read the queue, compare with runtime health and telemetry replay, then assign only one exact next action.
