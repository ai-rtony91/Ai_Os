# Implementation Sequence Report

Packet: AIOS-AUTONOMY-DOCS-SYNTHESIS-DRYRUN-001
Mode: DRY_RUN report creation only
Branch inspected: phase-night-supervisor-layer2-memory
Worktree: C:\Dev\Ai.Os

## Dependency Order

AI_OS should not build the visible Night Builder first. It should build the substrate first.

Strict sequence:

```text
Phase 0  MCP Foundation
Phase 1  Knowledge Graph
Phase 2  Worker Registry Consolidation
Phase 3  Event Schema and Event Log
Phase 4  Queue + Scheduler Projection
Phase 5  Validator Routing
Phase 6  Recovery Supervisor
Phase 7  Approval Intelligence
Phase 8  Commit Package Builder
Phase 9  Autonomy Scorecard
Phase 10 Night Builder Read-Only
Phase 11 Supervised Execution Expansion
```

The user-requested phase list stops at Phase 9. This report adds Phase 10-11 as downstream gates, not immediate work.

## Phase 0: MCP Foundation

Goal: create safe hands for read-only evidence inspection.

Current evidence:

- `docs/workflows/AI_OS_MCP_PROTOTYPE_PLAN.md`
- `services/python_supervisor/README.md`
- `schemas/aios/orchestration/command_request.schema.json`

Needed:

1. MCP Safe Hands architecture/workflow doc.
2. Manual MCP Inspector runbook.
3. Read-only path allowlist.
4. Steel-door denylist.
5. Tool exposure validator.
6. Audit receipt format.
7. Stop point before install.

Do not build yet:

- write-capable MCP
- shell execution MCP
- remote Pi 5 MCP
- active repo filesystem server
- queue or approval mutation through MCP

Done when:

- operator can prove a local stdio MCP path can read only approved evidence and cannot write/delete/move/rename.

## Phase 1: Knowledge Graph

Goal: make AI_OS explain itself without rereading the whole repo.

Current evidence:

- `docs/governance/source-of-truth-map.md`
- `docs/audits/active-system-map.md`
- `docs/governance/runtime-ownership-map.md`
- `automation/orchestration/execution_registry/AIOS_EXECUTION_CLASSIFICATION_REGISTRY.json`

Needed:

1. Machine-readable graph schema.
2. System nodes: docs, runtime, automation, workers, queues, validators, approvals, telemetry, dashboard, Trading Lab.
3. Ownership edges.
4. Dependency edges.
5. Protected asset list.
6. Decision log references.
7. Query helper: "what owns X?" and "what breaks if X changes?"

Done when:

- a helper can answer ownership and dependency questions from the graph, not ad hoc repo scans.

## Phase 2: Worker Registry Consolidation

Goal: one worker capability authority, one display binding.

Current evidence:

- `automation/orchestration/workers/AIOS_WORKER_REGISTRY.json`
- `automation/orchestration/workers/AIOS_WORKER_PROFILES.json`
- `automation/window_identity/AIOS_WORKER_REGISTRY.json`
- `docs/audits/active-system-map.md`

Needed:

1. Decide canonical capability source.
2. Keep window identity as display/runtime binding only.
3. Add stable IDs linking window markers to worker IDs.
4. Validate no script imports the wrong registry for capability decisions.
5. Retire duplicate capability fields only after dependency review.

Done when:

- routing asks one source what a worker can do.
- display asks a separate binding how the worker appears.

## Phase 3: Event Schema

Goal: define facts that trigger downstream work.

Current evidence:

- `schemas/aios/orchestration/EVENT_SCHEMA.md`
- `services/runtime/eventBus.ts`
- `services/telemetry/telemetryEvent.ts`
- `docs/governance/telemetry-contract.md`

Needed:

1. Reconcile orchestration event family with runtime and telemetry event names.
2. Choose canonical field names.
3. Define append-only event log path.
4. Add event validator.
5. Add compatibility mapper for current camelCase telemetry.
6. Define event source ownership.

Done when:

- work packet, validator, approval, worker, commit package, recovery, and dashboard facts can be emitted to one append-only event stream.

## Phase 4: Queue + Scheduler

Goal: one durable projection of what work exists and what can run.

Current evidence:

- `automation/orchestration/work_packets/`
- `automation/orchestration/command_queue/AIOS_COMMAND_QUEUE.json`
- `automation/orchestration/queue/DISPATCHER_QUEUE.json`
- `services/dispatcher/packetQueue.ts`
- `services/dispatcher/autonomousScheduler.ts`

Needed:

1. Define work packet as durable unit.
2. Define command as transient request, not durable work.
3. Create queue projection from packets and events.
4. Add dependency fields and blocker propagation.
5. Add retry, stale, dead-letter, and manual-review policies.
6. Add scheduler preview only.

Done when:

- AI_OS has one read model for pending, active, blocked, failed, retrying, approval-waiting, completed, and dead-letter packets.

## Phase 5: Validator Routing

Goal: choose validators without Anthony manually selecting them.

Current evidence:

- `automation/orchestration/validators/VALIDATOR_CHAIN_CONFIG_001.json`
- `automation/orchestration/validators/AIOS_VALIDATOR_ROUTER_RULES.example.json`
- `docs/workflows/VALIDATOR_EXECUTION_STANDARD.md`
- execution classification registry

Needed:

