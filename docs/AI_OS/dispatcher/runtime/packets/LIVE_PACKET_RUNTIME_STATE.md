# Live Packet Runtime State

## Purpose

This document defines the first live local packet runtime state for AI_OS.

The live packet runtime moves dispatcher packet tracking from example JSON into local state files that can later support controlled assignment, ownership, validation, approval review, and recovery.

## Scope

Allowed live packet runtime files:

- `Reports/dispatcher/runtime/packets/packet_queue.json`
- `Reports/dispatcher/runtime/packets/packet_runtime_table.json`
- `Reports/dispatcher/runtime/packets/packet_assignment_ledger.json`
- `Reports/dispatcher/runtime/packets/packet_status_history.json`

These files are local-first runtime state. They do not assign workers automatically, approve APPLY work, stage files, commit, push, connect to brokers, use OANDA, collect API keys, or enable live trading.

## Source Of Truth

`packet_runtime_table.json` is the packet runtime source of truth after a packet exists.

`packet_queue.json` is intake and queue state.

`packet_assignment_ledger.json` records assignment decisions after a human operator binds one queued packet to one idle worker.

`packet_status_history.json` records every packet status transition.

## Required Safety Defaults

Every new packet starts with:

- `status`: `QUEUED`
- `mode`: `DRY_RUN`
- `approval_required`: `true`
- `apply_allowed`: `false`
- `worker_id`: `null`
- `assigned_worker_id`: `null`
- `lock_ids`: `[]`

## Packet Assignment Boundary

Packet assignment is manual until a future approved packet creates validator-backed assignment tooling.

A packet may be assigned only when:

- the packet status is `QUEUED`
- the worker has no active packet
- allowed paths are narrow
- blocked paths are present
- lock conflicts are absent
- APPLY remains blocked
- human approval has not been bypassed

## Status Rules

Initial DRY_RUN flow:

1. `QUEUED`
2. `ASSIGNED`
3. `DRY_RUN_STARTED`
4. `DRY_RUN_COMPLETE`
5. `APPROVAL_REQUIRED`

Future APPLY flow:

1. `APPROVAL_REQUIRED`
2. `APPLY_APPROVED`
3. `APPLY_RUNNING`
4. `APPLY_COMPLETE`
5. `VALIDATED`

Unsafe, stale, conflicting, or unknown state becomes `REVIEW_REQUIRED`.

Known blocked work becomes `BLOCKED`.

Validation failure becomes `FAILED`.

## Packet To Worker Binding

Packet-to-worker binding is official only when both packet state and worker state agree on:

- `packet_id`
- `worker_id`
- `window_id`
- packet status
- assignment time
- next safe action

If packet state and worker state disagree, the packet must become `REVIEW_REQUIRED`.

## Packet To Lock Binding

DRY_RUN packets may inspect allowed paths without edit locks.

APPLY work requires lock IDs before edits begin.

Lock IDs stay empty until claimed:

```json
"lock_ids": []
```

Future lock binding must confirm every claimed path is inside packet `allowed_paths` and outside packet `blocked_paths`.

## Operator Check Integration

Future operator checks should read live packet state before example files.

Recommended read order:

1. `Reports/dispatcher/runtime/packets/packet_runtime_table.json`
2. `Reports/dispatcher/runtime/packets/packet_queue.json`
3. `Reports/dispatcher/runtime/packets/packet_assignment_ledger.json`
4. `Reports/dispatcher/runtime/packets/packet_status_history.json`

If any live packet JSON is invalid, missing required fields, or conflicts with worker or lock state, the operator check should report `REVIEW_REQUIRED`.

## Next Safe Action

Run the packet JSON parse validation, then review operator check output before approving any future packet assignment or APPLY automation.
