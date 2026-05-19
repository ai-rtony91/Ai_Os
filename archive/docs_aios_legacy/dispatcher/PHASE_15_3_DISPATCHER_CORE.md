# Phase 15.3 Dispatcher Core

Phase 15.3 creates the first dispatcher backbone for controlled multi-Codex work.

The dispatcher is the control layer. It assigns packets, tracks file ownership, requires approval before edits, validates work, prepares commit packages, and records recovery state.

Worker rule:

Workers do not free-roam. Each worker follows one packet and one approved path list.

Core safety model:

- One packet per worker.
- One lock per file ownership claim.
- Human approval is required before APPLY.
- Human approval is required before commit or push.
- Dirty repo state blocks commit packaging.
- Untracked `??` files are `REVIEW_REQUIRED`.
- Never use `git add .`.
- Stage exact approved files only.

Worker flow:

1. Dispatcher creates packet.
2. Worker claims packet.
3. Worker claims file lock.
4. Worker runs DRY_RUN.
5. Worker submits approval request.
6. Human approves or rejects.
7. Worker runs APPLY only if approved.
8. Validators run.
9. Commit package is created.
10. Human reviews commit package.
11. Exact files are staged.
12. Commit and push happen only after approval.
13. Clean state is verified.

Required status values:

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

