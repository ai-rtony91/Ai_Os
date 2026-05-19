# Phase 92 Dispatcher Orchestration Tree Cleanup

Date: 2026-05-19
Branch: `phase-92-dispatcher-orchestration-tree-cleanup`
Mode: APPLY, documentation-only

## Purpose

Clean the next active tree clutter after dashboard cleanup by inspecting dispatcher and orchestration legacy docs, extracting durable ideas into canonical documentation, checking active references, and classifying `automation/orchestration` without moving runtime code.

## Scope

Allowed paths used:

- `docs/concepts/aios-dispatcher-orchestration-concepts.md`
- `docs/audits/phase-92-dispatcher-orchestration-tree-cleanup.md`

Allowed but not changed:

- `docs/architecture/aios-system-architecture.md`
- `docs/workflows/aios-operator-workflows.md`

Blocked by instruction:

- apps
- services
- schemas
- tests
- `.github`
- broker, OANDA, webhook, live trading paths
- APPLY scripts
- `automation/orchestration` moves

## Files And Folders Inspected

- `docs/AI_OS/dispatcher` - 57 markdown files.
- `docs/AI_OS/orchestration` - 48 markdown files and 1 folder-purpose text file.
- `automation/orchestration` - 244 files across runtime scripts, examples, state, ledgers, reports, queues, workers, validators, and supervisor folders.
- Canonical docs inspected:
  - `docs/concepts/aios-dispatcher-orchestration-concepts.md`
  - `docs/architecture/aios-system-architecture.md`
  - `docs/workflows/aios-operator-workflows.md`
- Active reference areas searched:
  - `apps`
  - `automation`
  - `scripts`
  - `services`
  - `schemas`
  - `tests`
  - `.github`

## Extracted Ideas

Useful dispatcher/orchestration ideas preserved in the canonical concepts doc:

- packet lifecycle states for queued, locked, approval waiting, blocked, retryable, and complete work,
- dead-letter queue separation between retryable and poison packets,
- worker lease, heartbeat, and recovery models,
- runtime rebuild from visible registries, queues, ledgers, and reports,
- assignment locking and single-writer safety,
- validator chain outcomes with clear PASS, FAIL, BLOCKED, and REVIEW_REQUIRED statuses,
- exact-file commit package readiness,
- display-first scripts that expose state without mutating protected paths,
- human approval gates before APPLY, commit, push, merge, or risky automation.

## Move Decision

No folders were moved.

`docs/AI_OS/dispatcher` was not archived because active automation references still point at it.

`docs/AI_OS/orchestration` was not archived because active automation and operator workflow references still point at it.

## Exact Blockers

Dispatcher blockers:

- `automation/dispatcher/validators/Test-AIOSDispatcherDryRun.ps1` references `docs/AI_OS/dispatcher`.
- `automation/dispatcher/validators/Test-AIOSDispatcherDryRun.ps1` references:
  - `docs/AI_OS/dispatcher/PHASE_15_3_DISPATCHER_CORE.md`
  - `docs/AI_OS/dispatcher/DISPATCHER_PACKET_SCHEMA.md`
  - `docs/AI_OS/dispatcher/DISPATCHER_LOCK_SCHEMA.md`
  - `docs/AI_OS/dispatcher/DISPATCHER_APPROVAL_SCHEMA.md`
  - `docs/AI_OS/dispatcher/DISPATCHER_COMMIT_PACKAGE_SCHEMA.md`
  - `docs/AI_OS/dispatcher/DISPATCHER_RECOVERY_BOOTSTRAP.md`
  - `docs/AI_OS/dispatcher/DISPATCHER_VALIDATOR_CHAIN.md`
  - `docs/AI_OS/dispatcher/DISPATCHER_DASHBOARD_DATA_CONTRACT.md`
- `automation/operator/Test-AIOSCodexWindowSnapshot.DRY_RUN.ps1` references `docs/AI_OS/dispatcher/runtime/CODEX_WINDOW_SNAPSHOT_BOOTSTRAP.md`.

Orchestration blockers:

