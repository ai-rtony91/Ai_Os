# Top 50 Operation Glue Micro Gaps

Packet: AIOS-OPERATION-GLUE-FORENSICS-DRYRUN-001
Mode: DRY_RUN report creation only

Severity scale:

- 1: minor inconvenience.
- 2: reduces efficiency.
- 3: prevents automation.
- 4: blocks closed-loop operation.
- 5: core architectural blocker.

## Findings

| Rank | Severity | Micro gap | Evidence | Effect |
|---:|---:|---|---|---|
| 1 | 5 | Work packet creation does not insert into a canonical queue. | `New-AiOsWorkPacket.ps1`, `AIOS_COMMAND_QUEUE.json`, `DISPATCHER_QUEUE.json`, `packetQueue.ts` | Closed loop breaks immediately after packet creation. |
| 2 | 5 | There is no single state vocabulary for packets. | packet mover, runtime advancement, TypeScript queue, dispatcher queue JSON | Automation cannot safely infer next state. |
| 3 | 5 | Worker inbox add path is preview-only and cannot persist assignment. | `Add-AiOsWorkerInboxItem.DRY_RUN.ps1` | Scheduler/worker assignment cannot close. |
| 4 | 5 | Approval request generation is preview-only. | `New-AiOsPacketApprovalRequest.DRY_RUN.ps1` | Validation cannot produce a durable approval package. |
| 5 | 5 | Active approval inbox is missing from expected active path. | active-system-map expects `approval_inbox/APPROVAL_INBOX_001.json`; repo has archive copy | Approval state has no reliable active inbox. |
| 6 | 5 | No canonical append-only orchestration event log is consumed across the loop. | `EVENT_SCHEMA.md`, `eventBus.ts`, telemetry files | Triggers are procedural/manual instead of event-driven. |
| 7 | 5 | Runtime tick does not pass packet queue snapshot into scheduler. | `runtimeTick.ts`, `autonomousScheduler.ts` | Scheduler cannot act on canonical packet queue records. |
| 8 | 5 | Scheduler output does not feed worker resolver. | `autonomousScheduler.ts`, `Resolve-AiOsWorkerForPacket.DRY_RUN.ps1` | Scheduled work is not assigned. |
| 9 | 5 | Validator results are not written back to packet state. | `Invoke-AiOsValidatorChain.DRY_RUN.ps1`, `Move-AiOsPacketState.ps1` | Validation cannot trigger approval. |
| 10 | 5 | Commit package recommendations are not tied to packet, approval, or validator evidence. | `New-AiOsCommitPackageRecommendation.DRY_RUN.ps1` | Commit package is a Git-status helper, not a loop endpoint. |
| 11 | 4 | Goal intake creates one simple packet, not an executable task graph. | `Invoke-AiOsGoalIntake.ps1` | Human still decomposes real work. |
| 12 | 4 | Intake outbox has no observed downstream consumer. | `automation/outbox/AIOS_NEXT_ACTION.json` from intake script | Next action remains a file, not a trigger. |
| 13 | 4 | `Invoke-AiOsRuntimePacketAdvancement.ps1` advances only the newest active packet. | script sorts active packets by LastWriteTimeUtc | Multi-packet queue semantics are ignored. |
| 14 | 4 | Runtime packet advancement bypasses `Move-AiOsPacketState.ps1` transition guard. | direct status mutation in runtime advancement | Two transition engines can diverge. |
| 15 | 4 | Runtime advancement depends on `checkpoints/verify_success.ps1` instead of packet validator evidence. | `Invoke-AiOsRuntimePacketAdvancement.ps1` | Proof gate is not packet-specific. |
| 16 | 4 | Persistent supervisor DRY_RUN still calls self-route with `-Apply`. | `Start-AiOsPersistentRuntimeSupervisor.ps1` | Mode semantics are confusing and risky. |
| 17 | 4 | Action recommendation can return "No command recommended" as command text. | `Get-AiOsActionRecommendation.DRY_RUN.ps1` | Self-route needs special handling for non-command recommendations. |
| 18 | 4 | Scheduler preview is static and not wired to live queue state. | `Invoke-AiOsSchedulerPreview.DRY_RUN.ps1` | Preview cannot be used as execution scheduler. |
| 19 | 4 | TypeScript scheduler and PowerShell scheduler preview are separate systems. | `autonomousScheduler.ts`, scheduler preview script | Scheduler ownership is ambiguous. |
| 20 | 4 | `DISPATCHER_QUEUE.json` has assigned items unrelated to active packet files. | queue JSON vs work packet folders | Dispatcher queue and packet lifecycle drift. |
| 21 | 4 | Command queue stores commands, not durable work packets. | `AIOS_COMMAND_QUEUE.json` | It cannot be canonical work state. |
| 22 | 4 | Worker resolver output is console/JSON evidence only. | `Resolve-AiOsWorkerForPacket.DRY_RUN.ps1` | Selection does not become assignment. |
| 23 | 4 | Worker resolver fallback can assign unresolved work to `brainstem_codex`. | resolver fallback logic | Unknown ownership can become a default instead of escalation. |
| 24 | 4 | Worker registry and worker profiles split identity/capability. | `AIOS_WORKER_REGISTRY.json`, `AIOS_WORKER_PROFILES.json` | Routing can consult different authority layers. |
| 25 | 4 | Window identity registry duplicates worker identity concerns. | `automation/window_identity/AIOS_WORKER_REGISTRY.json` | Display binding and capability authority are not fully separated. |
| 26 | 4 | Worker state ownership script says window identity is presentation, but decision remains open. | `Get-AiOsWorkerStateOwnership.ps1`, active-system-map | Known ambiguity remains unresolved. |
| 27 | 4 | Worker inbox file is active, but no safe APPLY writer was found in the inspected handoff path. | `AIOS_WORKER_INBOX.json`, inbox add script | Assignment cannot be persisted by current preview lane. |
| 28 | 4 | Worker execution scripts are DRY_RUN-gated. | `workers/execution/Invoke-AiOsWorkerSafeExecute.DRY_RUN.ps1` | No qualified execution loop. |
| 29 | 4 | Validator recommendation is based on whole repo dirty state. | `Get-AiOsValidatorRecommendation.DRY_RUN.ps1` | Local backlog can affect unrelated packet validation. |
| 30 | 4 | Validator chain reports are not stored in a packet-specific evidence path. | validator chain runner | Approval and commit package layers cannot consume stable evidence. |
| 31 | 4 | Approval processor reads PR approval files, not approval inbox previews. | `Invoke-AiOsApprovalProcessor.DRY_RUN.ps1` | Approval systems are split. |
| 32 | 4 | Approval processor is DRY_RUN and never moves packet state. | approval processor output | Human must apply approval transition. |
| 33 | 4 | Approval detection is used by recommendation, but approval creation is not closed. | action recommendation, approval preview | The system can notice approvals better than it can create them. |
| 34 | 4 | Commit package branch-to-worker mapping does not recognize current branch. | commit package recommender maps only known worker branch regexes | Package ownership may show UNKNOWN on governed branches. |
| 35 | 4 | Commit package recommender expands untracked directories and may include unrelated backlog. | recommender scans `git status --short` | Package recommendations can mix work lanes. |
| 36 | 4 | No packet id flows into commit package recommendation. | commit package recommender parameters | Human must map diff to packet. |
| 37 | 4 | No approval id flows into commit package recommendation. | commit package recommender parameters | Commit package cannot prove decision readiness. |
| 38 | 4 | No validator evidence path flows into commit package recommendation. | commit package recommender parameters | Commit package cannot prove validation readiness. |
| 39 | 3 | MCP plan exists but no Inspector runbook or safe hands proof exists. | `AI_OS_MCP_PROTOTYPE_PLAN.md`, MCP report | MCP cannot yet reduce relay safely. |
| 40 | 3 | Python supervisor reads command queue, not packet queue. | `services/python_supervisor/main.py` | Supervisor focus does not match durable work packet model. |
| 41 | 3 | Python supervisor is explicitly not an MCP server, daemon, scheduler, executor, or queue mutator. | `services/python_supervisor/README.md` | It cannot close execution loop by design. |
| 42 | 3 | Night supervisor is read-only/report-first. | `NIGHT_SUPERVISOR_README.md`, Night Builder report | Overnight execution remains blocked. |
| 43 | 3 | Recovery systems produce plans and awareness, not qualified mutations. | recovery docs, `autonomousRemediation.ts` | Routine repair still needs human handoff. |
| 44 | 3 | Telemetry visibility consumes state but does not own transitions. | `runtimeVisibility.ts`, telemetry contract | Telemetry observes more than it drives. |
| 45 | 3 | Runtime event bus is in-memory and runtime-focused. | `services/runtime/eventBus.ts` | It cannot survive restart or serve as orchestration flight recorder. |
| 46 | 3 | Event schema, runtime events, and telemetry events are not reconciled. | `EVENT_SCHEMA.md`, `eventBus.ts`, `telemetryEvent.ts` | Subscribers cannot rely on one event shape. |
| 47 | 3 | Lock/collision validators detect conflict but do not arbitrate. | claim/collision validators, lock policy | Conflicts still escalate or stall. |
| 48 | 3 | Source-of-truth maps are documents, not runtime query artifacts. | governance and audit maps | Routing cannot ask one graph what owns a path. |
| 49 | 3 | Existing active packets may contain stale or legacy metadata. | active-system-map and prior report findings | State cannot be trusted without migration/normalization. |
| 50 | 3 | Generated reports are not yet consumed by automation. | `docs/reports/` outputs | Reports improve knowledge but do not close runtime handoffs. |

## Pattern Diagnosis

The recurring pattern is:

```text
script produces evidence
-> evidence is printed or written locally
-> no canonical consumer advances the next state
```

This is correct for safety at the current maturity level. It is also the reason Anthony remains the integration layer.
