# AI_OS Orchestration Source-of-Truth Map

Date: 2026-05-19

Scope: `automation/orchestration` only.

Mode: approved planning map and audit report only. No files moved. No files deleted. No app code modified. No push. No merge.

## Summary

`automation/orchestration` has both old root-level display fixtures and newer subfolder implementations. The approved planning direction is to keep the subfolder implementation files as canonical where they exist, then update root display scripts and old examples in a later controlled pass.

Several files look like generated or runtime state, but they are still referenced by scripts inside `automation/orchestration`. Do not archive them until the references listed below are updated.

## Approved planning defaults

- Cleanup is not approved by this map.
- Old/example/reference files must not be moved until reference checks pass.
- Runtime/generated state is protected evidence until a retention policy exists.
- `automation/operator/` remains active launcher/legacy-mixed and must not be cleaned until dependency review.
- `docs/AI_OS/**` remains reference/source material until file-by-file classification.
- Trading Lab package ownership remains REVIEW_REQUIRED outside this orchestration map.
- Dashboard remains fixture-driven until API migration to `services/orchestrator/` is approved.

## 1. Worker Registry

### Current Competing Files

- `automation/orchestration/worker_registry.example.json`
- `automation/orchestration/worker_registry.v1.example.json`
- `automation/orchestration/workers/AIOS_WORKER_REGISTRY.json`
- `automation/orchestration/workers/WORKER_REGISTRY.json`
- `automation/orchestration/workers/AIOS_WORKER_PROFILES.json`
- `automation/orchestration/workers/inbox/AIOS_WORKER_INBOX.json`
- `automation/orchestration/claims/WORKER_CLAIM_REGISTRY_001.json`
- `automation/orchestration/worker_lanes/WORKER_LANE_STATUS.example.json`

### Approved Canonical File/Folder

- Canonical worker registry: `automation/orchestration/workers/AIOS_WORKER_REGISTRY.json`
- Canonical worker tools: `automation/orchestration/workers/`
- Canonical profiles: `automation/orchestration/workers/AIOS_WORKER_PROFILES.json`
- Canonical inbox: `automation/orchestration/workers/inbox/AIOS_WORKER_INBOX.json`

### Files To Keep

- `automation/orchestration/workers/AIOS_WORKER_REGISTRY.json`
- `automation/orchestration/workers/AIOS_WORKER_PROFILES.json`
- `automation/orchestration/workers/Get-AiOsWorkerRegistry.DRY_RUN.ps1`
- `automation/orchestration/workers/Get-AiOsWorkerAddressBook.ps1`
- `automation/orchestration/workers/Resolve-AiOsWorkerForPacket.DRY_RUN.ps1`
- `automation/orchestration/workers/Resolve-AiOsNeededWorkers.DRY_RUN.ps1`
- `automation/orchestration/workers/Test-AiOsWorkerRegistryBridge.ps1`
- `automation/orchestration/workers/inbox/`
- `automation/orchestration/workers/WORKER_ROUTING_RULES.md`

### Files To Archive Later

- `automation/orchestration/worker_registry.example.json`
- `automation/orchestration/worker_registry.v1.example.json`
- `automation/orchestration/workers/WORKER_REGISTRY.json`
- `automation/orchestration/worker_lanes/WORKER_LANE_STATUS.example.json`

Archive only after scripts and displays stop reading these paths.

### Files That May Be Runtime/Generated

- `automation/orchestration/workers/inbox/AIOS_WORKER_INBOX.json`
- `automation/orchestration/claims/WORKER_CLAIM_REGISTRY_001.json`
- `automation/orchestration/worker_lanes/WORKER_LANE_STATUS.example.json`

### References To Update First

- `automation/orchestration/orchestration_status_snapshot.example.json` points worker registry input to `worker_registry.example.json`.
- `automation/orchestration/orchestration_spine_v1.example.json` points worker registry source to `automation/orchestration/worker_registry.example.json`.
- `automation/orchestration/show-orchestration-status.ps1` reads the worker registry path from `orchestration_status_snapshot.example.json`.
- `automation/orchestration/show-worker-status.ps1` reads `packet_queue.example.json` and `worker_registry.example.json`.
- `automation/orchestration/sync-worker-registry.ps1` reads `packet_queue.example.json` and `worker_registry.example.json`.

## 2. Queue

### Current Competing Files

