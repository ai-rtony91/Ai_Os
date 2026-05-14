# Phase 15.3.2 Assignment Locking

## Purpose

Assignment locking gives AI_OS a controlled way to let parallel Codex workers reserve packets and paths without colliding.

The system is intentionally simple: a worker claims one packet, the claim identifies assigned paths, and validators report conflicts before APPLY work continues.

## Why Assignment Locking Exists

Without locks, two workers can edit the same file group, create conflicting validation results, or accidentally package unrelated changes into a commit.

Assignment locks make ownership visible before work starts.

## Scaling Parallel Workers Safely

AI_OS can scale parallel workers only when each worker has:

- one packet
- one claim
- clear assigned paths
- blocked paths
- human approval before APPLY
- validator checks before commit packaging

## Why This Matters Before 10-25 Workers

Small worker counts can be managed manually. Larger worker counts need clear claim and lock records so the operator can see who owns each path and which packets are blocked.

Before AI_OS reaches 10-25 workers, collisions must be visible, recoverable, and blocked from commit packages.

## Future Direction

Future orchestration should connect claims, locks, approval inbox records, validator results, recovery state, and worker activity ledgers into one operator check.

The direction remains local-first, paper-only, and human-approved.

Blocked actions stay blocked:

- live trading
- broker actions
- OANDA actions
- API key collection
- installs
- startup tasks
- scheduled tasks
- external calls
- commits without exact-file review
- pushes without explicit approval

Next safe action: run the claim and lock DRY_RUN validators before assigning more workers.
