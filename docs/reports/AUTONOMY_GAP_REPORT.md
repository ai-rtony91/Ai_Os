# Autonomy Gap Report

Packet: AIOS-AUTONOMY-DOCS-SYNTHESIS-DRYRUN-001
Mode: DRY_RUN report creation only
Branch inspected: phase-night-supervisor-layer2-memory
Worktree: C:\Dev\Ai.Os

## Central Answer

If Anthony disappeared for 30 days but continued approving decisions, AI_OS could not yet safely continue supervised development work end to end.

It can inspect, recommend, classify, preview, validate parts of the workflow, and prepare some commit package evidence. It cannot yet autonomously maintain a durable task graph, safely route all work, recover routine failures, arbitrate conflicts, prepare approvals intelligently, or measure autonomy without Anthony acting as the integration layer.

Current AI_OS is a strong supervised orchestration workbench. It is not yet a supervised autonomous development environment.

## Authority Reconciliation

Repository authority wins over the three supplied autonomy documents.

Key conflicts:

| Source material claim | Repo authority | Winning rule |
|---|---|---|
| Write `docs/security/sos-escalation-policy.md` first | Current packet allowed writes only under `docs/reports/` | Report the need only. Do not create security docs in this packet. |
| Add `docs/architecture/toolchain-mcp-safe-hands.md` and pointer line | Current packet says do not edit `docs/architecture/` or existing docs outside reports | Report as next APPLY lane. Do not execute. |
| Night Builder eventually opens PRs | `AGENTS.md`, `README.md`, approval model, and autonomy levels require separate explicit approval for PR creation | PR creation remains human-approved until a future gate explicitly allows it. |
| "Autonomous development while asleep" | `docs/workflows/AI_OS_OVERNIGHT_SUPERVISOR_WORKFLOW.md` defines report-first read-only supervision only | Overnight must begin as read-only morning brief and packet draft preview. |
| Automatic recovery | `docs/workflows/SAFE_REPAIR_AND_RECOVERY_STANDARD.md` says repair output is evidence and planning, not approval | Recovery may detect and recommend; mutation requires approved APPLY. |

## Autonomy Layer Status Table

Scores: 0 missing, 1 documented only, 2 partial scaffold, 3 partial wired, 4 mostly implemented, 5 ready for supervised autonomy.

| Layer | Status | Score | Evidence | Main gap |
|---|---:|---:|---|---|
| 01 Knowledge Graph | PARTIAL | 2 | `docs/governance/source-of-truth-map.md`, `docs/audits/active-system-map.md`, `docs/governance/runtime-ownership-map.md` | No runtime-loadable graph or dependency query. |
| 02 Goal Intake | PARTIAL | 2 | `automation/intake/Convert-AiOsInputToPacketProposal.DRY_RUN.ps1`, `Invoke-AiOsGoalIntake.ps1` | Proposal and simple APPLY writer exist, but no robust decomposition into task graph. |
| 03 Task Graph Engine | PARTIAL | 2 | `services/dispatcher/executionGraph.ts`, campaign registry dependency fields | Dependency graph exists in code/registry, not unified with packets and queue. |
| 04 Worker Registry | PARTIAL | 3 | `automation/orchestration/workers/AIOS_WORKER_REGISTRY.json`, `AIOS_WORKER_PROFILES.json`, `automation/window_identity/AIOS_WORKER_REGISTRY.json` | Duplicate logical/window registries remain ambiguous. |
| 05 Queue System | PARTIAL | 3 | `automation/orchestration/work_packets/`, `command_queue/AIOS_COMMAND_QUEUE.json`, `queue/DISPATCHER_QUEUE.json`, `services/dispatcher/packetQueue.ts` | Multiple queue concepts and no single durable canonical projection. |
| 06 Event Bus | PARTIAL | 2 | `schemas/aios/orchestration/EVENT_SCHEMA.md`, `services/runtime/eventBus.ts`, telemetry ledger | Contract and in-memory bus differ; no append-only orchestration event bus. |
| 07 Validator Routing | PARTIAL | 3 | `VALIDATOR_CHAIN_CONFIG_001.json`, `AIOS_VALIDATOR_ROUTER_RULES.example.json`, validator scripts | Rules exist, but automatic changed-file to validator execution is not closed. |
| 08 Conflict Arbitration | PARTIAL | 2 | lock schemas, `PATH_CONFLICT_POLICY_001.md`, claim/collision validators | Detection exists; ordered arbitration policy and automatic safe resolution are incomplete. |
| 09 Recovery Supervisor | PARTIAL | 2 | `services/supervisor/runtimeSupervisor.ts`, `runtimeStateRebuilder.ts`, recovery docs, Night Supervisor gates | Recovery is mostly awareness/reporting; no qualified safe recovery executor. |
| 10 Self Audit | PARTIAL | 2 | active system map, source-of-truth map, work intelligence scan, topology/source validators | Audits exist as passes; no scheduled self-audit with narrow auto-remediation. |
| 11 Approval Intelligence | PARTIAL | 2 | `docs/security/approval-model.md`, approval gate JSON, approval inbox scripts | Active approval inbox file is missing; no risk-ranked approval bundling. |
| 12 Commit Package Intelligence | PARTIAL | 3 | `automation/orchestration/commit_packages/`, recommender, commit package gate | Strong preview, no automatic diff grouping by dependency graph. |
| 13 Autonomy Scorecard | DOCUMENTED ONLY | 1 | autonomy levels, telemetry concepts, report references | No scorecard model measuring human dependency, recovery rate, routing rate. |