- `automation/orchestration/packet_queue.example.json`
- `automation/orchestration/packet_queue_ledger.v1.example.json`
- `automation/orchestration/queue/DISPATCHER_QUEUE.json`
- `automation/orchestration/queue/WORKER_PACKET_QUEUE_001.json`
- `automation/orchestration/queue/WORKER_PACKET_TEMPLATE_001.json`
- `automation/orchestration/command_queue/AIOS_COMMAND_QUEUE.json`
- `automation/orchestration/work_packets/active/*.json`
- `automation/orchestration/work_packets/blocked/*.json`
- `automation/orchestration/work_packets/complete/*.json`
- `automation/orchestration/work_packets/templates/AIOS_WORK_PACKET.template.json`

### Approved Canonical File/Folder

- Canonical queue model: `automation/orchestration/work_packets/`
- Canonical packet creator: `automation/orchestration/work_packets/New-AiOsWorkPacket.ps1`
- Canonical packet state tools:
  - `automation/orchestration/work_packets/Get-AiOsWorkPacketState.ps1`
  - `automation/orchestration/work_packets/Move-AiOsPacketState.ps1`
  - `automation/orchestration/work_packets/Route-AiOsWorkPacket.DRY_RUN.ps1`
- Canonical command queue, if retained separately: `automation/orchestration/command_queue/AIOS_COMMAND_QUEUE.json`

### Files To Keep

- `automation/orchestration/work_packets/`
- `automation/orchestration/work_packets/templates/AIOS_WORK_PACKET.template.json`
- `automation/orchestration/advancement/Invoke-AiOsPacketAdvancement.DRY_RUN.ps1`
- `automation/orchestration/command_queue/AIOS_COMMAND_QUEUE.json`
- `automation/orchestration/command_queue/Add-AiOsCommandQueueItem.DRY_RUN.ps1`
- `automation/orchestration/command_queue/Get-AiOsCommandQueue.DRY_RUN.ps1`

### Files To Archive Later

- `automation/orchestration/packet_queue.example.json`
- `automation/orchestration/packet_queue_ledger.v1.example.json`
- `automation/orchestration/queue/DISPATCHER_QUEUE.json`
- `automation/orchestration/queue/WORKER_PACKET_QUEUE_001.json`
- `automation/orchestration/queue/WORKER_PACKET_TEMPLATE_001.json`

Archive only after display scripts and status snapshots use `automation/orchestration/work_packets/`.

### Files That May Be Runtime/Generated

- `automation/orchestration/work_packets/active/*.json`
- `automation/orchestration/work_packets/blocked/*.json`
- `automation/orchestration/work_packets/complete/*.json`
- `automation/orchestration/packet_queue_ledger.v1.example.json`
- `automation/orchestration/command_queue/AIOS_COMMAND_QUEUE.json`

### References To Update First

- `automation/orchestration/orchestration_status_snapshot.example.json` points queue input to `packet_queue.example.json`.
- `automation/orchestration/orchestration_spine_v1.example.json` points packet queue source to `automation/orchestration/packet_queue.example.json`.
- `automation/orchestration/show-dispatcher-queue.ps1` reads `packet_queue.example.json`.
- `automation/orchestration/show-worker-status.ps1` reads `packet_queue.example.json`.
- `automation/orchestration/sync-worker-registry.ps1` reads `packet_queue.example.json`.
- `automation/orchestration/mission_control/Export-AiOsMissionState.ps1` references `automation/orchestration/packet_queue.example.json`.
- `automation/orchestration/mission_control/aios_mission_state.example.json` references `automation/orchestration/packet_queue.example.json`.
- `automation/orchestration/supervisor/aios_supervisor_state.example.json` references `automation/orchestration/packet_queue.example.json`.

## 3. Approval Inbox

### Current Competing Files

- `automation/orchestration/approval_inbox.example.json`
- `automation/orchestration/approval_inbox.v1.example.json`
- `automation/orchestration/approval_inbox/APPROVAL_INBOX_001.json`
- `automation/orchestration/approval_inbox/APPLY_APPROVAL_GATE_001.json`
- `automation/orchestration/approval_inbox/APPROVAL_STATUS_RULES_001.md`
- `automation/orchestration/approval_runner/APPROVAL_DECISION_REPORT.example.json`
- `automation/orchestration/approval_runner/Get-AiOsApprovalDecision.DRY_RUN.ps1`
- `automation/orchestration/approval_processor/Invoke-AiOsApprovalProcessor.DRY_RUN.ps1`
- `automation/orchestration/approval_detection/Find-AiOsApprovalMatch.DRY_RUN.ps1`
- `automation/orchestration/approvals/APPROVE_PR_73.json`
- `automation/orchestration/approvals/APPROVE_PR_TEMPLATE.json`

