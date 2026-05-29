# Master Reconciliation Roadmap

Packet: AIOS-MASTER-RECONCILIATION-ROADMAP-DRYRUN-001
Mode: DRY_RUN report creation only
Branch inspected: phase-night-supervisor-layer2-memory
Worktree: C:\Dev\Ai.Os

## Executive Answer

The shortest safe path to supervised overnight development is not another broad investigation and not immediate MCP installation.

The repo evidence shows AI_OS already has many autonomy parts: goal intake, work packets, queues, scheduler code, worker registries, worker profiles, validators, approval gates, commit package recommendations, telemetry, runtime supervisor code, recovery planning, and Night Supervisor doctrine.

The missing layer is the closed-loop state handoff:

```text
packet_created
-> queued
-> scheduled
-> worker_assignment_preview
-> assignment_persisted
-> execution_result
-> validator_result
-> approval_requested
-> approved_or_blocked
-> commit_package_ready
-> human_review_required
```

The first hard loop break is still:

```text
Packet -> Canonical Queue
```

## What AI_OS Actually Has Today

| Subsystem | Actual repo state | Evidence |
|---|---|---|
| Governance authority | Strong | `AGENTS.md`, `README.md`, `docs/governance/source-of-truth-map.md` |
| Active system map | Exists | `docs/audits/active-system-map.md` |
| Goal intake | Partial | `automation/intake/Invoke-AiOsGoalIntake.ps1`, `Convert-AiOsInputToPacketProposal.DRY_RUN.ps1` |
| Work packets | Exists, active | `automation/orchestration/work_packets/` |
| Queue surfaces | Multiple partial systems | `automation/orchestration/command_queue/AIOS_COMMAND_QUEUE.json`, `automation/orchestration/queue/DISPATCHER_QUEUE.json`, `services/dispatcher/packetQueue.ts` |
| Scheduler | Partial | `services/dispatcher/autonomousScheduler.ts`, scheduler preview scripts |
| Worker registry | Partial but strong | `automation/orchestration/workers/AIOS_WORKER_REGISTRY.json`, `AIOS_WORKER_PROFILES.json` |
| Window identity | Exists, separate concern | `automation/window_identity/AIOS_WORKER_REGISTRY.json` |
| Worker inbox | Exists, not closed-loop | `automation/orchestration/workers/inbox/AIOS_WORKER_INBOX.json` |
| Validator chain | Strong partial | `automation/orchestration/validators/`, `VALIDATOR_CHAIN_CONFIG_001.json` |
| Approval model | Partial | `docs/security/approval-model.md`, approval gate and scripts |
| Commit package prep | Strong partial | `automation/orchestration/commit_packages/` |
| Runtime supervisor | Partial | `services/supervisor/`, `automation/orchestration/runtime/` |
| Telemetry | Partial | `services/telemetry/`, `telemetry/work_ledger.jsonl`, runtime visibility |
| Night Supervisor doctrine | Exists | `docs/workflows/AI_OS_OVERNIGHT_SUPERVISOR_WORKFLOW.md`, qualification gates |
| MCP | Documented only | `docs/workflows/AI_OS_MCP_PROTOTYPE_PLAN.md`, MCP report |

## What AI_OS Does Not Have

1. A canonical closed-loop state contract used by packet, queue, scheduler, worker, validator, approval, and commit systems.
2. A durable packet-to-queue projection that every downstream layer consumes.
3. A scheduler path that consumes the active packet queue projection.
4. A governed worker assignment writer.
5. A packet-scoped validator result evidence path.
6. A durable approval request path into a canonical active approval inbox.
7. Commit package recommendations tied to packet id, validator evidence, approval id, and dependency graph.
8. A single append-only orchestration event log consumed by recovery, scheduler, approvals, and scorecard.
9. A runtime-loadable knowledge graph.
10. A qualified recovery supervisor and SOS escalation policy.
11. A real autonomy scorecard.
12. A proven read-only MCP safe-hands installation path.

## Assumptions That Were Wrong

