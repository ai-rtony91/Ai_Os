# Closed Loop Breakpoints

Packet: AIOS-OPERATION-GLUE-FORENSICS-DRYRUN-001
Mode: DRY_RUN report creation only

## Loop Closure Test

Question:

Can AI_OS currently perform this without human coordination?

```text
Goal -> Packet -> Queue -> Assignment -> Validation -> Approval Package
```

Answer: no.

The exact first hard break is:

```text
Packet -> Queue
```

`automation/intake/Invoke-AiOsGoalIntake.ps1` can call `automation/orchestration/work_packets/New-AiOsWorkPacket.ps1`, and the packet builder can write a packet under `automation/orchestration/work_packets/active`. But that file does not become an entry in one canonical durable queue consumed by the scheduler, worker assignment layer, validator router, approval inbox, and commit package builder.

## Breakpoint Table

| # | Handoff | Status | Severity | Evidence | Breakpoint |
|---:|---|---|---:|---|---|
| 1 | Goal -> Intake | CONNECTED | 2 | `automation/intake/Invoke-AiOsGoalIntake.ps1` | Goal intake accepts a goal and can write intake/outbox only with `-Apply`. |
| 2 | Intake -> Packet | PARTIAL | 3 | `Invoke-AiOsGoalIntake.ps1`, `New-AiOsWorkPacket.ps1` | Simple goal becomes one packet, not a graph of executable packets. |
| 3 | Packet -> Canonical Queue | BROKEN | 5 | `New-AiOsWorkPacket.ps1`, `AIOS_COMMAND_QUEUE.json`, `DISPATCHER_QUEUE.json`, `packetQueue.ts` | Packet file is not inserted into command queue, dispatcher queue, or TypeScript packet queue. |
| 4 | Queue -> Scheduler | PARTIAL | 4 | `autonomousScheduler.ts`, `runtimeTick.ts` | Scheduler can consume `packetQueueSnapshot`, but runtime tick does not pass one. |
| 5 | Scheduler -> Worker Selection | BROKEN | 4 | `Resolve-AiOsWorkerForPacket.DRY_RUN.ps1` | Scheduler actions do not call worker resolver. |
| 6 | Worker Selection -> Assignment | BROKEN | 5 | `Add-AiOsWorkerInboxItem.DRY_RUN.ps1` | Inbox item is preview only and never persisted. |
| 7 | Assignment -> Execution | BROKEN | 5 | worker execution scripts under `automation/orchestration/workers/` | Worker execution remains DRY_RUN-gated and not fed by assignment state. |
| 8 | Execution -> Validation | PARTIAL | 4 | packet `validator` field, validator recommender, validator chain | Validator route is not triggered by worker completion or packet events. |
| 9 | Validation -> Packet State | BROKEN | 4 | `Invoke-AiOsValidatorChain.DRY_RUN.ps1`, `Move-AiOsPacketState.ps1` | Validator result does not automatically update `validation_status` or move packet to awaiting approval. |
| 10 | Packet -> Approval Request | PARTIAL | 4 | `New-AiOsPacketApprovalRequest.DRY_RUN.ps1` | Approval request is preview only. |
| 11 | Approval Request -> Approval Inbox | BROKEN | 5 | active-system-map expects `APPROVAL_INBOX_001.json`; only archive copy found | No canonical active inbox receives packet approval requests. |
| 12 | Approval -> Packet Approved | PARTIAL | 4 | `Invoke-AiOsApprovalProcessor.DRY_RUN.ps1` | Approval processor scans PR approval files and previews mutation only. |
| 13 | Approved Packet -> Commit Package | PARTIAL | 4 | `New-AiOsCommitPackageRecommendation.DRY_RUN.ps1` | Commit package is based on Git status, not approved packet and validator evidence. |
| 14 | Commit Package -> Human Review | CONNECTED | 2 | commit package recommendation output | Human can review exact files, but evidence chain is not closed. |

## State Vocabulary Mismatch

Different layers use different state names.

Packet builder:

- `proposed`
- `active`

Packet mover:

- `active`
- `routed`
- `dry_run_done`
- `awaiting_approval`
- `approved`
- `applying`
- `validated`
- `complete`
- `blocked`
- `failed`