### Approved Canonical File/Folder

- Canonical approval inbox: `automation/orchestration/approval_inbox/APPROVAL_INBOX_001.json`
- Canonical approval gate: `automation/orchestration/approval_inbox/APPLY_APPROVAL_GATE_001.json`
- Canonical approval rules: `automation/orchestration/approval_inbox/APPROVAL_STATUS_RULES_001.md`
- Canonical approval decision runner: `automation/orchestration/approval_runner/Get-AiOsApprovalDecision.DRY_RUN.ps1`

### Files To Keep

- `automation/orchestration/approval_inbox/`
- `automation/orchestration/approval_runner/`
- `automation/orchestration/approval_detection/Find-AiOsApprovalMatch.DRY_RUN.ps1`
- `automation/orchestration/approval_processor/Invoke-AiOsApprovalProcessor.DRY_RUN.ps1`

### Files To Archive Later

- `automation/orchestration/approval_inbox.example.json`
- `automation/orchestration/approval_inbox.v1.example.json`
- `automation/orchestration/approvals/APPROVE_PR_73.json`

Keep `automation/orchestration/approvals/APPROVE_PR_TEMPLATE.json` only if PR approval examples remain in scope.

### Files That May Be Runtime/Generated

- `automation/orchestration/approval_inbox/APPROVAL_INBOX_001.json`
- `automation/orchestration/approval_runner/APPROVAL_DECISION_REPORT.example.json`
- `automation/orchestration/approvals/APPROVE_PR_73.json`

### References To Update First

- `automation/orchestration/orchestration_status_snapshot.example.json` points approval input to `approval_inbox.example.json`.
- `automation/orchestration/orchestration_spine_v1.example.json` points approval source to `automation/orchestration/approval_inbox.example.json`.
- `automation/orchestration/show-approval-inbox.ps1` reads `approval_inbox.example.json`.
- `automation/orchestration/show-approval-inbox-v1.ps1` reads `approval_inbox.v1.example.json`.
- `automation/orchestration/show-orchestration-status.ps1` reads approval input from `orchestration_status_snapshot.example.json`.

## 4. Validator Chain

### Current Competing Files

- `automation/orchestration/validator_chain.example.json`
- `automation/orchestration/validator_routing_supervisor.v1.example.json`
- `automation/orchestration/validator_chain_runner/Invoke-AiOsValidatorChain.DRY_RUN.ps1`
- `automation/orchestration/validator_chain_runner/VALIDATOR_CHAIN_RUN_REPORT.example.json`
- `automation/orchestration/validators/VALIDATOR_CHAIN_001.json`
- `automation/orchestration/validators/VALIDATOR_CHAIN_CONFIG_001.json`
- `automation/orchestration/validators/VALIDATOR_CHAIN_RUNBOOK_001.md`
- `automation/orchestration/validators/VALIDATOR_RECOMMENDATION.example.json`
- `automation/orchestration/validators/Invoke-OrchestrationValidatorChain.DRY_RUN.ps1`
- `automation/orchestration/validators/Get-AiOsValidatorRecommendation.DRY_RUN.ps1`
- `automation/orchestration/validators/Test-*.DRY_RUN.ps1`

### Approved Canonical File/Folder

- Canonical validator folder: `automation/orchestration/validators/`
- Canonical validator chain config: `automation/orchestration/validators/VALIDATOR_CHAIN_CONFIG_001.json`
- Canonical validator chain runner: `automation/orchestration/validators/Invoke-OrchestrationValidatorChain.DRY_RUN.ps1`
- Canonical validator recommendation runner: `automation/orchestration/validators/Get-AiOsValidatorRecommendation.DRY_RUN.ps1`

### Files To Keep

- `automation/orchestration/validators/`
- `automation/orchestration/validators/VALIDATOR_CHAIN_CONFIG_001.json`
- `automation/orchestration/validators/VALIDATOR_CHAIN_001.json`
- `automation/orchestration/validators/VALIDATOR_CHAIN_RUNBOOK_001.md`
- `automation/orchestration/validators/Invoke-OrchestrationValidatorChain.DRY_RUN.ps1`
- `automation/orchestration/validators/Get-AiOsValidatorRecommendation.DRY_RUN.ps1`
- `automation/orchestration/validators/Test-*.DRY_RUN.ps1`

