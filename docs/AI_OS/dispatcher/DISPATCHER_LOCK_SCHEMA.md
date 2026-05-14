# Dispatcher Lock Schema

A lock is a file ownership claim.

Workers must claim locks before APPLY work starts. Locks prevent two workers from editing the same file or folder at the same time.

Required fields:

| Field | Purpose |
| --- | --- |
| `lock_id` | Unique lock name. |
| `worker_id` | Worker holding the lock. |
| `claimed_paths` | Files or folders claimed by the worker. |
| `packet_id` | Packet connected to the lock. |
| `created_at` | Lock creation timestamp. |
| `expires_at` | Time when the lock needs review. |
| `status` | Current lock status. |
| `release_reason` | Why the lock was released or marked inactive. |

Allowed lock statuses:

- `ACTIVE`
- `RELEASED`
- `EXPIRED`
- `BLOCKED`
- `REVIEW_REQUIRED`

Overlap rule:

An active folder lock blocks file locks inside that folder. An active file lock blocks another worker from claiming that file or its parent folder.

