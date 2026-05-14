# Worker Heartbeat Model

Heartbeats show whether a worker session appears active.

A current heartbeat does not prove work is correct. A stale heartbeat does not make the worker safe to replace.

## Source Of Truth

Current heartbeat state belongs in:

`Reports/dispatcher/runtime/workers/worker_heartbeat_table.json`

## Required Heartbeat Fields

| Field | Purpose |
| --- | --- |
| `worker_id` | Worker identity sending the heartbeat. |
| `launch_session_id` | Launch session connected to the heartbeat. |
| `assigned_packet_id` | Packet connected to the worker, or null. |
| `current_state` | Worker state at heartbeat time. |
| `heartbeat_time` | Last heartbeat timestamp. |
| `heartbeat_age_seconds` | Computed heartbeat age. |
| `stale_after_seconds` | Age threshold for stale classification. |
| `stale_status` | `CURRENT`, `STALE`, or `REVIEW_REQUIRED`. |
| `terminal_window_name` | Visible terminal name. |
| `next_safe_action` | Safe operator instruction. |

## Stale Rules

- Missing heartbeat for an assigned worker becomes `REVIEW_REQUIRED`.
- Stale heartbeat during `APPLY_RUNNING` becomes `REVIEW_REQUIRED`.
- Stale heartbeat during `VALIDATING` becomes `REVIEW_REQUIRED`.
- Stale heartbeat while `IDLE` becomes `STALE`.
- Stale worker does not mean safe to replace.