- `automation/status/Get-AiOsWorkflowState.DRY_RUN.ps1` references `docs\AI_OS\orchestration\AIOS_ORCHESTRATION_FRAMEWORK_DRAFT.md`.
- `automation/operator/Test-AiOsWorkflowOrchestrator.DRY_RUN.ps1` references `docs/AI_OS/orchestration/AIOS_WORKFLOW_ORCHESTRATOR_V1.md`.
- `automation/operator/Test-AiOsWorkerAutoRouting.DRY_RUN.ps1` references `docs/AI_OS/orchestration/AIOS_WORKER_AUTO_ROUTING_V1.md`.
- `automation/operator/Test-AiOsPhase3State.DRY_RUN.ps1` references `docs/AI_OS/orchestration/AIOS_PHASE3_STATEFUL_ORCHESTRATION.md`.
- `automation/orchestration/bootstrap/Test-AiOsWorkspaceBootstrap.DRY_RUN.ps1` references multiple `docs/AI_OS/orchestration` rulebook/bootstrap docs.
- `automation/orchestration/supervisor/Resolve-AiOsSupervisorAssignment.DRY_RUN.ps1` references `AIOS_OPERATOR_RULEBOOK.md`, `AIOS_DAILY_START.md`, and `AIOS_WORKSPACE_BOOTSTRAP.md`.
- `automation/orchestration/validators/Invoke-OrchestrationValidatorChain.DRY_RUN.ps1` references `docs/AI_OS/orchestration` and `PHASE_15_3_4_VALIDATOR_CHAIN_AUTOMATION.md`.
- Multiple `automation/orchestration/*.json`, worker profile, lock, ledger, approval, recovery, and work packet files still reference `docs/AI_OS/orchestration`.

## automation/orchestration Classification

Active code:

- `adapters/`, `advancement/`, `approval_detection/`, `approval_processor/`, `approval_runner/`, `blockers/`, `bootstrap/`, `clean_state/`, `command_queue/`, `commit_packages/`, `compliance/`, `control/`, `control_summary/`, `daemon/`, `daily_snapshot/`, `git/`, `github_status/`, `guard/`, `health/`, `health_summary/`, `locks/`, `memory/`, `mission_control/`, `next_step/`, `operator/`, `policy/`, `post_push/`, `pr_gates/`, `queue_runner/`, `recommendations/`, `router/`, `runtime/`, `self_heal/`, `supervisor/`, `swarm/`, `task_generator/`, `terminal_workstations/`, `validator_chain_runner/`, `validators/`, `work_packets/`, `worker_builder/`, `worker_lanes/`, `workers/`.
- Root scripts such as `Run-AiOsOperatorLoop.DRY_RUN.ps1`, `Run-AiOsPreflight.DRY_RUN.ps1`, `Test-AiOsCommandCenterState.DRY_RUN.ps1`, `Test-AiOsOperationalChain.DRY_RUN.ps1`, display scripts, and PR template helpers.

Active examples/state:

- `approval_inbox/*.json`
- `command_queue/AIOS_COMMAND_QUEUE.json`
- `claims/WORKER_CLAIM_REGISTRY_001.json`
- `locks/FILE_LOCK_REGISTRY_001.json`
- `memory/AIOS_RUNTIME_MEMORY.json`
- `operator/AIOS_OPERATOR_RULES.json`
- `policy/AIOS_WORKER_SAFETY_POLICY.json`
- `queue/*.json`
- `workers/AIOS_WORKER_PROFILES.json`
- `workers/AIOS_WORKER_REGISTRY.json`
- `workers/WORKER_REGISTRY.json`
- `workers/*heartbeat.json`
- `work_packets/active/*.json`

Stale examples:

- root `*.v1.example.json`
- root `*.example.json`
- subfolder `*.example.json`
- v1 display/example files that mirror older planning models
- `task_cards/WORKER-*-TASK.md`

Logs/temp/generated candidates:

- `reports/*.csv`
- `reports/ORCHESTRATION_STATUS_SNAPSHOT_001.md`
- `PR_BODY_LAST_GENERATED.md`
- `workers/logs/*.log`
- generated status/check reports
- `work_packets/complete/*.json`
- `work_packets/blocked/*.json`

Future cleanup targets:

- Redirect active references away from `docs/AI_OS/dispatcher` and `docs/AI_OS/orchestration` before any archive move.
- Decide whether heartbeat and runtime memory JSON files should remain checked in.
- Separate source examples from generated runtime state.
- Archive stale v1 examples only after validator/operator dependencies are removed.
- Decide whether old task cards are retained as fixtures or archived as historical planning artifacts.

## Validation Plan

Required validation after edits:

- `git status --short -uall`
- `git diff --stat`
- `git diff --name-status`
- `git diff --check`
- parser check for changed `.ps1` files, if any
- JSON parse check for changed `.json` files, if any
- confirm no unauthorized files changed
- confirm no delete-only entries

## Result

Phase 92 extracted useful ideas and documented blockers. No source folders were archived because active references remain.

Push: NO
