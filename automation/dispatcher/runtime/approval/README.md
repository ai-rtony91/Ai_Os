# Approval Runtime

This folder is reserved for the AI_OS approval runtime scaffold.

Current scope:

- Documentation and example records only.
- No executable approval automation.
- No automatic APPLY.
- No automatic commit.
- No automatic push.

Approval runtime rules:

- Human approval is required before APPLY.
- Approval must bind to a packet, worker, task, and exact file list.
- Approval records must include validator, lock, dirty repo, and risk evidence.
- Missing, stale, or mismatched approval records are `REVIEW_REQUIRED`.
- Blocked or rejected approvals must not start APPLY.

Required approval states:

- `REQUESTED`
- `WAITING_REVIEW`
- `APPROVED`
- `BLOCKED`
- `REJECTED`
- `EXPIRED`
- `REVIEW_REQUIRED`

Every runtime record must include `next_safe_action`.