## Layer Findings

### 01 Knowledge Graph

Status: PARTIAL.
Readiness: 2/5.

What exists:

- Source-of-truth structure in `docs/governance/source-of-truth-map.md`.
- Active system map in `docs/audits/active-system-map.md`.
- Runtime ownership map in `docs/governance/runtime-ownership-map.md`.
- Folder ownership maps and placement rules under `docs/governance/`.
- Execution classification registry in `automation/orchestration/execution_registry/AIOS_EXECUTION_CLASSIFICATION_REGISTRY.json`.

What is missing:

- A runtime-loadable repo graph artifact.
- System-to-file dependency edges.
- Protected asset ownership in machine-readable query form.
- Decision history linked to authority files.
- Fast answer to "what breaks if file X changes?"

Dependency:

This must precede reliable goal intake, task graph generation, validator routing, conflict arbitration, approval intelligence, and commit packaging.

### 02 Goal Intake

Status: PARTIAL.
Readiness: 2/5.

What exists:

- `automation/intake/Convert-AiOsInputToPacketProposal.DRY_RUN.ps1` can scan `inputs/pending` and produce packet proposals in preview.
- `automation/intake/Invoke-AiOsGoalIntake.ps1` turns a simple goal into a goal intake record and, with `-Apply`, can call `New-AiOsWorkPacket.ps1`.
- `automation/orchestration/recommendations/Get-AiOsNextPacketRecommendation.DRY_RUN.ps1` recommends next packet actions based on input and packet counts.

What is missing:

- Multi-step decomposition from "Build X" into a validated dependency graph.
- Risk tagging integrated with the classification registry and protected path ownership.
- Human approval checkpoint for proposed task graph.
- Consistent separation between packet proposal, queue insertion, approval request, and worker assignment.

### 03 Task Graph Engine

Status: PARTIAL.
Readiness: 2/5.

What exists:

- `services/dispatcher/executionGraph.ts` contains dependency-aware graph code.
- `automation/orchestration/campaign_registry/AIOS_STRATEGIC_CAMPAIGN_REGISTRY.json` uses `depends_on`, `blocked_by`, and selection policies.
- `schemas/aios/orchestration/supervisor_queue.schema.json` includes `dependency_ids`.

What is missing:

- Unified task graph over real work packets.
- Blocker propagation from queue, approval, validator, worker, and lock state.
- Graph executor that remains read-only until approval.
- Graph visualization or query surface for operator review.

