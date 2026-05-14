# Dispatcher Approval Schema

An approval request asks the human operator for permission to APPLY changes.

DRY_RUN work may produce a plan and validation notes. APPLY work cannot start until the approval request is approved.

Required fields:

| Field | Purpose |
| --- | --- |
| `packet_id` | Packet requesting approval. |
| `worker_id` | Worker requesting approval. |
| `requested_changes` | Plain-English summary of intended edits. |
| `files_to_change` | Exact files the worker wants to change. |
| `validation_summary` | DRY_RUN validation result. |
| `risk_summary` | Known risks and blocked areas. |
| `approval_status` | Current approval state. |
| `approved_by_human` | True only after human approval. |
| `approval_timestamp` | Approval or rejection time. |
| `next_safe_action` | Next safe operator action. |

Approval statuses:

- `PENDING`
- `APPROVED`
- `REJECTED`
- `REVIEW_REQUIRED`

Safety rule:

If `approved_by_human` is not true, APPLY is blocked.

