# Runtime Source Of Truth Map

This map defines which runtime files own facts.

Do not let dashboard fixtures, status summaries, or old queue files become competing sources of truth.

## Runtime Truths

| Runtime truth | Source of truth | Summary only |
| --- | --- | --- |
| Packets | `Reports/dispatcher/runtime/packets/packet_runtime_table.json` | `dispatcher_runtime_status.json` |
| Locks | `Reports/dispatcher/runtime/locks/lock_runtime_table.json` | `dispatcher_runtime_status.json` |
| Workers | `Reports/dispatcher/runtime/workers/active_worker_table.json` | `queue_health_summary.json` |
| Heartbeats | `Reports/dispatcher/runtime/heartbeats/worker_heartbeat_table.json` | `recovery_runtime_status.json` |
| Approvals | `Reports/dispatcher/runtime/approval/approval_runtime_ledger.json` | `approval_runtime_status.json` |
| Validators | `Reports/dispatcher/runtime/validators/validator_execution_ledger.json` | `validator_runtime_status.json` |
| Commit packages | `Reports/dispatcher/runtime/commit_packages/commit_package_ledger.json` | `commit_readiness_status.json` |
| Recovery | `Reports/dispatcher/runtime/recovery/recovery_runtime_ledger.json` | `recovery_runtime_status.json` |
| Queue health | Derived from packets, workers, locks, and heartbeats | `queue_health_summary.json` |
| Status index | Generated from runtime summaries | `runtime_status_index.json` |

## File Roles

Runtime tables own current state.

Ledgers own history and decisions.

Status files summarize current state for humans and future dashboard use.

Dashboard-facing files must not become the place where runtime truth is edited.

## Conflict Rule

If two files disagree, the source-of-truth file wins.

If the source-of-truth file is missing, invalid, stale, or cannot be parsed, the runtime must mark the affected item `REVIEW_REQUIRED`.