| Historical assumption | Repo reality | Roadmap correction |
|---|---|---|
| AI_OS mostly lacks autonomy components | Components exist, but handoffs are broken | Prioritize operation glue over net-new components |
| MCP is the immediate bottleneck | Packet -> queue is the first hard loop break | Build MCP docs/checklist, but close internal state continuity first |
| Worker registry can be solved by deleting a duplicate | Window identity registry is active display support | Demote/rename later; do not delete |
| Queue is simply missing | Multiple queue stores exist | Define one canonical queue projection from packets/events |
| Approval system is absent | Approval model/gates/scripts exist | Repair inbox and persistence, then add intelligence |
| Commit packaging is missing | Commit package recommender exists | Add packet/evidence/dependency inputs |
| Night Builder starts by coding overnight | Repo doctrine supports read-only/report-first only | Start with Night Builder Read-Only after state/evidence gates |

## Assumptions That Were Correct

1. The steel door must remain permanent.
2. Human approval remains the authority for APPLY, commit, push, merge, deploy, secrets, and trading.
3. The system needs a knowledge graph/runtime repo memory.
4. The event layer must become append-only and crash-survivable.
5. Validator routing must become packet-scoped and evidence-producing.
6. Recovery must be conservative, qualified, and SOS-bound.
7. The autonomy scorecard is needed to distinguish operator decisions from operator babysitting.
8. Night Builder must start with read-only inspection and reports, not execution.

## Truth Table

| Subsystem | Originally assumed missing | Actually exists | Partial | Missing | Wrong assumption |
|---|---:|---:|---:|---:|---|
| Knowledge Graph | Yes | Yes, as docs | Yes | Runtime graph | It is not absent; it is non-queryable |
| Goal Intake | Yes | Yes | Yes | Robust task graph | It creates simple packets, not executable graphs |
| Task Graph | Yes | Yes, in dispatcher/campaign concepts | Yes | Unified packet graph | Code exists but is not connected to packets |
| Worker Registry | Duplicate/problem | Yes | Yes | Clean role separation | Delete was unsafe; demotion is right |
| Queue | Yes | Yes, several | Yes | Canonical projection | Missing one owner, not all queue code |
| Scheduler | Yes | Yes | Yes | Live queue input | Scheduler exists but is not fed packet snapshot |
| Event Bus | Yes | Yes, partial | Yes | Append-only orchestration log | Runtime bus exists but is not the needed flight recorder |
| Validator Routing | Yes | Yes | Yes | Packet-scoped router | Existing validator stack is strong |
| Approval System | Yes | Yes | Yes | Active inbox persistence/intelligence | Gate exists; handoff is broken |
| Commit Packaging | Yes | Yes | Yes | Packet/evidence integration | Recommender exists |
| Night Supervisor | Yes | Yes, doctrine/skeleton | Yes | Qualified unattended run | Must remain read-only first |
| MCP | Yes | Documented only | No | Installed/proven safe path | MCP is not first loop break |
| Worker Identity | Duplicate registry | Yes | Yes | Demoted naming | It is a separate display concern |
| Telemetry | Yes | Yes | Yes | Transition authority | Telemetry observes, does not drive |
| Recovery | Yes | Yes, planning/code | Yes | Qualified executor/SOS | Awareness exists |

## First Hard Loop Break

Packet -> Canonical Queue.

Evidence:

- `automation/intake/Invoke-AiOsGoalIntake.ps1` can call `automation/orchestration/work_packets/New-AiOsWorkPacket.ps1`.
- The packet lands under `automation/orchestration/work_packets/active`.
- It does not become a canonical queue item consumed by `AIOS_COMMAND_QUEUE.json`, `DISPATCHER_QUEUE.json`, `services/dispatcher/packetQueue.ts`, scheduler, worker assignment, validator routing, approval inbox, or commit package.

Required fix:

Create a read-only canonical queue projection from packet files and normalized state mapping. Do not mutate packets in the first APPLY lane.

## Second Hard Loop Break

Queue -> Scheduler -> Worker Assignment.

Evidence:

