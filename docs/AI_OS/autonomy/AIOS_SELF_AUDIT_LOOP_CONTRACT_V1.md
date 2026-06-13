# AIOS Self-Audit Loop Contract v1

## 1. Purpose

AIOS self-audit is a console-only, read-only inspection loop.

It helps AIOS inspect itself, classify gaps, rank next candidate packets, and stop. It does not execute work. It does not approve work. It does not write reports. It does not mutate the repo. It does not launch runtime, workers, scheduler, daemon, queues, or trading paths.

The purpose of this contract is to let AIOS move toward safer self-development without granting execution authority.

## 2. Operating Rule

AIOS may inspect, classify, rank, and recommend. AIOS may not write, mutate, launch, approve, enqueue, execute, or trade.

## 3. Allowed Inputs

AIOS may read:

- `AGENTS.md`
- `README.md`
- `RISK_POLICY.md`
- campaign registry JSON
- no-ready-stage discovery output
- campaign next-task selector output
- action recommendation output
- relay/SOS state
- validator definitions
- packet generator contracts
- commit package preview output
- approval/lock/worker collision validators
- dashboard, telemetry, Trading Lab, Forex/OANDA docs
- test files as static evidence
- git status, git log, and git diff metadata

## 4. Allowed Outputs

AIOS may print to console:

- current state
- repo cleanliness
- campaign state
- self-audit findings
- surface classifications
- gap classifications
- candidate packet IDs
- candidate packet intent
- required approvals
- blockers
- next safe review action

AIOS must not write:

- `Reports`
- telemetry
- evidence files
- packet drafts
- proposed work packets
- relay messages
- registry changes
- queue changes
- lock changes
- approval changes
- runtime state
- dashboard files
- service/app files

## 5. Surface Classification Rules

`SAFE_READ_ONLY`:
May be used directly by the self-audit loop if it prints or returns evidence without writing.

`WRITES_REPORTS_OR_EVIDENCE`:
Must be excluded from the no-write loop unless a future packet proves a console-only mode.

`GENERATES_PACKET_DRAFT_ONLY`:
May be used only as preview evidence. It must not write packet files, create READY stages, approve APPLY, or enqueue work.

`MUTATES_STATE_OR_PROTECTED_SURFACE`:
Forbidden in the self-audit loop.

`UNKNOWN_NEEDS_REVIEW`:
Forbidden until a focused DRY_RUN review classifies it.

## 6. Approved Read-Only Candidate Surfaces

These are candidate safe surfaces, subject to normal validation:

- `automation/orchestration/campaign_registry/Get-AiOsCampaignNoReadyStageDiscovery.DRY_RUN.ps1`
- `automation/orchestration/campaign_registry/Get-AiOsCampaignNextTask.DRY_RUN.ps1`
- `automation/orchestration/recommendations/Get-AiOsActionRecommendation.DRY_RUN.ps1` as evidence only
- `automation/orchestration/autonomy_control_plane/aios_self_build_cycle_composer.py`
- `automation/orchestration/autonomy_router/aios_next_action_decider.py`
- `automation/orchestration/packet_generator/Test-AiOsCodexPacket.DRY_RUN.ps1`
- `automation/orchestration/validators/Invoke-OrchestrationValidatorChain.DRY_RUN.ps1`
- `automation/orchestration/validators/Test-ApplyApprovalGate.DRY_RUN.ps1`
- `automation/orchestration/validators/Test-ApprovalInboxIntegrity.DRY_RUN.ps1`
- `automation/orchestration/validators/Test-LockRegistryIntegrity.DRY_RUN.ps1`
- `automation/orchestration/validators/Test-WorkerClaimCollision.DRY_RUN.ps1`
- `automation/orchestration/validators/New-CommitPackagePreview.DRY_RUN.ps1`
- `automation/orchestration/relay_bus/Get-AiOsRelayBusState.DRY_RUN.ps1`
- `automation/orchestration/relay_bus/Get-AiOsSosEscalationPolicy.DRY_RUN.ps1`
- `automation/orchestration/relay_bus/Resolve-AiOsRelayHumanReview.DRY_RUN.ps1`
- `automation/orchestration/review_bridge/Get-AiOsRelayOperatorState.DRY_RUN.ps1`
- `automation/telemetry/Preview-AiOsTelemetry.DRY_RUN.ps1`
- `automation/reporting/Preview-AiOsDailyReport.DRY_RUN.ps1`

