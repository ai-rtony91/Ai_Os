# Operations Documentation Index

Status: CURRENT
Mode: Operations documentation

## Purpose

This index points MAIN CONTROL and worker lanes to the current operations runbooks.

## Current Runbooks

- `docs/AI_OS/operations/MAIN_CONTROL_OPERATING_MODEL.md`
  - MAIN CONTROL authority, evidence sources, stop conditions, and control commands.
- `docs/AI_OS/operations/WORKER_LANE_LIFECYCLE.md`
  - Worker lane assignment, DRY_RUN/APPLY lifecycle, isolation, and stale lane review.
- `docs/AI_OS/operations/RUNTIME_CONTROL_RUNBOOK.md`
  - Runtime startup, shutdown, status, health, state files, and stop conditions.
- `docs/AI_OS/operations/QUEUE_AND_PACKET_LIFECYCLE.md`
  - Queue evidence, packet statuses, approval boundary, and review rules.
- `docs/AI_OS/operations/AUDIT_REPLAY_AND_OBSERVABILITY.md`
  - Telemetry ledger, audit replay, runtime visibility, invalid data, and recovery interpretation.
- `docs/AI_OS/operations/MERGE_ORDER_AND_VALIDATION.md`
  - Merge review order, validator chain, required evidence, and blockers.
- `docs/AI_OS/operations/DO_NOT_DO_RULES.md`
  - Hard safety boundaries for operations work.

## Supporting Existing Docs

- `docs/AI_OS/operations/STAGE9_OPERATIONAL_SCAFFOLD_PLAN.md`
- `docs/AI_OS/WORKER_GOVERNANCE.md`
- `docs/AI_OS/runtime/RUNTIME_LOOP.md`
- `docs/AI_OS/operator/AIOS_OPERATOR_COMMAND_MAP_DRAFT.md`
- `docs/AI_OS/operator/AIOS_WORKER_BRANCH_AND_LANE_RULES.md`
- `docs/AI_OS/operator/AIOS_MERGE_VALIDATION_AND_CONFLICT_ARBITRATION.md`
- `docs/AI_OS/observability/AIOS_OBSERVABILITY_HEALTHCHECKS_DRAFT.md`

## Source Evidence Paths

- `scripts/control/`
- `scripts/workers/`
- `scripts/runtime/`
- `services/runtime/`
- `services/dispatcher/`
- `services/telemetry/`
- `automation/orchestration/queue/DISPATCHER_QUEUE.json`
- `telemetry/work_ledger.jsonl`

## Next Safe Action

Start operations review with `MAIN_CONTROL_OPERATING_MODEL.md`, then use the specific runbook for runtime, queue, worker, audit, or merge work.
