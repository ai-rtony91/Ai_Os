# AI_OS Runtime API Contract

Mode: READ_ONLY

This contract defines the internal runtime visibility surface exposed by
`services/orchestrator/index.js`. The API is for local status, queue, audit,
health, visibility, and control-readiness inspection only.

## Endpoints

### GET /api/runtime/status

Returns runtime state from local telemetry files:

- `telemetry/runtime/runtime_state.json`
- `telemetry/runtime/runtime_heartbeat.json`
- `telemetry/runtime/runtime_process.json`

The endpoint reports missing files as `UNKNOWN` or `MISSING` data. It does not
start or stop runtime processes.

### GET /api/runtime/queue

Returns a read-only summary of:

- `automation/orchestration/queue/DISPATCHER_QUEUE.json`

The endpoint returns queue item counts, status counts, lane counts, and raw
items. It does not assign, advance, or edit queue items.

### GET /api/runtime/audit

Returns a timeline from:

- `telemetry/work_ledger.jsonl`

Optional query:

- `recent`: positive integer limiting timeline output to the most recent
  entries.

Invalid JSONL lines are counted and skipped.

### GET /api/runtime/health

Returns a combined read-only health summary from runtime state, heartbeat,
queue, and telemetry ledger parse status.

Optional query:

- `staleHeartbeatMinutes`: positive integer heartbeat freshness limit.

### GET /api/runtime/visibility

Returns one combined read-only snapshot for internal consumers. It includes
runtime status, health, queue status, recent audit entries, and control summary.

### GET /api/runtime/control

Returns control capability state only. Runtime start, stop, assignment, and
packet advancement are blocked by API default.

## Safety Boundary

This API must remain read-only unless a future APPLY explicitly approves a
separate control layer. The current API does not expose POST control routes and
does not call PowerShell control scripts.

Blocked by default:

- runtime start
- runtime stop
- queue item assignment
- packet advancement
- APPLY
- commit
- push
- broker execution
- live trading
- secret collection

Next safe action: use these endpoints for internal visibility only.
