# Approval Inbox Schema

Approval inbox records describe a worker request for APPLY permission.

The inbox is not an approval by itself. A request is only approved when `approval_status` is `APPROVED` and `approved_by_human` is `true`.

## Required Fields

| Field | Purpose |
| --- | --- |
| `approval_id` | Unique approval request ID. |
| `packet_id` | Packet connected to this request. |
| `worker_id` | Worker requesting APPLY permission. |
| `task_id` | Task or workload ID. |
| `approval_status` | Current request state. |
| `approved_by_human` | True only after human approval. |
| `requested_changes` | Beginner-readable summary of planned edits. |
| `expected_outputs` | Expected docs, JSON, reports, or other outputs. |
| `allowed_paths` | Paths the request may touch. |
| `blocked_paths` | Paths the request must not touch. |
| `files_expected_to_change` | Exact file list for APPLY. |
| `validator_summary` | Validator result evidence. |
| `risk_summary` | Risk notes for the operator. |
| `lock_summary` | Worker lock ownership evidence. |
| `dirty_repo_summary` | Current dirty repo and untracked file state. |
| `rollback_notes` | Recovery notes if APPLY fails. |
| `created_at` | Request creation time. |
| `approval_timestamp` | Human approval, rejection, or block time. |
| `next_safe_action` | Safest next operator action. |

## Valid Statuses

- `REQUESTED`
- `WAITING_REVIEW`
- `APPROVED`
- `BLOCKED`
- `REJECTED`
- `EXPIRED`
- `REVIEW_REQUIRED`

## Review Rule

If any required field is missing, stale, or inconsistent with current repo evidence, the request must be marked `REVIEW_REQUIRED`.