### Files To Archive Later

- `automation/orchestration/validator_chain.example.json`
- `automation/orchestration/validator_routing_supervisor.v1.example.json`
- `automation/orchestration/validator_chain_runner/`

Archive only after root display scripts and status snapshots use `automation/orchestration/validators/`.

### Files That May Be Runtime/Generated

- `automation/orchestration/validator_chain_runner/VALIDATOR_CHAIN_RUN_REPORT.example.json`
- `automation/orchestration/validators/VALIDATOR_RECOMMENDATION.example.json`
- `automation/orchestration/reports/VALIDATOR_CHAIN_ACTIVITY_LEDGER_001.csv`

### References To Update First

- `automation/orchestration/orchestration_status_snapshot.example.json` points validator input to `validator_chain.example.json`.
- `automation/orchestration/orchestration_spine_v1.example.json` points validator source to `automation/orchestration/validator_chain.example.json`.
- `automation/orchestration/show-validator-chain.ps1` reads `validator_chain.example.json`.
- `automation/orchestration/show-validator-routing-supervisor.ps1` reads `validator_routing_supervisor.v1.example.json`.
- `automation/orchestration/show-orchestration-status.ps1` reads validator input from `orchestration_status_snapshot.example.json`.

## 5. Commit Package Flow

### Current Competing Files

- `automation/orchestration/commit_package.example.json`
- `automation/orchestration/commit_packages/COMMIT_PACKAGE_MANIFEST_001.json`
- `automation/orchestration/commit_packages/COMMIT_PACKAGE_RECOMMENDATION.example.json`
- `automation/orchestration/commit_packages/COMMIT_PACKAGE_RULES_001.md`
- `automation/orchestration/commit_packages/COMMIT_PACKAGE_TEMPLATE_001.json`
- `automation/orchestration/commit_packages/New-AiOsCommitPackageRecommendation.DRY_RUN.ps1`
- `automation/orchestration/validators/New-CommitPackagePreview.DRY_RUN.ps1`
- `automation/orchestration/validators/Test-CommitPackageManifest.DRY_RUN.ps1`
- `automation/orchestration/show-commit-package.ps1`
- `automation/orchestration/git/Submit-AiOsWork.ps1`

### Approved Canonical File/Folder

- Canonical commit package folder: `automation/orchestration/commit_packages/`
- Canonical recommendation runner: `automation/orchestration/commit_packages/New-AiOsCommitPackageRecommendation.DRY_RUN.ps1`
- Canonical rules: `automation/orchestration/commit_packages/COMMIT_PACKAGE_RULES_001.md`

### Files To Keep

- `automation/orchestration/commit_packages/`
- `automation/orchestration/commit_packages/New-AiOsCommitPackageRecommendation.DRY_RUN.ps1`
- `automation/orchestration/commit_packages/COMMIT_PACKAGE_RULES_001.md`
- `automation/orchestration/commit_packages/COMMIT_PACKAGE_TEMPLATE_001.json`
- `automation/orchestration/validators/Test-CommitPackageManifest.DRY_RUN.ps1`

### Files To Archive Later

- `automation/orchestration/commit_package.example.json`
- `automation/orchestration/validators/New-CommitPackagePreview.DRY_RUN.ps1`

Archive only after `show-commit-package.ps1` and any old docs point to `automation/orchestration/commit_packages/`.

### Files That May Be Runtime/Generated

- `automation/orchestration/commit_packages/COMMIT_PACKAGE_MANIFEST_001.json`
- `automation/orchestration/commit_packages/COMMIT_PACKAGE_RECOMMENDATION.example.json`
- `automation/orchestration/reports/COMMIT_PACKAGE_ACTIVITY_LEDGER_001.csv`
- `automation/orchestration/commit_package.example.json`

### References To Update First

- `automation/orchestration/orchestration_spine_v1.example.json` points commit packaging source to `automation/orchestration/commit_package.example.json`.
- `automation/orchestration/show-commit-package.ps1` reads `commit_package.example.json`.
- `automation/orchestration/validators/VALIDATOR_CHAIN_CONFIG_001.json` includes `commit_package_review`.
- `automation/orchestration/validators/VALIDATOR_CHAIN_RUNBOOK_001.md` documents `commit_package_review`.

## 6. Supervisor / Control Loop

### Current Competing Files

