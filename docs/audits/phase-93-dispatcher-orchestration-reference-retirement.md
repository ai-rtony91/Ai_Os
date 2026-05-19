# Phase 93 Dispatcher Orchestration Reference Retirement

Date: 2026-05-19
Branch: `phase-92-dispatcher-orchestration-tree-cleanup`
Mode: APPLY, reference retirement only

## Purpose

Retire active references that blocked archiving `docs/AI_OS/dispatcher` and `docs/AI_OS/orchestration`, without moving folders, deleting files, pushing, merging, touching protected app/service/schema/test/GitHub paths, or running APPLY scripts.

## Search Scope

Exact references searched across active areas:

- `docs/AI_OS/dispatcher`
- `docs\AI_OS\dispatcher`
- `docs/AI_OS/orchestration`
- `docs\AI_OS\orchestration`

Areas searched:

- `apps`
- `automation`
- `scripts`
- `services`
- `schemas`
- `tests`
- `.github`

## References Retired

Dispatcher references retired:

- `automation/dispatcher/validators/Test-AIOSDispatcherDryRun.ps1`
  - Replaced `docs/AI_OS/dispatcher` required folder with `docs/concepts`.
  - Replaced required dispatcher draft docs with canonical docs:
    - `docs/concepts/aios-dispatcher-orchestration-concepts.md`
    - `docs/architecture/aios-system-architecture.md`
    - `docs/workflows/aios-operator-workflows.md`
    - `docs/audits/phase-92-dispatcher-orchestration-tree-cleanup.md`
  - Replaced blocked-term scan root from `docs/AI_OS/dispatcher` to canonical docs.
- `automation/operator/Test-AIOSCodexWindowSnapshot.DRY_RUN.ps1`
  - Replaced `docs/AI_OS/dispatcher/runtime/CODEX_WINDOW_SNAPSHOT_BOOTSTRAP.md` with `docs/concepts/aios-dispatcher-orchestration-concepts.md`.

Orchestration references retired:

- `automation/operator/Test-AiOsWorkflowOrchestrator.DRY_RUN.ps1`
  - Replaced `docs/AI_OS/orchestration/AIOS_WORKFLOW_ORCHESTRATOR_V1.md` with `docs/concepts/aios-dispatcher-orchestration-concepts.md`.
  - Updated the documentation content check to validate canonical orchestration concepts instead of the legacy draft.
- `automation/operator/Test-AiOsWorkerAutoRouting.DRY_RUN.ps1`
  - Replaced `docs/AI_OS/orchestration/AIOS_WORKER_AUTO_ROUTING_V1.md` with `docs/concepts/aios-dispatcher-orchestration-concepts.md`.
- `automation/operator/Test-AiOsPhase3State.DRY_RUN.ps1`
  - Replaced `docs/AI_OS/orchestration/AIOS_PHASE3_STATEFUL_ORCHESTRATION.md` with `docs/concepts/aios-dispatcher-orchestration-concepts.md`.
- `automation/orchestration/assignment_locks.example.json`
  - Replaced `docs/AI_OS/orchestration/` with `docs/concepts/aios-dispatcher-orchestration-concepts.md`.
- `automation/orchestration/orchestration_gap_ledger.example.json`
  - Replaced legacy orchestration doc-folder references with canonical concept and Phase 92 audit docs.
- `automation/orchestration/packet_queue_ledger.v1.example.json`
  - Replaced legacy orchestration doc-folder references with canonical concept and operator workflow docs.
- `automation/orchestration/recovery_bootstrap.example.json`
  - Replaced legacy orchestration doc-folder reference with the Phase 92 audit doc.
- `automation/orchestration/worker_registry.v1.example.json`
  - Replaced legacy orchestration doc-folder references with canonical concept and operator workflow docs.

## Remaining Blockers

No remaining `docs/AI_OS/dispatcher` references were found in the active search scope.

Remaining `docs/AI_OS/orchestration` references were found in paths outside this phase's allowed edit scope:

- `automation/status/Get-AiOsWorkflowState.DRY_RUN.ps1`
- `automation/orchestration/bootstrap/Test-AiOsWorkspaceBootstrap.DRY_RUN.ps1`
- `automation/orchestration/supervisor/Resolve-AiOsSupervisorAssignment.DRY_RUN.ps1`
- `automation/orchestration/validators/Invoke-OrchestrationValidatorChain.DRY_RUN.ps1`
- `automation/orchestration/Run-AiOsOperatorLoop.APPLY.ps1`
- `automation/orchestration/approval_inbox/APPLY_APPROVAL_GATE_001.json`
- `automation/orchestration/commit_packages/COMMIT_PACKAGE_MANIFEST_001.json`
- `automation/orchestration/locks/FILE_LOCK_REGISTRY.example.json`
- `automation/orchestration/operator/AIOS_OPERATOR_RULES.json`
- `automation/orchestration/workers/AIOS_WORKER_PROFILES.json`
- `automation/orchestration/work_packets/complete/20260516-064502-rulebook-foundation.json`
- `automation/orchestration/reports/COMMIT_PACKAGE_ACTIVITY_LEDGER_001.csv`

## Phase 94 Move Readiness

`docs/AI_OS/dispatcher`: ready for move from the active-reference perspective, subject to final pre-move scan.

`docs/AI_OS/orchestration`: not ready for move. Remaining active references exist in disallowed paths and must be retired or explicitly reclassified as non-blocking historical evidence before the folder can move safely.

## Validation Plan

Required validation after edits:

- `git status --short -uall`
- `git diff --stat`
- `git diff --name-status`
- `git diff --check`
- PowerShell parser check for changed `.ps1` files.
- JSON parse check for changed `.json` files.
- Confirm no unauthorized files changed.
- Confirm no delete-only entries.

## Result

Phase 93 retired all allowed dispatcher references and the allowed orchestration references. It did not move folders and did not run APPLY scripts.

Push: NO
