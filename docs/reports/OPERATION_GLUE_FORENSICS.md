# Operation Glue Forensics

Packet: AIOS-OPERATION-GLUE-FORENSICS-DRYRUN-001
Mode: DRY_RUN report creation only
Branch inspected: phase-night-supervisor-layer2-memory
Worktree: C:\Dev\Ai.Os

## Bottom Line

AI_OS does not lack components. It lacks a single closed-loop handoff contract between the components.

The repo contains goal intake, work packets, queues, scheduler previews, worker registries, worker inboxes, validators, approval previews, commit package recommendations, runtime supervisors, telemetry, recovery plans, and Night Supervisor planning. These are mostly operating as separate preview or evidence surfaces. The continuous supervised development loop breaks because outputs are not consistently consumed by the next system, state names differ across layers, and several critical transitions remain human-carried rather than event-driven.

Exact loop break:

```text
Goal intake can create a work packet,
but packet creation does not reliably insert into one canonical queue,
does not emit a canonical event,
does not assign a worker through a persistent inbox,
does not automatically trigger validator routing,
does not generate a persisted approval item,
and does not hand validated evidence into commit package review.
```

## Authority Used

Repository authority wins over generated reports and source documents.

Primary authority:

- `AGENTS.md`
- `README.md`
- `docs/governance/source-of-truth-map.md`
- `docs/audits/active-system-map.md`

Report inputs:

- `docs/reports/MCP_FOUNDATION_REPORT.md`
- `docs/reports/AUTONOMY_GAP_REPORT.md`
- `docs/reports/NIGHT_BUILDER_REPORT.md`
- `docs/reports/IMPLEMENTATION_SEQUENCE_REPORT.md`
- `docs/reports/EXECUTIVE_SUMMARY.md`

Implementation evidence:

- `automation/intake/Invoke-AiOsGoalIntake.ps1`
- `automation/orchestration/work_packets/New-AiOsWorkPacket.ps1`
- `automation/orchestration/work_packets/Move-AiOsPacketState.ps1`
- `automation/orchestration/runtime/Invoke-AiOsRuntimePacketAdvancement.ps1`
- `automation/orchestration/runtime/Start-AiOsPersistentRuntimeSupervisor.ps1`
- `automation/orchestration/recommendations/Get-AiOsActionRecommendation.DRY_RUN.ps1`
- `automation/orchestration/scheduler/Invoke-AiOsSchedulerPreview.DRY_RUN.ps1`
- `automation/orchestration/workers/Resolve-AiOsWorkerForPacket.DRY_RUN.ps1`
- `automation/orchestration/workers/inbox/Add-AiOsWorkerInboxItem.DRY_RUN.ps1`
- `automation/orchestration/validators/Get-AiOsValidatorRecommendation.DRY_RUN.ps1`
- `automation/orchestration/validator_chain_runner/Invoke-AiOsValidatorChain.DRY_RUN.ps1`
- `automation/orchestration/approval_inbox/New-AiOsPacketApprovalRequest.DRY_RUN.ps1`
- `automation/orchestration/approval_processor/Invoke-AiOsApprovalProcessor.DRY_RUN.ps1`
- `automation/orchestration/commit_packages/New-AiOsCommitPackageRecommendation.DRY_RUN.ps1`
- `automation/orchestration/command_queue/AIOS_COMMAND_QUEUE.json`
- `automation/orchestration/queue/DISPATCHER_QUEUE.json`
- `services/dispatcher/packetQueue.ts`
- `services/dispatcher/autonomousScheduler.ts`
- `services/runtime/runtimeTick.ts`

## Transition Trace

