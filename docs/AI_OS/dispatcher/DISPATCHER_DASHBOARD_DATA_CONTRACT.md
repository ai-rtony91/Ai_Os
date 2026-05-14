# Dispatcher Dashboard Data Contract

This document defines future dashboard data only. It does not change the dashboard.

The dispatcher can later publish a status snapshot for the AI_OS dashboard.

Recommended fields:

| Field | Purpose |
| --- | --- |
| `generated_at` | Snapshot time. |
| `dispatcher_status` | Overall dispatcher status. |
| `active_worker_count` | Number of workers with assigned packets. |
| `queued_packet_count` | Number of waiting packets. |
| `active_lock_count` | Number of active ownership claims. |
| `pending_approval_count` | APPLY requests waiting for review. |
| `failed_packet_count` | Failed or blocked packets. |
| `commit_ready_count` | Packages ready for human review. |
| `repo_state` | Clean, dirty, or review-required state. |
| `next_safe_action` | Beginner-readable next action. |

Status output should stay local-first and must not collect secrets.

