# AI_OS Night Supervisor Qualification Gates

Status: Gate 1 foundation governance.

This document records the approved Gate 1 foundation decisions. It does not
authorize autonomy, schedulers, daemons, backup execution, Raspberry Pi
functionality, effectors, commits, pushes, merges, broker execution, trading,
secrets handling, or authority expansion.

## Qualification States

| State | Meaning | Allowed authority | Promotion rule |
|---|---|---|---|
| PROVISIONAL | Implemented or documented, but not trusted. | Read-only evidence collection and reporting. | Controlled evidence exists for the next gate. |
| TESTED | Controlled tests passed. | Supervised DRY_RUN use only. | Gate evidence is repeatable and reviewed. |
| TRUSTED | Repeated real evidence passed across operating windows. | Higher-confidence recommendations only. | Multi-night evidence and recovery proof pass. |
| QUALIFIED | Human Owner signs off after ledger-backed evidence. | Authority named by the promotion record only. | Human Owner approval in the qualification ledger. |

Implemented does not mean qualified. Green tests do not mean overnight trust.
Validator output is evidence, not approval. No AI worker grants itself
authority.

## Gate 1 Decision Record

Approved Human Owner decisions for Gate 1 foundation:

1. System 2 is the canonical heartbeat authority.
2. System 1 is legacy/reference-only.
3. Daemon heartbeat loops are forbidden for qualification.
4. Supervisor V2 receives a read-only worker health stage.
5. Qualification ledger foundation is required before overnight testing.
6. PR #301 remains effector-only and disabled.
7. Backup Officer remains documentation-only.
8. Maintenance Officer remains documentation-only.
9. No authority expands before Gate 1 passes.

## Heartbeat Authority

System 2 means the dispatcher/runtime worker heartbeat model, including:

- `automation/dispatcher/runtime/workers/Update-AIOSWorkerHeartbeat.ps1`
- `automation/dispatcher/runtime/validators/Test-AIOSStaleWorker.ps1`
- `Reports/dispatcher/runtime/workers/worker_heartbeat_table.json`
- `Reports/dispatcher/runtime/workers/active_worker_table.json`

System 1 means the simple legacy heartbeat scripts, including:

- `scripts/write-worker-heartbeat.ps1`
- `scripts/heartbeat-loop.ps1`
- `scripts/detect-stale-workers.ps1`
- `scripts/mark-worker-offline.ps1`

System 1 must not be used as qualification authority. Its loop behavior is not
qualified and must not become an overnight daemon path.

## Gate 1 Worker Health Scope

Gate 1 may add:

- a worker heartbeat schema;
- a qualification ledger schema;
- a read-only worker health monitor;
- Supervisor V2 report fields for worker health evidence;
- tests proving read-only behavior and stale/unknown classification.

Gate 1 must not:

- write heartbeat files;
- launch workers;
- reassign packets;
- release locks;
- approve work;
- enable effectors;
- run backup;
- create schedules;
- create daemons.

## Required Worker States

Gate 1 uses these canonical states:

- ACTIVE
- IDLE
- STARTING
- STOPPING
- STALE
- MISSING
- CRASHED
- UNKNOWN

Unknown or malformed heartbeat evidence must be reported as `UNKNOWN`, not
repaired automatically.

## Qualification Ledger Foundation

The ledger schema is required before overnight testing, but the ledger itself is
not created in Gate 1 foundation. Future ledger entries must be append-only,
evidence-linked, and promotion-neutral until Human Owner approval.

## Stop Rule

Gate 1 completion means the read-only evidence foundation is ready for review.
It does not promote Night Supervisor beyond PROVISIONAL and does not authorize
Gate 2, overnight runs, backup execution, scheduler work, or effectors.