### 04 Worker Registry

Status: PARTIAL.
Readiness: 3/5.

What exists:

- Canonical orchestration worker registry: `automation/orchestration/workers/AIOS_WORKER_REGISTRY.json`.
- Capability-heavy profiles: `automation/orchestration/workers/AIOS_WORKER_PROFILES.json`.
- Runtime/terminal identity registry: `automation/window_identity/AIOS_WORKER_REGISTRY.json`.
- Active system map explicitly flags dual registry dependency.

Overlap:

- Orchestration registry owns logical worker roles.
- Window identity registry owns visible terminal/window labels.
- Profiles contain stronger lane, path, branch, and risk ceiling information than the basic registry.

Contradiction:

- Some docs call the orchestration registry canonical, while `Get-AiOsWorkerAddressBook.ps1` and active-system-map still depend on both orchestration and window identity registries.

Recommendation:

Keep orchestration registry plus worker profiles as the capability authority. Keep window identity as runtime/display binding only, referencing worker IDs instead of duplicating capability authority.

### 05 Queue System

Status: PARTIAL.
Readiness: 3/5.

What exists:

- Work packet folders under `automation/orchestration/work_packets/`.
- Command queue: `automation/orchestration/command_queue/AIOS_COMMAND_QUEUE.json`.
- Dispatcher queue: `automation/orchestration/queue/DISPATCHER_QUEUE.json`.
- Worker packet queue example: `automation/orchestration/queue/WORKER_PACKET_QUEUE_001.json`.
- TypeScript packet queue engine: `services/dispatcher/packetQueue.ts`.

Problem:

AI_OS has several queue-like stores. They do not yet converge into one durable source of "what work exists now."

Needed boundary:

- Work packet: durable unit of work.
- Command: transient instruction/request related to a packet.
- Queue projection: one canonical state view derived from packet, approval, validator, and worker evidence.

### 06 Event Bus

Status: PARTIAL.
Readiness: 2/5.

What exists:

- Contract event family in `schemas/aios/orchestration/EVENT_SCHEMA.md`.
- In-memory runtime event bus in `services/runtime/eventBus.ts`.
- Telemetry event writer in `services/telemetry/telemetryWriter.ts`.
- Telemetry governance contract in `docs/governance/telemetry-contract.md`.

Contradiction:

- `EVENT_SCHEMA.md` uses orchestration events like `work_packet_created`, `validator_passed`, and `commit_package_recommended`.
- `services/runtime/eventBus.ts` uses runtime-only events like `runtime_started`, `runtime_tick_completed`, and `policy_decision`.
- `services/telemetry/telemetryEvent.ts` uses camelCase fields and events such as `packet_dispatched`, while governance wants snake_case canonical fields.

Needed:

An append-only orchestration event log with one versioned schema and a mapper from legacy/current telemetry events.

### 07 Validator Routing

Status: PARTIAL.
Readiness: 3/5.

What exists:

- `automation/orchestration/validators/VALIDATOR_CHAIN_CONFIG_001.json`.
- `automation/orchestration/validators/AIOS_VALIDATOR_ROUTER_RULES.example.json`.
- `docs/workflows/VALIDATOR_EXECUTION_STANDARD.md`.
- Many DRY_RUN validators under `automation/orchestration/validators/`.
- Execution classification registry for script risk.

Missing:

- A canonical "changed files -> validators -> result package" router.
- Automatic run rules for safe read-only validators after packet completion.
- Stable result schema enforcement across all validators.

### 08 Conflict Arbitration

Status: PARTIAL.
Readiness: 2/5.

What exists:

- Lock schemas under `schemas/aios/orchestration/`.
- `automation/orchestration/locks/PATH_CONFLICT_POLICY_001.md`.
- `automation/orchestration/validators/Test-WorkerClaimCollision.DRY_RUN.ps1`.
- Claim registry `automation/orchestration/claims/WORKER_CLAIM_REGISTRY_001.json`.
- Worker lane collision checks.

