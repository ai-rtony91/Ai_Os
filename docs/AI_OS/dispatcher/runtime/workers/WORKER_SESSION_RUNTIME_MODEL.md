# Worker Session Runtime Model

The worker-session runtime tracks Codex worker windows after launch.

It does not launch workers by itself in this phase. It defines the session records that future runtime tools and dashboard summaries can read.

## Source Of Truth

Current worker state belongs in:

`Reports/dispatcher/runtime/workers/active_worker_table.json`

Session history belongs in:

`Reports/dispatcher/runtime/workers/worker_session_ledger.json`

Do not create competing active worker tables.

## Required Worker Fields

| Field | Purpose |
| --- | --- |
| `worker_id` | Stable worker identity, such as `AIOS-07`. |
| `worker_label` | Human-readable label for the worker window. |
| `launch_session_id` | Unique launch session connected to this worker. |
| `assigned_role` | Runtime responsibility assigned to the worker. |
| `assigned_packet_id` | Packet currently assigned to the worker, or null. |
| `current_state` | Current worker runtime state. |
| `launch_time` | Time the worker session was launched. |
| `heartbeat_time` | Last heartbeat timestamp. |
| `heartbeat_age_seconds` | Computed heartbeat age. |
| `claimed_paths` | Paths the worker currently owns through locks. |
| `lock_ids` | Lock records connected to the worker. |
| `approval_state` | Current APPLY approval state. |
| `validator_state` | Latest validator state connected to this worker. |
| `terminal_window_name` | Visible terminal title for operator matching. |
| `next_safe_action` | Beginner-readable next action. |

## Required Worker States

- `IDLE`
- `ASSIGNED`
- `DRY_RUN_STARTED`
- `DRY_RUN_COMPLETE`
- `WAITING_APPROVAL`
- `APPLY_RUNNING`
- `VALIDATING`
- `VALIDATED`
- `STALE`
- `BLOCKED`
- `FAILED`
- `REVIEW_REQUIRED`
- `STOPPED`

## Runtime Rules

- A worker may have one active packet.
- A worker must not run APPLY without human approval.
- A worker must not commit or push.
- A stale worker must not be automatically replaced.
- Human approval is required before reassignment.
- Unknown or conflicting state becomes `REVIEW_REQUIRED`.

