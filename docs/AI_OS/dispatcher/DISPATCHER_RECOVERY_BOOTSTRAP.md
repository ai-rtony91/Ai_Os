# Dispatcher Recovery Bootstrap

Recovery state helps AI_OS resume after a crash, reboot, or closed Codex window.

The recovery file should be checked before assigning new packets.

Required recovery fields:

| Field | Purpose |
| --- | --- |
| `active_packets` | Packets that were assigned or in progress. |
| `active_locks` | File ownership claims that may still matter. |
| `pending_approvals` | APPLY requests waiting for human review. |
| `failed_packets` | Packets that failed or were blocked. |
| `last_known_git_state` | Last recorded branch and dirty state. |
| `next_safe_action` | Safest resume instruction. |
| `updated_at` | Last recovery update time. |

Recovery rules:

- Unknown worker state becomes `REVIEW_REQUIRED`.
- Expired locks become `REVIEW_REQUIRED`.
- Dirty repo state is not cleaned automatically.
- Staging, commit, and push are never automatic.

