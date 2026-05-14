# AI_OS Dispatcher

This folder is the controlled work area for multi-Codex coordination.

The dispatcher controls worker activity. Workers do not free-roam. Each worker receives one packet, claims the needed file ownership lock, completes DRY_RUN work first, and waits for human approval before APPLY.

Core rules:

- One packet per worker.
- One lock per file ownership claim.
- Human approval is required before APPLY.
- Human approval is required before commit or push.
- A dirty repo blocks commit packaging.
- Untracked `??` files are `REVIEW_REQUIRED`.
- Never use `git add .`.
- Stage exact approved files only.
- Do not touch protected root files unless a packet explicitly allows it and a human approves it.
- Do not touch trading execution, credential, or external execution paths from dispatcher scaffold work.

Required packet status values:

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

Dispatcher folders:

- `packets/` stores worker packets.
- `locks/` stores file ownership claims.
- `approval_inbox/` stores APPLY approval requests.
- `commit_packages/` stores exact-file commit package drafts.
- `recovery/` stores crash recovery state.
- `validators/` stores DRY_RUN validation helpers.

