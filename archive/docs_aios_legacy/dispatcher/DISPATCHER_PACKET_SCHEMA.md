# Dispatcher Packet Schema

A packet is one job for one worker.

Required fields:

| Field | Purpose |
| --- | --- |
| `packet_id` | Unique packet name. |
| `worker_id` | Worker assigned to the packet. |
| `status` | Current packet status. |
| `allowed_paths` | Paths the worker may inspect or change when approved. |
| `blocked_paths` | Paths the worker must not touch. |
| `task_goal` | Plain-English goal. |
| `validation_steps` | Commands and checks required for this packet. |
| `expected_outputs` | Files, reports, or summaries expected from the worker. |
| `approval_required` | Whether human approval is needed before APPLY. |
| `created_at` | Packet creation timestamp. |
| `updated_at` | Last packet update timestamp. |
| `next_safe_action` | Next action a beginner operator can take safely. |

Allowed status values:

- `QUEUED`
- `ASSIGNED`
- `DRY_RUN_STARTED`
- `DRY_RUN_COMPLETE`
- `APPROVAL_REQUIRED`
- `APPLY_APPROVED`
- `APPLY_COMPLETE`
- `VALIDATED`
- `COMMIT_READY`
- `COMMITTED`
- `BLOCKED`
- `FAILED`
- `REVIEW_REQUIRED`

Packet rule:

If a path is not listed in `allowed_paths`, the worker must stop before editing it.

