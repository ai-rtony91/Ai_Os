# Live Worker Heartbeat State

This document defines the first live worker runtime state files for AI_OS worker supervision.

The files are local-first runtime state. They do not contain secrets, API keys, startup tasks, scheduled tasks, auto-launch logic, APPLY automation, commit logic, or push logic.

## Live State Files

Current worker state:

`Reports/dispatcher/runtime/workers/active_worker_table.json`

Current heartbeat state:

`Reports/dispatcher/runtime/workers/worker_heartbeat_table.json`

Session history:

`Reports/dispatcher/runtime/workers/worker_session_ledger.json`

Registration state:

`Reports/dispatcher/runtime/workers/worker_registration_status.json`

## Initial Worker Slots

The live state starts with ten worker slots:

- `AIOS-01`
- `AIOS-02`
- `AIOS-03`
- `AIOS-04`
- `AIOS-05`
- `AIOS-06`
- `AIOS-07`
- `AIOS-08`
- `AIOS-09`
- `AIOS-10`

## Initial State Rules

- `heartbeat_time` may be null before a live heartbeat exists.
- `stale_status` starts as `REVIEW_REQUIRED`.
- Workers remain `REVIEW_REQUIRED` until live heartbeat and registration checks exist.
- A stale worker does not mean safe to replace.
- Human approval is required before reassignment.
- No worker launch, APPLY, commit, push, startup task, or scheduled task is triggered by these files.

## Next Safe Action

Register live worker heartbeats before assigning packets, claiming locks, or starting APPLY work.

