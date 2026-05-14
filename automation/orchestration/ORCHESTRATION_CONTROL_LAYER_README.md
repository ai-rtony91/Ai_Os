# AI_OS Orchestration Control Layer

This layer organizes Codex worker work into visible packets, locks, approvals, validators, commit packages, recovery notes, and status reports.

It does not run work automatically. It gives the operator a controlled way to see what each worker is allowed to touch, what must be reviewed, and what is blocked.

## Worker Packet Flow

1. A packet starts as `draft`.
2. The operator reviews the objective, allowed paths, blocked paths, and validation steps.
3. The packet becomes `ready`.
4. One worker claims one packet.
5. The worker reports DRY_RUN findings.
6. APPLY work waits for human approval.
7. Completed work must pass validators before commit packaging.

## Approval Before APPLY

APPROVAL is required before APPLY because workers may have stale context, file ownership may conflict, and protected paths must stay untouched.

Approval must be explicit and tied to exact files and exact allowed paths.

## Intentional Commit Packages

Commits are packaged intentionally so the operator can review exactly which files are staged and which files stay out.

This prevents blind commits, unrelated file inclusion, and accidental staging from a dirty worktree.

## Clean-State Verification

Clean-state checks matter because stale files, untracked files, ahead or behind branches, and interrupted work can hide risk.

Workers should not start new APPLY work until the operator understands repo state.

## Blocked Execution

This layer blocks broker actions, live trading, real order paths, API key collection, startup tasks, scheduled tasks, external network calls, and unsafe automation.

AI_OS orchestration is paper-only and operator-governed.
