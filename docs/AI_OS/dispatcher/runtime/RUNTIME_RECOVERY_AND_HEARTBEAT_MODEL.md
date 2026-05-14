# Runtime Recovery And Heartbeat Model

Heartbeats show whether a worker appears active.

Recovery decides how to resume when state is stale, failed, unclear, or interrupted.

## Heartbeat Source Of Truth

Heartbeat current state belongs in:

`Reports/dispatcher/runtime/heartbeats/worker_heartbeat_table.json`

## Recovery Source Of Truth

Recovery decisions belong in:

`Reports/dispatcher/runtime/recovery/recovery_runtime_ledger.json`

Recovery summary belongs in:

`Reports/dispatcher/runtime/recovery/recovery_runtime_status.json`

## Heartbeat Rules

A current heartbeat means the worker may still be active.

A stale heartbeat does not mean the worker's work is safe to replace.

A missing heartbeat for an assigned worker becomes `REVIEW_REQUIRED`.

## Recovery Behavior

On resume, the recovery reconciler should check:

- active packets
- active locks
- active workers
- stale heartbeats
- pending approvals
- failed packets
- dirty repo state
- untracked files

## Recovery Actions

Safe automated actions:

- read current state
- write summaries
- mark unclear state `REVIEW_REQUIRED`
- recommend the next safe action

Human approval required:

- resume APPLY
- override stale lock
- reassign stale worker
- prepare commit package
- stage, commit, or push