## 7. Excluded Write-Capable Surfaces

These are excluded from the no-write self-audit loop:

- `automation/self_build/aios_self_build_cycle.py`
- `automation/self_build/aios_self_build_inspector.py`
- `automation/orchestration/autonomy_reports/aios_self_build_evidence_persister.py`
- `automation/orchestration/autonomy_reports/aios_self_build_evidence_ledger.py` when output path is used
- `automation/orchestration/autonomy_control_plane/Invoke-AiOsAutonomyControlPlane.DRY_RUN.ps1`
- `automation/orchestration/autonomy_router/Get-AiOsAutonomyNextAction.DRY_RUN.ps1`
- `automation/orchestration/autonomy_router/aios_decision_to_packet_drafter.py` when file output is used
- `automation/orchestration/autonomy_loop/Invoke-AiOsAutonomyLoop.DRY_RUN.ps1`
- `automation/orchestration/autonomy_discovery/Get-AiOsAutonomyInventory.DRY_RUN.ps1`
- `automation/orchestration/review_bridge/New-AiOsCodexReportRelayItem.DRY_RUN.ps1`
- `automation/orchestration/reports/New-AiOsMorningBrief.ps1`
- `automation/telemetry/Update-AiOsProductionReadout.ps1`
- `automation/reporting/New-AiOsReport.ps1`
- `automation/orchestration/commit_packages/Invoke-AiOsExactCommitPackage.ps1`
- `automation/orchestration/relay_bus/New-AiOsRelayMessage.DRY_RUN.ps1` when used in APPLY/write mode

## 8. Packet Recommendation Boundary

AIOS may recommend candidate packet IDs and packet intent in console output only.

AIOS must not:

- create READY stages
- mutate the campaign registry
- write packet drafts
- write proposed work packets
- approve APPLY
- enqueue work
- launch workers
- run protected git actions
- recommend APPLY execution as a next safe action

## 9. SOS / Anthony Wake Boundary

Routine review may be classified.

SOS escalation requires Anthony. Anthony-required review requires Anthony. Secrets, credentials, `.env`, broker, OANDA, webhook, order, live trading, approval mutation, queue mutation, lock mutation, runtime start, worker launch, scheduler, daemon, commit, push, PR, or merge require Anthony.

## 10. Stop Conditions

The self-audit loop must stop if:

- `AGENTS.md`, `README.md`, or `RISK_POLICY.md` is missing
- worktree is dirty outside explicit review scope
- registry inconsistency is detected
- unknown or write-capable surface is selected
- `Reports`/evidence write path is selected
- telemetry write path is selected
- runtime/worker/scheduler/daemon command is surfaced
- queue/lock/approval mutation is surfaced
- broker/OANDA/webhook/order/live-trading path is surfaced
- secrets, credentials, or `.env` use is detected
- protected git action is proposed
- confidence is insufficient

## 11. Future Runner Requirements

A future implementation packet may build a console-only self-audit runner only after this contract is merged.

That runner must prove:

- no file writes
- no `Reports` writes
- no telemetry writes
- no registry mutation
- no packet file writes
- no relay writes
- no queue/lock/approval mutation
- no runtime/worker/scheduler/daemon launch
- no broker/OANDA/webhook/order/live-trading path
- no protected git action
- console output only

## 12. Non-Goals

This contract does not enable day/night autonomy.

This contract does not enable runtime autonomy.

This contract does not enable worker launch.

This contract does not enable dashboard implementation.

This contract does not enable live trading.

This contract does not enable auto-approval.

This contract does not make AIOS fully autonomous.