| Transition | Status | Evidence | Glue failure |
|---|---|---|---|
| Goal -> Intake | CONNECTED | `Invoke-AiOsGoalIntake.ps1` accepts `-Goal` and writes intake/outbox when `-Apply` is used. | Intake is simple and goal text stays mostly undecomposed. |
| Intake -> Packet | PARTIAL | `Invoke-AiOsGoalIntake.ps1` calls `New-AiOsWorkPacket.ps1` when `-Apply` is used. | The packet is created directly in `work_packets/active`, not through approval, graph, event, or queue projection. |
| Packet -> Queue | BROKEN | Packet files live under `automation/orchestration/work_packets/active`; separate queue files also exist. | `New-AiOsWorkPacket.ps1` writes packet files but does not insert into `AIOS_COMMAND_QUEUE.json`, `DISPATCHER_QUEUE.json`, or `services/dispatcher/packetQueue.ts` state. |
| Queue -> Scheduler | PARTIAL | `autonomousScheduler.ts` can consume `packetQueueSnapshot`; `runtimeTick.ts` calls it. | `runtimeTick.ts` does not pass `packetQueueSnapshot`, so scheduler operates from replay/resume inputs, not the active packet folder or dispatcher queue. |
| Scheduler -> Worker Selection | BROKEN | `Resolve-AiOsWorkerForPacket.DRY_RUN.ps1` can select a worker from profiles. | Scheduler actions are not fed into the worker resolver. Worker resolver is manual/DRY_RUN. |
| Worker Selection -> Worker Assignment | BROKEN | `Add-AiOsWorkerInboxItem.DRY_RUN.ps1` previews an inbox item. | The inbox add script never mutates the inbox, even with `-Apply`; it says a separate APPLY command is required. |
| Worker Assignment -> Execution | BROKEN | Worker execution scripts are DRY_RUN only in inspected path. | No persistent assignment creates a worker-executable task. |
| Execution -> Validation | PARTIAL | Packets can contain `validator`; validator recommendation and chain exist. | Packet completion does not automatically call validator routing. Validator recommendation is based on `git status`, not packet event/state. |
| Validation -> Approval | BROKEN | `New-AiOsPacketApprovalRequest.DRY_RUN.ps1` previews an approval. | It does not persist an approval inbox item; approval inbox active file is absent from expected path. |
| Approval -> Packet Advancement | PARTIAL | `Move-AiOsPacketState.ps1` enforces approval for protected transitions. | Approval processor is DRY_RUN and only scans PR approval files under `automation/orchestration/approvals`, not the active approval inbox. |
| Approval -> Commit Package | PARTIAL | Commit package recommendation exists. | Commit package recommender scans current Git status and protected paths; it does not consume approval items, packet state, validator evidence, or task graph. |
| Commit Package -> Human Review | CONNECTED | Recommender outputs exact-file staging suggestions and risk exclusions. | This part is intentionally human-gated, but not fed by the closed packet-validation-approval loop. |

## Subsystem IO Map

### Goal Intake

Input: goal string.
Process: slug generation and simple safety summary.
Output: `automation/intake/AIOS_GOAL_INTAKE.json`, `automation/outbox/AIOS_NEXT_ACTION.json`, optional work packet.
Consumer: human/operator scripts.
Glue failure: no canonical event and no graph-backed task decomposition.

### Work Packet Builder

Input: packet fields from caller.
Process: builds JSON packet.
Output: file under `automation/orchestration/work_packets/active` when `-Mode APPLY`.
Consumer: packet state scripts and recommendation scripts.
Glue failure: output bypasses canonical queue projection and event bus.

### Packet State Mover

Input: packet file path and target state.
Process: validates legal transitions and protected gates.
Output: updated packet JSON only when `-Apply`.
Consumer: human/operator and runtime packet advancement.
Glue failure: transition vocabulary differs from other queue/status models.

### Runtime Packet Advancement

Input: newest active packet file.
Process: simple status mapping plus `checkpoints/verify_success.ps1` in APPLY.
Output: direct packet status mutation.
Consumer: persistent runtime supervisor.
Glue failure: it advances only one latest packet, ignores queue dependencies, ignores assignment state, and does not emit events.

### Persistent Runtime Supervisor

Input: path registry, action recommendation, packet advancement.
Process: loops for N cycles and writes audit log.
Output: `automation/orchestration/runtime/logs/supervisor_cycles.jsonl`.
Consumer: human/operator.
Glue failure: calls self-route with `-Apply` even in supervisor DRY_RUN mode, and packet advancement is not event-driven.

### Action Recommendation

Input: runtime health, next-step resolver, blocker resolver, approval match detector.
Process: chooses one recommended command.
Output: command recommendation plus result contract.
Consumer: runtime self-route, operator menus, morning/session helpers.
Glue failure: command strings are not durable work; "No command recommended" can flow into self-route gate as a command candidate.

### Scheduler Preview

Input: none.
Process: emits static preview event classes.
Output: scheduler preview only.
Consumer: human/operator.
Glue failure: not connected to packet queue state, worker availability, or event log.

### TypeScript Scheduler

Input: resume plan, dead letter queue, worker leases, optional packet queue snapshot.
Process: generates scheduled actions.
Output: `SchedulerPlan`.
Consumer: runtime tick and visibility.
Glue failure: active `runtimeTick.ts` does not pass packet queue snapshot, so active packet files do not become scheduler work.

