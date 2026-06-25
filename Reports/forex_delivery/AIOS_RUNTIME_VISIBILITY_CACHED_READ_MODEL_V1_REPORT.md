# AIOS Runtime Visibility Cached Read Model V1 Report

Packet: `AIOS-RUNTIME-VISIBILITY-CACHED-READ-MODEL-V1`
Mode: `APPLY`
Lane: `runtime-visibility-cached-read-model-v1`

## What This Does For AIOS

Runtime visibility now has a dependency-aware cached read model for `getVisibilitySnapshot()`.
The first read still builds the normal read-only snapshot from runtime, queue, and telemetry sources.
Repeated reads reuse the cached snapshot while the dependency file fingerprints remain unchanged and the cache TTL is still valid.

This keeps the dashboard/status path responsive without adding mutation authority.

## Expected Latency Savings

Expected savings come from avoiding repeated filesystem reads and JSON/JSONL parsing for unchanged runtime visibility inputs during quick dashboard refreshes.
The first read has the same cost as before.
Subsequent reads inside the 1000 ms TTL avoid rebuilding the snapshot unless one of these source files changes:

- `telemetry/runtime/runtime_state.json`
- `telemetry/runtime/runtime_heartbeat.json`
- `telemetry/runtime/runtime_process.json`
- `telemetry/work_ledger.jsonl`
- `telemetry/night_supervisor/night_ledger.jsonl`
- `automation/orchestration/queue/DISPATCHER_QUEUE.json`

The largest practical improvement should appear when the telemetry ledgers grow or when the dashboard polls faster than the source files change.

## Safety Boundary

- Cache fingerprinting uses file stat reads only.
- The cache performs no source file writes, deletes, moves, queue mutation, control mutation, worker launch, broker call, OANDA call, or network call.
- The existing schema `aios.runtime_visibility_api.v1` is preserved.
- Existing read-only fields, blocked control summary, frontend-safe display contract, and `nextSafeAction` semantics are preserved.
- Missing source files remain safe because the existing snapshot builder still produces the blocked/read-only model.

## Validation

Validated during this packet:

- `node --test tests/services/runtimeVisibilityCache.test.js` passed 6/6 tests.
- `node --test tests/services/runtimeVisibilityContract.test.js` passed 4/4 tests.
- `node -c services/orchestrator/runtimeVisibilityCache.js` passed.
- `node -c services/orchestrator/runtimeApiService.js` passed.
- `git diff --check` passed with only the existing Git line-ending warning for `services/orchestrator/runtimeApiService.js`.

## Future Next Packet Recommendation

Add an optional read-only runtime visibility timing probe that records cache hit/miss counts and snapshot build duration into generated evidence only.
Keep that probe display-only and do not connect it to scheduler, queue mutation, broker, OANDA, live trading, or approval authority.
