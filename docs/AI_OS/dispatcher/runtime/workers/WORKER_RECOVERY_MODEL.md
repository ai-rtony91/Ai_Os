# Worker Recovery Model

Worker recovery reconciles worker sessions, heartbeats, packets, locks, approvals, and repo state after interruption.

## Source Of Truth

Worker recovery summary belongs in:

`Reports/dispatcher/runtime/workers/worker_recovery_status.json`

## Recovery Inputs

- active worker table
- worker heartbeat table
- packet runtime table
- lock runtime table
- approval runtime status
- validator runtime status
- git status
- dirty and untracked file state

## Safe Automated Recovery Actions

- read current runtime files
- classify stale workers
- detect missing heartbeats
- detect packet and lock mismatches
- mark unclear state `REVIEW_REQUIRED`
- recommend the next safe action

## Human Approval Required

Human approval is required before:

- reassigning a stale worker packet
- overriding a worker lock
- resuming APPLY
- preparing a commit package
- staging, committing, or pushing

## Recovery Rules

- Stale worker does not mean safe to replace.
- Interrupted APPLY becomes `REVIEW_REQUIRED`.
- Unknown worker state becomes `REVIEW_REQUIRED`.
- Packet mismatch becomes `REVIEW_REQUIRED`.
- Lock mismatch becomes `REVIEW_REQUIRED`.