### Worker Resolver

Input: packet path or packet id.
Process: matches owner lane, assigned worker, or related file paths against worker profiles.
Output: selected worker and guard/save command suggestions.
Consumer: human/operator.
Glue failure: no scheduler or queue runner persists the selected worker into inbox/assignment state.

### Worker Inbox Add

Input: worker id and task text.
Process: validates worker exists and builds inbox item preview.
Output: console preview only.
Consumer: human/operator.
Glue failure: `.DRY_RUN.ps1` never writes inbox state; assignment stops here.

### Validator Recommendation

Input: `git status --short`.
Process: classifies changed files and recommends validators.
Output: validator recommendation report.
Consumer: human/operator or validator chain.
Glue failure: not triggered by `packet.completed`, worker output, or changed-file event; untracked backlog can pollute recommendations.

### Validator Chain Runner

Input: current Git status plus optional worker/evidence paths.
Process: runs diff check, parse checks, clean-state verifier, approval runner, and post-push verifier conditionally.
Output: JSON validator chain run report.
Consumer: human/operator.
Glue failure: no canonical validator result is written back to packet, approval request, event log, or commit package.

### Approval Request Preview

Input: packet file.
Process: creates approval request preview.
Output: console/JSON preview.
Consumer: human/operator.
Glue failure: does not persist to active approval inbox.

### Approval Processor

Input: PR approval files and active packet files.
Process: matches approved PR files to waiting packets.
Output: preview of packet move to approved.
Consumer: human/operator.
Glue failure: PR approval files are separate from packet approval request previews and active approval inbox.

### Commit Package Recommendation

Input: current Git status.
Process: classifies changed/new files, excludes protected paths, recommends exact-file staging commands.
Output: commit package recommendation.
Consumer: human/operator.
Glue failure: does not consume packet id, validator results, approval evidence, worker assignment, or dependency graph.

## Ranking Summary

Severity scale:

- Severity 1: minor inconvenience.
- Severity 2: reduces efficiency.
- Severity 3: prevents automation.
- Severity 4: blocks closed-loop operation.
- Severity 5: core architectural blocker.

Top severity findings:

| Severity | Finding |
|---:|---|
| 5 | No canonical state transition authority connects packet, queue, scheduler, worker, validation, approval, and commit package state. |
| 5 | No append-only event stream is consumed across the loop. |
| 5 | Packet creation bypasses a canonical durable queue projection. |
| 5 | Worker assignment is preview-only and does not persist from scheduler decisions. |
| 5 | Approval preview does not persist into a canonical active approval inbox. |
| 4 | Runtime scheduler does not consume active packet folder or packet queue snapshot in `runtimeTick.ts`. |
| 4 | Validator results are not written back to packet state or approval evidence. |
| 4 | Commit package recommendation is Git-status-based, not packet/evidence-based. |
| 4 | Multiple queue stores compete without one read model. |
| 4 | Worker capability and window identity registries still create routing ambiguity. |

## MCP Forensics

MCP would solve some inspection and relay problems. It would not close the loop by itself.

Real MCP blockers it can help:

- Reduce manual file-reading relay across authority files, reports, queues, telemetry, and packet state.
- Provide a safer read-only tool surface for future agents to inspect approved repo evidence.
- Standardize external tool access after safe hands governance exists.
- Support Night Builder read-only morning brief generation.

Problems MCP does not solve:

- It does not choose the canonical queue.
- It does not reconcile packet status vocabularies.
- It does not make scheduler output persist worker assignment.
- It does not create the event log.
- It does not restore the active approval inbox.
- It does not validate or approve packet transitions.
- It does not generate recovery qualifications or SOS rules.
- It does not turn DRY_RUN previews into safe APPLY flows.

MCP is not the exact point where the loop currently breaks. The loop breaks at packet-to-queue and queue-to-assignment. MCP is useful only after AI_OS defines which state surfaces it is allowed to read and which state transitions remain unreachable.

## Final Forensic Answer

AI_OS is currently a supervised orchestration workbench with strong evidence tooling. It is not a continuous supervised execution environment because its components do not share one authoritative state machine.

The highest-leverage glue fix is not "more autonomy." It is a single closed-loop state contract:

```text
packet_created -> queued -> assigned -> executed -> validator_result -> approval_requested -> approved_or_blocked -> commit_package_ready -> human_review
```

Each transition needs one owner, one input, one output, one consumer, and one event. Until that exists, Anthony remains the integration layer.