- `automation/orchestration/Run-AiOsOperatorLoop.DRY_RUN.ps1`
- `automation/orchestration/Run-AiOsOperatorLoop.APPLY.ps1`
- `automation/orchestration/control/Get-AiOsOperatorControlLoop.DRY_RUN.ps1`
- `automation/orchestration/control/OPERATOR_CONTROL_LOOP.example.json`
- `automation/orchestration/control_summary/Get-AiOsControlSummary.DRY_RUN.ps1`
- `automation/orchestration/control_summary/CONTROL_SUMMARY_REPORT.example.json`
- `automation/orchestration/supervisor/Start-AiOsSupervisor.ps1`
- `automation/orchestration/supervisor/Invoke-AiOsSupervisorLoop.DRY_RUN.ps1`
- `automation/orchestration/supervisor/Resolve-AiOsSupervisorAssignment.DRY_RUN.ps1`
- `automation/orchestration/supervisor/aios_supervisor_state.example.json`
- `automation/orchestration/supervisor/aios_supervision_rules.example.json`
- `automation/orchestration/runtime/Start-AiOsPersistentRuntimeSupervisor.ps1`
- `automation/orchestration/runtime/Start-AiOsRuntimeCycle.DRY_RUN.ps1`
- `automation/orchestration/runtime/Invoke-AiOsRuntimeSelfRoute.ps1`
- `automation/orchestration/runtime/Invoke-AiOsRuntimePacketAdvancement.ps1`
- `automation/orchestration/daemon/Start-AiOsRuntimeDaemon.DRY_RUN.ps1`
- `automation/orchestration/persistent_worker_supervisor.v1.example.json`
- `automation/orchestration/launch_supervisor.v1.example.json`
- `automation/orchestration/queue_health_supervisor.v1.example.json`

### Approved Canonical File/Folder

- Canonical operator control loop: `automation/orchestration/control/Get-AiOsOperatorControlLoop.DRY_RUN.ps1`
- Canonical supervisor folder: `automation/orchestration/supervisor/`
- Canonical runtime folder, only for persistent/repeated cycles: `automation/orchestration/runtime/`

Important: `automation/orchestration/Run-AiOsOperatorLoop.APPLY.ps1` currently contains branch creation, staging, commit, and push behavior. It should not be canonical for near-term safe operation.

### Files To Keep

- `automation/orchestration/control/`
- `automation/orchestration/supervisor/`
- `automation/orchestration/runtime/`
- `automation/orchestration/health/Test-AiOsRuntimeHealth.DRY_RUN.ps1`
- `automation/orchestration/recommendations/Get-AiOsActionRecommendation.DRY_RUN.ps1`

### Files To Archive Later

- `automation/orchestration/Run-AiOsOperatorLoop.DRY_RUN.ps1`
- `automation/orchestration/Run-AiOsOperatorLoop.APPLY.ps1`
- `automation/orchestration/persistent_worker_supervisor.v1.example.json`
- `automation/orchestration/launch_supervisor.v1.example.json`
- `automation/orchestration/queue_health_supervisor.v1.example.json`
- `automation/orchestration/daemon/Start-AiOsRuntimeDaemon.DRY_RUN.ps1`

Archive or disable `Run-AiOsOperatorLoop.APPLY.ps1` only after MAIN CONTROL approves, because it includes push behavior and may be unsafe as an active entrypoint.

### Files That May Be Runtime/Generated

- `automation/orchestration/control/OPERATOR_CONTROL_LOOP.example.json`
- `automation/orchestration/control_summary/CONTROL_SUMMARY_REPORT.example.json`
- `automation/orchestration/supervisor/aios_supervisor_state.example.json`
- `automation/orchestration/runtime/*` outputs if created later
- `automation/orchestration/memory/AIOS_RUNTIME_MEMORY.json`

### References To Update First

- `automation/orchestration/advancement/Invoke-AiOsPacketAdvancement.DRY_RUN.ps1` calls `automation/orchestration/supervisor/Invoke-AiOsSupervisorLoop.DRY_RUN.ps1`.
- `automation/orchestration/health/Test-AiOsRuntimeHealth.DRY_RUN.ps1` checks `automation/orchestration/supervisor/Invoke-AiOsSupervisorLoop.DRY_RUN.ps1`.
- `automation/orchestration/bootstrap/Test-AiOsWorkspaceBootstrap.DRY_RUN.ps1` recommends `Start-AiOsWork.ps1` as primary operator entrypoint and calls `automation/orchestration/supervisor/Resolve-AiOsSupervisorAssignment.DRY_RUN.ps1`.
- `automation/orchestration/terminal_workstations/Show-AiOsOperatorMenu.ps1` points to `automation/orchestration/supervisor/Start-AiOsSupervisor.ps1`.

