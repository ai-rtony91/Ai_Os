# Dispatcher Locks

Locks prevent two workers from claiming the same file or folder at the same time.

Each lock records one ownership claim. A worker must hold a valid lock before APPLY work begins.

Required lock fields:

- `lock_id`
- `worker_id`
- `claimed_paths`
- `packet_id`
- `created_at`
- `expires_at`
- `status`
- `release_reason`

Allowed lock statuses:

- `ACTIVE`
- `RELEASED`
- `EXPIRED`
- `BLOCKED`
- `REVIEW_REQUIRED`

Overlap rule:

If one active lock claims a folder, another worker cannot claim a file inside that folder. If one active lock claims a file, another worker cannot claim that file or its parent folder for APPLY work.

Expired lock rule:

An expired lock is not automatically safe. It becomes `REVIEW_REQUIRED` until a human or dispatcher recovery step decides what should happen next.