1. Changed-file classifier.
2. Packet-risk classifier integration.
3. Path-to-validator map.
4. Validator result schema enforcement.
5. Event emission for validator started/passed/failed.
6. Fail-closed policy for unknown validators.

Done when:

- AI_OS can say exactly which validators are required for a change and why.

## Phase 6: Recovery Supervisor

Goal: make routine failures boring and recoverable.

Current evidence:

- `services/supervisor/runtimeSupervisor.ts`
- `services/dispatcher/runtimeStateRebuilder.ts`
- `services/runtime/autonomousRemediation.ts`
- `docs/workflows/SAFE_REPAIR_AND_RECOVERY_STANDARD.md`
- `docs/governance/AIOS_NIGHT_SUPERVISOR_QUALIFICATION_GATES.md`

Needed:

1. SOS escalation policy.
2. Qualification ledger.
3. Recovery drill fixtures.
4. Crash/restart replay from event log.
5. Stale worker and packet recovery policy.
6. Quarantine policy for corrupt state.
7. No auto-repair outside narrow approved list.

Done when:

- recovery can classify routine failures, recommend safe next steps, and escalate only true SOS conditions.

## Phase 7: Approval Intelligence

Goal: Anthony decides; AI_OS prepares the decision.

Current evidence:

- `docs/security/approval-model.md`
- `automation/orchestration/approval_inbox/APPLY_APPROVAL_GATE_001.json`
- approval scripts and status rules
- approval tier policy

Needed:

1. Restore or create canonical active approval inbox through approved lane.
2. Approval item schema enforcement.
3. Risk ranking using knowledge graph.
4. Bundling by goal/packet/dependency.
5. Recommendation text that remains non-authoritative.
6. Morning brief projection.

Done when:

- approval review shows risk, affected systems, validator evidence, and downstream unblock value.

## Phase 8: Commit Package Builder

Goal: prepare clean exact-file commit candidates without staging.

Current evidence:

- `automation/orchestration/commit_packages/`
- `docs/workflows/AI_OS_COMMIT_PUSH_GATE.md`
- `AGENTS.md` safe commit rule

Needed:

1. Dependency-aware file grouping.
2. Validation evidence attachment.
3. Exact file staging preview.
4. Commit message recommendation.
5. PR description draft, if PR creation is separately approved later.
6. Approval intelligence handoff.

Done when:

- AI_OS can prepare a commit candidate and Anthony only reviews the exact package before any commit approval.

## Phase 9: Autonomy Scorecard

Goal: measure where Anthony is still the manager instead of the decision-maker.

Current evidence:

- `docs/governance/AI_OS_AUTONOMY_LEVELS.md`
- telemetry contract
- runtime visibility models

Needed:

1. Scorecard schema.
2. Event-derived metrics.
3. Manual intervention classification.
4. Recovery rate.
5. Routing rate.
6. Validation rate.
7. Approval load.
8. Coordination load.

Done when:

- AI_OS can report: "human decisions are X percent; human coordination cleanup is Y percent."

## Future APPLY Packet List

1. `AIOS-MCP-SAFE-HANDS-DOCS-APPLY-001`
   Create MCP Safe Hands doc/checklist only.

2. `AIOS-KNOWLEDGE-GRAPH-SCHEMA-DRYRUN-001`
   Inspect existing maps and propose graph schema.

3. `AIOS-KNOWLEDGE-GRAPH-SEED-APPLY-001`
   Create first graph artifact from active maps.

4. `AIOS-WORKER-REGISTRY-CONSOLIDATION-DRYRUN-001`
   Trace all worker registry consumers.

5. `AIOS-WORKER-REGISTRY-BINDING-APPLY-001`
   Add display binding references without removing old registry fields.

6. `AIOS-EVENT-SCHEMA-RECONCILIATION-DRYRUN-001`
   Reconcile event families and telemetry naming.

7. `AIOS-EVENT-LOG-CONTRACT-APPLY-001`
   Add append-only event log contract and validator.

8. `AIOS-QUEUE-PROJECTION-DRYRUN-001`
   Map all queue sources to one read model.

9. `AIOS-VALIDATOR-ROUTER-DRYRUN-001`
   Build changed-file-to-validator route plan.

10. `AIOS-SOS-ESCALATION-POLICY-APPLY-001`
    Create canonical SOS policy after security/governance approval.

11. `AIOS-APPROVAL-INBOX-REPAIR-DRYRUN-001`
    Resolve active approval inbox missing-file mismatch.

12. `AIOS-AUTONOMY-SCORECARD-SCHEMA-DRYRUN-001`
    Define metrics and evidence sources.

## Exact Recommended First APPLY Lane

First APPLY lane should be documentation-only:

```text
Packet ID: AIOS-MCP-SAFE-HANDS-DOCS-APPLY-001
Mode: APPLY
Lane: MCP Safe Hands Foundation Documentation
Allowed paths:
- docs/architecture/toolchain-mcp-safe-hands.md
- one pointer line in the existing autonomy-loop document, if located and explicitly approved
Forbidden:
- MCP install
- package install
- server launch
- automation/orchestration mutation
- services mutation
- telemetry mutation
- trading/broker/secrets/runtime
Validation:
- git diff --check
- git diff --name-only
- verify only approved docs paths changed
Stop:
- after documentation and validation report
```

Reason: MCP Safe Hands is the safest first foundation because it reduces future manual relay work while preserving all steel-door boundaries.