Missing:

- Ordered arbitration table for duplicate packets, validator disagreement, branch conflicts, and worker path collisions.
- Rule-driven dedupe policy at queue insert.
- "Stricter validator wins" policy encoded in machine-readable form.
- Escalation thresholds tied to SOS policy.

### 09 Recovery Supervisor

Status: PARTIAL.
Readiness: 2/5.

What exists:

- `services/supervisor/runtimeSupervisor.ts` generates health and alerts.
- `services/dispatcher/runtimeStateRebuilder.ts` rebuilds dispatcher state from telemetry replay.
- `services/runtime/autonomousRemediation.ts` generates remediation plans.
- `automation/recovery/` and `automation/orchestration/recovery/` contain recovery plans.
- `docs/governance/AIOS_NIGHT_SUPERVISOR_QUALIFICATION_GATES.md` defines Gate 1-7 safety.

Missing:

- Qualified recovery executor.
- Crash-survivable event replay as authority.
- Approved quarantine behavior.
- SOS escalation policy.
- Real-world multi-night evidence and qualification ledger.

### 10 Self Audit

Status: PARTIAL.
Readiness: 2/5.

What exists:

- Active system and source-of-truth maps.
- Work intelligence scan scripts under `automation/work_intelligence/`.
- Source-of-truth resolver and topology guards.
- Numerous audit reports under `docs/audits/`.

Missing:

- Recurring self-audit job.
- Narrow auto-remediation list.
- Drift detector comparing repo graph to filesystem, queues, validators, workers, approvals, and runtime state.
- Morning report integration tied to scorecard.

### 11 Approval Intelligence

Status: PARTIAL.
Readiness: 2/5.

What exists:

- `docs/security/approval-model.md`.
- `automation/orchestration/approval_inbox/APPLY_APPROVAL_GATE_001.json`.
- Approval status rules and scripts.
- Approval tier policy.

Observed issue:

- `automation/orchestration/approval_inbox/APPROVAL_INBOX_001.json` is missing in the active path, even though active-system-map lists it as active. An archive copy exists. This is a repo-state mismatch.

Missing:

- Approval ranking by risk and unblock value.
- Bundling of related approvals.
- Risk explanations sourced from knowledge graph.
- Recommendation text that remains explicitly non-authoritative.

### 12 Commit Package Intelligence

Status: PARTIAL.
Readiness: 3/5.

What exists:

- `automation/orchestration/commit_packages/New-AiOsCommitPackageRecommendation.DRY_RUN.ps1`.
- Commit package manifest and rules.
- `docs/workflows/AI_OS_COMMIT_PUSH_GATE.md`.
- Exact-file staging doctrine in `AGENTS.md`.

Missing:

- Dependency-aware grouping.
- Automatic validator evidence attachment.
- PR candidate preparation flow that stops before PR creation unless separately approved.
- Integration with approval intelligence.

### 13 Autonomy Scorecard

Status: DOCUMENTED ONLY.
Readiness: 1/5.

What exists:

- `docs/governance/AI_OS_AUTONOMY_LEVELS.md`.
- Telemetry concepts and runtime visibility models.
- Prior report references to autonomy scorecard.

Missing:

- Scorecard schema.
- Metrics pipeline for auto-routed, auto-validated, auto-recovered, auto-packaged, and human-intervention counts.
- Distinction between healthy human decisions and wasteful human coordination.
- Dashboard or morning brief projection.

## Top Repository-Specific Missing Systems

1. Runtime-loadable AI_OS knowledge graph.
2. Safe MCP read-only evidence bridge.
3. Canonical durable queue projection.
4. Unified append-only orchestration event log.
5. Worker registry consolidation and display binding separation.
6. Validator router over changed files and packet state.
7. SOS escalation policy.
8. Recovery supervisor qualification ledger and drills.
9. Approval intelligence over the approval inbox/gate.
10. Autonomy scorecard backed by telemetry.
