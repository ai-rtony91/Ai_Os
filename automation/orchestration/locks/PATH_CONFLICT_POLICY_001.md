# AI_OS Path Conflict Policy 001

Path ownership prevents worker collisions.

## Rules

- No dual ownership of the same file or folder path.
- Runtime paths have the highest priority because they can affect packet, lock, approval, validator, and recovery state.
- Documentation paths are lower priority but still need one owner when edited.
- Validator paths must stay isolated so validation behavior is not changed by unrelated worker packets.
- Overwrites are blocked unless the operator explicitly approves exact files.
- If ownership is unclear, mark the work `REVIEW_REQUIRED`.

## Escalation

Escalate to human review when:

- two workers claim overlapping paths
- a lock has no worker ID
- a claim has no packet ID
- a lock is expired but still affects active work
- a worker needs to edit a path owned by another worker

Next safe action: resolve conflicts before APPLY, staging, commit, or push.
