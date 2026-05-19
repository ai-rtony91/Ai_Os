# Phase 15.4 Runtime Architecture

Phase 15.4 consolidates dispatcher runtime planning into one plain, controlled design.

The runtime is the local control layer for guided AI_OS work. It does not place trades, call brokers, use API keys, run live webhooks, commit, push, or bypass human approval.

## Runtime Goal

The dispatcher runtime keeps multi-worker work from fragmenting.

It coordinates:

- packets
- locks
- workers
- heartbeats
- recovery
- validators
- approvals
- commit package readiness
- status outputs
- queue health

## Runtime Owners

The dispatcher runtime controller owns the full work cycle.

Packet runtime manager owns packet state.

Lock runtime manager owns file and folder ownership claims.

Worker lifecycle manager owns worker assignment and active worker state.

Heartbeat manager owns worker liveness checks.

Recovery reconciler owns crash, stale worker, stale lock, and dirty repo resume decisions.

Validator router owns which validation checks must run.

Approval router owns human approval gates.

Commit package manager owns commit readiness only. It never stages files by itself.

Status output writer owns dashboard-safe summaries.

Queue monitor owns queue health summaries.

## Runtime Flow

1. A packet is created.
2. A worker is assigned.
3. The worker claims allowed file or folder locks.
4. The worker runs DRY_RUN.
5. The worker requests approval before APPLY.
6. Human approval is recorded.
7. APPLY runs only for approved paths.
8. Validators run.
9. Commit readiness is prepared.
10. Human approval is required before staging, commit, or push.

## Duplication Rule

Only one file or table should own each runtime truth.

Status files are summaries. Ledgers are history. Dashboard-facing files are read-only views for later UI use.

## Safety Rule

When state is unclear, stale, dirty, conflicting, or outside approved paths, the runtime must mark the item `REVIEW_REQUIRED`.

