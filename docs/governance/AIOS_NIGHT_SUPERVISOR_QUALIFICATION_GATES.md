# AI_OS Night Supervisor Qualification Gates

Status: Gates 1-2 runtime evidence foundation governance.

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
- a System 2 runtime table bootstrap that creates conservative no-live-heartbeat evidence;
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

Runtime table bootstrap is blood supply, not qualification. Bootstrap rows prove
that Night Supervisor has a canonical place to read worker evidence; they do not
prove that any worker is alive, active, idle, stale, missing, crashed, trusted,
or qualified. Initial bootstrap rows must remain conservative and must not mark
any worker `ACTIVE`, `APPLY_RUNNING`, `VALIDATING`, or `HEALTHY`.

The canonical System 2 runtime worker files are:

- `Reports/dispatcher/runtime/workers/worker_heartbeat_table.json`
- `Reports/dispatcher/runtime/workers/active_worker_table.json`
- `Reports/dispatcher/runtime/workers/worker_registration_status.json`
- `Reports/dispatcher/runtime/workers/worker_session_ledger.json`

Gate 1 does not pass from bootstrap alone. Gate 1 requires live heartbeat
evidence, stale/missing behavior proof, read-only monitor proof, and Human Owner
review.

## Gate 2 Packet Integrity Scope

Gate 2 may add:

- a read-only packet integrity monitor;
- a packet integrity evidence schema when the routing contract is not enough;
- Supervisor V2 report fields for packet integrity evidence;
- tests proving packet integrity classification is conservative and read-only.

Gate 2 reuses Gate 1 worker health evidence. It must not create a second worker
health model, infer worker crashes without worker health evidence, mutate
packets, claim locks, approve packets, block dispatch by new policy, enable
effectors, or expand authority.

Gate 2 does not pass from the packet monitor alone. It requires packet ownership
evidence, lock/approval corroboration, stale/abandoned/orphaned packet drills,
and Human Owner review.

## Gates 1-7 Controlled Evidence Scope

The first seven Night Supervisor gates are:

1. Gate 1 - Worker Health / Heartbeat Evidence.
2. Gate 2 - Packet Integrity / Ownership Evidence.
3. Gate 3 - Crash / Recovery Awareness.
4. Gate 4 - Single Overnight Simulation.
5. Gate 5 - Multi-Night Evidence Model.
6. Gate 6 - Morning Handoff Preview.
7. Gate 7 - Qualification Ledger / Promotion Package Preview.

Controlled drills are allowed for TESTED evidence. Controlled drills may use
fixtures, temp directories, read-only monitor functions, and preview reports.
Controlled drills do not equal real-world overnight trust.

Real-world TRUSTED or QUALIFIED status still requires live evidence windows,
reviewed qualification ledger entries, recovery proof, morning handoff evidence,
and explicit Human Owner approval. No AI worker, validator, green test run,
simulated overnight report, or promotion package can grant that approval.

Gate 3 remains awareness-only. It may detect recovery need, but must not clear
locks, reassign packets, kill processes, launch workers, approve work, or run a
recovery executor.

Gate 4 may simulate overnight cycles. It must not wait overnight, schedule work,
start daemons, launch workers, or enable effectors.

Gate 5 defines the multi-night evidence model. It must reject fake
qualification when evidence windows are simulated or lack explicit real-world
window markers.

Gate 6 creates a morning handoff preview only. It must state that Night
Supervisor remains PROVISIONAL unless ledger evidence and Human Owner approval
prove otherwise.

Gate 7 may build preview ledger entries and promotion packages. It must not
forge Human Owner approval, write trusted/qualified status, or grant authority.

No authority expands before Gate 1 and Gate 2 have reviewed evidence. The
effector layer remains disabled.

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

Gate 1 or Gate 2 foundation completion means the read-only evidence foundation
is ready for review. It does not promote Night Supervisor beyond PROVISIONAL and
does not authorize overnight runs, backup execution, scheduler work, daemon
work, effectors, broker execution, trading, commits, pushes, merges, or any
autonomous authority.
