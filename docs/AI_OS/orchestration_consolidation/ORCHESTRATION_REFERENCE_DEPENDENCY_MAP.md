# Orchestration Reference Dependency Map

## Reference Scan Summary

The audit searched `automation`, `docs`, and `schemas` for orchestration control terms including relay runner, session continuity, packet queue, approval inbox, clean-state, dispatcher, validator, worker assignment, PR lane, commit/push gate, active repo path, and Paper SOS runtime path.

References are widespread. This confirms that consolidation must update references before any move/delete.

## Files And Areas Actively Referenced

| Topic | Active or likely referenced paths |
|---|---|
| PR lane | `docs/workflows/AI_OS_PR_LANE_RUNNER.md`, `automation/orchestration/pr_gates/`, root PR helper scripts |
| Commit/push gate | `docs/workflows/AI_OS_COMMIT_PUSH_GATE.md`, `automation/orchestration/commit_packages/`, `automation/orchestration/pr_gates/` |
| Validator standards | `docs/workflows/VALIDATOR_EXECUTION_STANDARD.md`, `automation/orchestration/validators/`, `automation/orchestration/validator_chain_runner/` |
| Worker lifecycle | `docs/workflows/WORKER_TASK_LIFECYCLE_STANDARD.md`, `automation/orchestration/work_packets/`, `automation/orchestration/workers/` |
| Approval inbox | `automation/orchestration/approval_inbox/`, `automation/orchestration/approval_runner/`, `automation/orchestration/approval_processor/`, `docs/workflows/AI_OS_NIGHT_SUPERVISOR_APPROVAL_QUEUE_WORKFLOW.md` |
| Dispatch | `docs/AI_OS/dispatch/`, `schemas/aios/dispatch/`, `automation/orchestration/dispatch/`, `automation/orchestration/router/` |
| Night Supervisor | `docs/AI_OS/night_supervisor/`, `docs/workflows/AI_OS_OVERNIGHT_SUPERVISOR_WORKFLOW.md`, `automation/orchestration/night_supervisor/`, `schemas/aios/night_supervisor/` |
| OpenAI planner bridge | `docs/AI_OS/openai_api_bridge/`, `automation/orchestration/openai_api_bridge/`, `schemas/aios/dispatch/OPENAI_PACKET_DRAFT.schema.json` |

## Paths That Must Be Updated Before Move Or Delete

- Any script or doc that references root `show-*` scripts.
- Any script or doc that references root `*.example.json` orchestration snapshots.
- Any script or doc that references `approval_inbox.v1.example.json` instead of `approval_inbox/APPROVAL_INBOX_001.json`.
- Any script or doc that references `packet_queue_ledger.v1.example.json` instead of `work_packets/` or the approved queue path.
- Any script or doc that references `worker_registry.v1.example.json` instead of `workers/AIOS_WORKER_REGISTRY.json`.
- Any script or doc that references `session_continuity.v1.example.json` without stating it is legacy or compatibility evidence.
- Any script or doc that treats validator-chain output as approval rather than evidence.

## Old Or Root Example Reference Risks

The root of `automation/orchestration/` still contains multiple example/state-shaped files and display scripts that can be confused with active state:

- `approval_inbox.v1.example.json`
- `assignment_lock_controller.v1.example.json`
- `assignment_locks*.example.json`
- `launch_supervisor.v1.example.json`
- `orchestration_control_state.v1.example.json`
- `orchestration_gap_ledger.example.json`
- `orchestration_spine_v1.example.json`
- `orchestration_status_snapshot.example.json`
- `packet_queue_ledger.v1.example.json`
- `persistent_worker_supervisor.v1.example.json`
- `queue_health_supervisor.v1.example.json`
- `recovery_bootstrap*.example.json`
- `session_continuity.v1.example.json`
- `startup_orchestration.v1.example.json`
- `validator_routing_supervisor.v1.example.json`
- `worker_registry.v1.example.json`
- `show-*` root display helpers

## Unknown References Requiring Manual Review

- External operator launcher references outside `automation/orchestration/`.
- Dashboard or terminal launcher references that may read old root examples.
- Human copy/paste workflows documented outside `docs/AI_OS/` and `docs/workflows/`.
- `.github` workflow references to validators or scripts.
- Any nontracked local scripts or shortcuts on the operator machine.