## 7. Operator Status Command

### Current Competing Files

- `automation/orchestration/show-orchestration-status.ps1`
- `automation/orchestration/control/Get-AiOsOperatorControlLoop.DRY_RUN.ps1`
- `automation/orchestration/control_summary/Get-AiOsControlSummary.DRY_RUN.ps1`
- `automation/orchestration/health_summary/Get-AiOsOrchestrationHealth.DRY_RUN.ps1`
- `automation/orchestration/health/Test-AiOsRuntimeHealth.DRY_RUN.ps1`
- `automation/orchestration/show-orchestration-spine.ps1`
- `automation/orchestration/show-orchestration-control-state.ps1`
- `automation/orchestration/show-orchestration-gaps.ps1`
- `automation/orchestration/show-dispatcher-queue.ps1`
- `automation/orchestration/show-worker-status.ps1`
- `automation/orchestration/show-approval-inbox.ps1`
- `automation/orchestration/show-validator-chain.ps1`
- `automation/orchestration/show-commit-package.ps1`
- `automation/orchestration/terminal_workstations/Show-AiOsOperatorMenu.ps1`

### Approved Canonical File/Folder

- Canonical operator status command: `automation/orchestration/control/Get-AiOsOperatorControlLoop.DRY_RUN.ps1`
- Canonical status summaries: `automation/orchestration/control_summary/` and `automation/orchestration/health_summary/`
- Legacy display compatibility: keep `automation/orchestration/show-orchestration-status.ps1` until all root examples are retired.

### Files To Keep

- `automation/orchestration/control/Get-AiOsOperatorControlLoop.DRY_RUN.ps1`
- `automation/orchestration/control/OPERATOR_CONTROL_LOOP.example.json`
- `automation/orchestration/control_summary/Get-AiOsControlSummary.DRY_RUN.ps1`
- `automation/orchestration/health_summary/Get-AiOsOrchestrationHealth.DRY_RUN.ps1`
- `automation/orchestration/health/Test-AiOsRuntimeHealth.DRY_RUN.ps1`
- `automation/orchestration/terminal_workstations/Show-AiOsOperatorMenu.ps1`

### Files To Archive Later

- Root `show-*` scripts after their data sources are folded into `control/Get-AiOsOperatorControlLoop.DRY_RUN.ps1`.
- `automation/orchestration/show-orchestration-status.ps1` after it is replaced by the canonical control command.
- `automation/orchestration/orchestration_status_snapshot.example.json` after canonical status inputs are no longer root examples.

### Files That May Be Runtime/Generated

- `automation/orchestration/orchestration_status_snapshot.example.json`
- `automation/orchestration/control/OPERATOR_CONTROL_LOOP.example.json`
- `automation/orchestration/control_summary/CONTROL_SUMMARY_REPORT.example.json`
- `automation/orchestration/health_summary/ORCHESTRATION_HEALTH_REPORT.example.json`
- `automation/orchestration/reports/ORCHESTRATION_STATUS_SNAPSHOT_001.md`

### References To Update First

- `automation/orchestration/terminal_workstations/Start-AiOsTelemetryDeck.ps1` points to `automation/orchestration/show-orchestration-status.ps1`.
- `automation/orchestration/orchestration_status_snapshot.example.json` points to root status inputs.
- `automation/orchestration/show-orchestration-status.ps1` reads `orchestration_status_snapshot.example.json`.
- `automation/orchestration/terminal_workstations/Show-AiOsOperatorMenu.ps1` lists separate status commands rather than one canonical status command.

## Cross-Cutting Archive Candidates

Do not archive now. Later candidates after reference updates:

- root `*.example.json` display fixtures that have canonical subfolder replacements
- root `show-*` scripts replaced by canonical control status output
- `automation/orchestration/reports/*.csv`
- `automation/orchestration/reports/ORCHESTRATION_STATUS_SNAPSHOT_001.md`
- `automation/orchestration/validator_chain_runner/`
- duplicate root supervisor example files

## Immediate Next Safe Action

1. Approve the canonical paths above as MAIN CONTROL doctrine.
2. Update display/status scripts to read canonical subfolder paths.
3. Run reference searches for each old root example path.
4. Only then move old examples and redundant display scripts to `archive/orchestration_legacy`.

No file should be moved or deleted from `automation/orchestration` before these reference updates are complete.
