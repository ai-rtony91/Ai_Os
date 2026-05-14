# Packet Template Schema

## Purpose

This schema defines the first packet template shape for AI_OS dispatcher runtime work.

Packets should be beginner-readable, machine-readable, and strict enough to prevent workers from free-roaming.

## Required Fields

| Field | Purpose |
| --- | --- |
| `packet_id` | Unique packet identifier. |
| `phase_id` | Phase or workload identifier. |
| `window_id` | Intended worker window, when known. |
| `worker_role` | Worker role expected to run the packet. |
| `status` | Current packet status. |
| `priority` | Operator priority for next selection. |
| `mode` | `DRY_RUN` or approved `APPLY`. Default is `DRY_RUN`. |
| `task_goal` | Plain-English objective. |
| `allowed_paths` | Paths the worker may inspect or edit when approved. |
| `blocked_paths` | Paths the worker must not touch. |
| `validation_steps` | Required validation commands or checks. |
| `expected_report_sections` | Required completion report sections. |
| `approval_required` | Whether human approval is required before APPLY. |
| `apply_allowed` | Whether APPLY is currently allowed. |
| `created_at` | Packet creation timestamp. |
| `updated_at` | Last packet update timestamp. |
| `assigned_worker_id` | Worker assigned to packet, or `null`. |
| `next_safe_action` | One safe beginner-readable next action. |

## Required Status Values

- `QUEUED`
- `ASSIGNED`
- `DRY_RUN_STARTED`
- `DRY_RUN_COMPLETE`
- `APPROVAL_REQUIRED`
- `BLOCKED`
- `REVIEW_REQUIRED`

Future runtime tables may also support:

- `APPLY_APPROVED`
- `APPLY_RUNNING`
- `APPLY_COMPLETE`
- `VALIDATED`
- `COMMIT_READY`
- `COMMITTED`
- `FAILED`

## Default Safety Values

Recommended defaults:

- `mode`: `DRY_RUN`
- `approval_required`: `true`
- `apply_allowed`: `false`
- `assigned_worker_id`: `null`

## Review Required Rules

Set packet status to `REVIEW_REQUIRED` when:

- allowed paths are missing or too broad
- blocked paths conflict with allowed paths
- worker state is unknown
- packet references a stale lock
- packet references untracked or unrelated dirty files
- APPLY appears abandoned
- validation cannot confirm safety

## Next Safe Action Rule

Each packet must include one clear `next_safe_action`.

Bad:
`Review the queue, maybe run validators, and maybe assign a worker.`

Good:
`Assign this packet to one available DRY_RUN worker after confirming allowed and blocked paths.`
