# Dispatcher Packets

Packets are the dispatcher jobs assigned to Codex workers.

Each worker gets one active packet at a time. A packet tells the worker what it may inspect, what it may change after approval, what paths are blocked, what validation must run, and what output is expected.

Required packet fields:

- `packet_id`
- `worker_id`
- `status`
- `allowed_paths`
- `blocked_paths`
- `task_goal`
- `validation_steps`
- `expected_outputs`
- `approval_required`
- `created_at`
- `updated_at`
- `next_safe_action`

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

Packet safety rule:

If a worker needs a path that is not listed in `allowed_paths`, the worker must stop and request a new packet or a packet update.