- `services/dispatcher/autonomousScheduler.ts` can consume `packetQueueSnapshot`.
- `services/runtime/runtimeTick.ts` does not pass active packet queue snapshot.
- Worker resolver exists, but scheduler output does not feed it.
- `Add-AiOsWorkerInboxItem.DRY_RUN.ps1` previews assignment and does not persist inbox state.

Required fix:

Connect scheduler preview to the queue projection, then connect dispatch actions to worker resolver preview, then build a governed assignment writer for safe folders only.

## Third Hard Loop Break

Validation -> Approval -> Commit Package.

Evidence:

- Validator chain exists but results do not write back to packet state or packet-scoped evidence.
- Approval request generation is preview-only.
- Active approval inbox state is mismatched/missing in the expected path.
- Commit package recommendation scans Git status, not packet id, validator evidence, approval id, or task graph.

Required fix:

Persist packet-scoped validator evidence, repair approval inbox persistence, then feed approved packet/evidence into commit package recommendation.

## MCP Actual Position In Roadmap

MCP is Phase 0 governance and safe-hands preparation, not the first operational glue fix.

Ranking: important, but not highest-leverage for closed-loop operation.

MCP should proceed only as:

1. Documentation/checklist.
2. Manual local stdio Inspector proof.
3. Read-only filesystem evidence path.
4. No write/delete/move/rename/push/deploy/trading tools.

MCP does not solve packet-to-queue, scheduler handoff, approval persistence, validator evidence, or event schema reconciliation.

## Night Builder Readiness

Current readiness:

- Read-only morning brief: YELLOW.
- Packet draft preview: YELLOW.
- Overnight execution: RED.
- SOS-only operation: RED.

Night Builder cannot safely run autonomous development yet. The safe first milestone is a read-only Night Builder that reads approved evidence, drafts morning reports, flags SOS items, and writes only approved report/evidence files.

## Estimated Distance To Supervised Overnight Development

Evidence-based estimate:

- Read-only overnight reporting: after MCP Safe Hands docs, queue projection, event contract, and evidence path. Estimated 3-5 focused APPLY lanes after current reports.
- Supervised packet routing without execution: after queue projection, scheduler preview integration, worker resolver integration, and approval inbox repair. Estimated 6-10 focused APPLY lanes.
- Supervised overnight development execution in safe rooms: after validator evidence, assignment writer, recovery/SOS, commit package evidence, and qualification gates. Estimated 12-18 focused APPLY lanes.

Do not measure this as calendar time. Measure it as closed-loop gates passed.

## Top 10 Highest-Leverage Fixes

1. Define closed-loop state contract.
2. Build read-only canonical queue projection from work packets.
3. Feed queue projection into scheduler preview.
4. Connect scheduler actions to worker resolver preview.
5. Build governed worker assignment writer for safe lanes only.
6. Add packet-scoped validator routing and evidence.
7. Repair/define canonical active approval inbox.
8. Tie commit package recommendation to packet, evidence, and approval.
9. Add append-only orchestration event log.
10. Add autonomy scorecard from event/queue evidence.

## Final Roadmap

```text
1. Closed-loop state contract
2. Canonical queue projection
3. Scheduler consumes queue projection
4. Worker resolver consumes scheduler actions
5. Governed worker assignment writer
6. Packet-scoped validator routing
7. Validator evidence persistence
8. Approval inbox repair
9. Approval request persistence
10. Commit package evidence integration
11. Append-only event log
12. Knowledge graph seed
13. Worker identity demotion/rename
14. SOS policy and recovery gates
15. Autonomy scorecard
16. MCP Safe Hands manual proof
17. Night Builder Read-Only
18. Safe-room supervised execution expansion
```

## Final Recommendation

The next APPLY lane should be implementation, not more discovery:

```text
AIOS-CLOSED-LOOP-STATE-CONTRACT-APPLY-001
```

Purpose:

Create the canonical state vocabulary and read-only mapping table used by packet, queue, scheduler, worker, validator, approval, commit package, recovery, and scorecard layers.

Stop before runtime mutation.