Runtime packet advancement:

- `active`
- `routed`
- `dry_run_done`
- `awaiting_approval`
- `approved`
- `applying`
- `validated`
- `complete`

TypeScript packet queue:

- `queued`
- `scheduled`
- `executing`
- `retrying`
- `waiting_approval`
- `approved`
- `dry_run`
- `applied`
- `completed`
- `failed`
- `blocked`
- `rolled_back`
- `dead_letter`
- `manual_review`

Dispatcher queue JSON:

- `DONE`
- `ASSIGNED`

Impact: a packet can be "active" in one subsystem, "queued" in another, "ASSIGNED" in a third, and invisible to the TypeScript scheduler. This is a Severity 5 loop blocker because automation cannot safely advance state when state vocabulary is not unified.

## Current Closed-Loop Execution Capacity

| Capability | Current capacity | Evidence | Verdict |
|---|---|---|---|
| Accept goal | Yes | `Invoke-AiOsGoalIntake.ps1` | Exists. |
| Create packet | Yes, direct packet file | `New-AiOsWorkPacket.ps1` | Partial. |
| Insert packet into durable queue | No | multiple queue stores | Broken. |
| Generate scheduler plan | Yes, in code/preview | `autonomousScheduler.ts`, scheduler preview | Partial. |
| Assign worker | Preview only | `Resolve-AiOsWorkerForPacket.DRY_RUN.ps1` | Broken for automation. |
| Persist worker inbox item | No | `Add-AiOsWorkerInboxItem.DRY_RUN.ps1` | Broken. |
| Execute worker task | No closed assignment-execution loop | worker scripts are DRY_RUN-gated | Broken. |
| Choose validators | Yes, from Git status | `Get-AiOsValidatorRecommendation.DRY_RUN.ps1` | Partial. |
| Persist validation result to packet | No | validator chain emits report only | Broken. |
| Generate approval request | Preview only | `New-AiOsPacketApprovalRequest.DRY_RUN.ps1` | Broken for automation. |
| Process approval | Preview only | `Invoke-AiOsApprovalProcessor.DRY_RUN.ps1` | Broken for automation. |
| Prepare commit package | Yes, from Git status | commit package recommender | Partial. |

## Night Builder Breakpoints

These are the missing integrations that prevent overnight supervised development:

1. No safe read-only MCP hands connected to approved evidence.
2. Night supervisor can produce reports, but cannot rely on a canonical event log.
3. Scheduler preview is not connected to active packet queue state.
4. TypeScript scheduler is not fed by active packet files in runtime tick.
5. Worker assignment is preview-only and does not write inbox state.
6. Worker inbox does not feed a qualified execution loop.
7. Validator routing is not triggered by packet completion.
8. Validator results do not persist to packet or approval evidence.
9. Approval request is preview-only and not written to an active inbox.
10. Commit package builder does not consume packet/validator/approval evidence.
11. Recovery supervisor cannot replay a complete event stream.
12. Telemetry is consumed for visibility, but not as the canonical state-transition source.

## MCP Breakpoint Review

MCP is useful for reading and inspecting the surfaces involved in these breakpoints. It is not the closed-loop mechanism.

MCP can help with:

- read-only evidence collection
- morning brief generation
- repo-memory and authority inspection
- validator evidence discovery
- approval inbox visibility after the inbox is repaired

MCP cannot fix:

- packet-to-queue insertion
- queue-to-scheduler state projection
- scheduler-to-worker assignment persistence
- validator-result-to-approval handoff
- approval-to-commit-package evidence chain
- event schema reconciliation

Therefore MCP is a Phase 0 hands layer, not the primary loop closure fix. The first loop closure fix is canonical state projection from packets into queue/scheduler/assignment.

## Highest-Leverage Breakpoint

The highest-leverage breakpoint is Packet -> Canonical Queue.

Why:

- Goal intake already creates packets.
- Worker routing already reads packets.
- Validator and approval scripts already inspect packets or Git state.
- Runtime/scheduler code already has queue abstractions.
- The missing link is one durable queue projection that every downstream layer can consume.

Without this, every later layer keeps guessing which work exists now.
