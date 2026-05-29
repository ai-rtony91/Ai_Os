# AIOS_CLOSED_LOOP_STATE_CONTRACT_V1

Packet: AIOS-CLOSED-LOOP-STATE-CONTRACT-DESIGN-DRYRUN-001
Mode: DRY_RUN report creation only
Branch inspected: phase-night-supervisor-layer2-memory
Worktree: C:\Dev\Ai.Os

## Purpose

This contract defines the smallest shared state model needed to close:

```text
Goal -> Packet -> Queue -> Scheduler -> Worker Resolver
```

It does not authorize implementation, queue mutation, packet mutation, worker assignment persistence, MCP work, commits, pushes, merges, runtime execution, approval mutation, or trading work.

## Design Boundary

This is a read-model contract first.

V1 should normalize existing packet and queue evidence into one shared vocabulary without changing active packet files. Mutation comes later through separate approved APPLY lanes.

## State Contract Summary

Canonical packet states:

```text
proposed
queued
assigned
running
validated
approval_pending
approved
completed
blocked
failed
```

Primary rule:

`packet.current_state` is the only state field downstream consumers should read.

Legacy fields may remain as source evidence but must be projected into `current_state`.

## Packet Schema

Minimum packet record:

| Field | Required | Type | Purpose |
|---|---:|---|---|
| `contract_version` | yes | string | Must equal `AIOS_CLOSED_LOOP_STATE_CONTRACT_V1`. |
| `packet_id` | yes | string | Stable unique packet id. |
| `goal_id` | no | string | Parent goal/intake id when known. |
| `title` | yes | string | Human-readable work title. |
| `current_state` | yes | enum | One canonical state from this contract. |
| `legacy_state` | no | string | Original state/status from existing packet/queue source. |
| `state_source` | yes | string | Source file or subsystem used to project state. |
| `lane` | no | string | Worker lane or operating lane. |
| `risk_level` | yes | enum | `low`, `medium`, `high`, `protected`, or `unknown`. |
| `allowed_paths` | no | array | Paths the packet may touch. |
| `forbidden_paths` | yes | array | Protected paths and steel-door exclusions. |
| `dependencies` | no | array | Packet ids that must complete first. |
| `blockers` | no | array | Current blocker ids or reason strings. |
| `validator_hooks` | no | array | Validator ids or routing hints required later. |
| `approval_hooks` | no | array | Approval gates required later. |
| `created_at` | yes | string | ISO-8601 timestamp if available; otherwise projection timestamp. |
| `updated_at` | yes | string | ISO-8601 timestamp if available; otherwise projection timestamp. |
| `queue_projection_id` | no | string | Queue read-model id once projected. |

## Queue Schema

Minimum queue projection:

| Field | Required | Type | Purpose |
|---|---:|---|---|
| `contract_version` | yes | string | Must equal `AIOS_CLOSED_LOOP_STATE_CONTRACT_V1`. |
| `projection_id` | yes | string | Unique queue projection run id. |
| `generated_at` | yes | string | Projection timestamp. |
| `source_roots` | yes | array | Packet/queue roots used as inputs. |
| `records` | yes | array | Normalized packet records. |
| `counters` | yes | object | Counts by canonical state. |
| `blocked_records` | yes | array | Records blocked by dependencies, risk, missing ownership, or invalid state. |
| `scheduler_ready_records` | yes | array | Records eligible for scheduler preview. |
| `manual_review_records` | yes | array | Records that cannot be safely scheduled. |
| `warnings` | yes | array | Non-blocking projection issues. |
| `errors` | yes | array | Blocking projection issues. |

Minimum queue record:

| Field | Required | Type | Purpose |
|---|---:|---|---|
| `packet_id` | yes | string | Packet id. |
| `current_state` | yes | enum | Canonical state. |
| `priority` | no | integer | Scheduler ordering hint. |
| `risk_level` | yes | enum | Used to prevent protected auto-routing. |
| `dependencies` | no | array | Blocking packet ids. |
| `blocked_reason` | no | string | Why scheduler must skip it. |
| `scheduler_eligible` | yes | boolean | Whether scheduler may plan it. |
| `resolver_eligible` | yes | boolean | Whether worker resolver may preview it. |
| `recommended_next_action` | yes | string | Human-readable next action. |

## State Names

| Canonical state | Meaning | Scheduler eligible | Worker resolver eligible | Notes |
|---|---|---:|---:|---|
| `proposed` | Packet proposal exists but is not accepted into queue | no | no | Requires approval/intake acceptance. |
| `queued` | Accepted durable work item waiting for scheduling | yes | yes | First schedulable state. |
| `assigned` | Worker assignment exists or is ready to persist | no | no | Assignment writer owns persistence later. |
| `running` | Worker is actively executing | no | no | V1 does not execute workers. |
| `validated` | Work has validator evidence | no | no | Downstream approval hook. |
| `approval_pending` | Approval package is waiting for human decision | no | no | Human-gated. |
| `approved` | Human approval exists for the next protected step | no | no | Does not imply commit/push/merge. |
| `completed` | Packet lifecycle complete | no | no | Terminal success state. |
| `blocked` | Cannot proceed until blocker clears | no | no | Requires blocker reason. |
| `failed` | Execution/validation/projection failed | no | no | Requires retry/escalation policy later. |

## Allowed Transitions

| From | To | Owner | Required evidence |
|---|---|---|---|
| none | `proposed` | Goal intake | Goal text or packet proposal. |
| `proposed` | `queued` | Queue projection / future intake acceptor | Valid packet id, safe paths, no protected blocker. |
| `queued` | `assigned` | Future assignment writer | Scheduler preview and worker resolver output. |
| `assigned` | `running` | Future worker execution gate | Human-approved execution lane. |
| `running` | `validated` | Validator router/evidence writer | Packet-scoped validator result. |
| `validated` | `approval_pending` | Approval request writer | Validator evidence and approval requirement. |
| `approval_pending` | `approved` | Human approval gate | Human decision record. |
| `approved` | `completed` | Packet state mover / future commit package flow | Completion evidence. |
| any non-terminal | `blocked` | Projection, scheduler, resolver, validator, approval, or recovery | Blocker reason. |
| any non-terminal | `failed` | Validator, worker, projection, or recovery | Failure reason and retry count. |
| `blocked` | `queued` | Human or recovery gate | Blocker cleared evidence. |
| `failed` | `queued` | Human or recovery gate | Retry approved and retry ceiling not exceeded. |

Forbidden V1 transitions:

- `queued` -> `running` without `assigned`.
- `proposed` -> `assigned` without `queued`.
- `validated` -> `completed` without approval check when approval is required.
- Any state -> commit, push, merge, deploy, trading, broker, OANDA, secrets, or credential action.

## Ownership Rules

| Layer | Owns | Does not own |
|---|---|---|
| Goal intake | `proposed` packet creation | Queue truth, worker assignment, validation, approval. |
| Packet store | Durable packet source files | Scheduler decisions. |
| Queue projection | Normalized read model and canonical `current_state` projection | Mutating packet files in V1. |
| Scheduler | Scheduling plan from `queued` records | Worker selection authority or inbox writes. |
| Worker resolver | Worker selection preview from scheduler-ready records | Inbox persistence or execution. |
| Validator router | Future validator hook selection | V1 queue admission. |
| Approval system | Future approval hooks and human decision state | Auto-approval. |
| Human operator | Protected decisions | Routine projection computation. |

## Scheduler Inputs

Scheduler V1 input should be the queue projection, not raw packet folders or command queue files.

Required scheduler input:

| Field | Source | Rule |
|---|---|---|
| `packet_id` | Queue projection record | Required. |
| `current_state` | Queue projection record | Must equal `queued`. |
| `priority` | Packet or default projection policy | Higher priority first after safety filters. |
| `risk_level` | Packet or classification fallback | `protected` and `unknown` cannot auto-route. |
| `dependencies` | Packet or task graph evidence | All dependencies must be `completed` or approved equivalent. |
| `allowed_paths` | Packet | Must not overlap forbidden/protected paths. |
| `blockers` | Queue projection | Must be empty. |

Scheduler V1 output:

| Field | Purpose |
|---|---|
| `packet_id` | Work being planned. |
| `scheduler_action` | `preview_assignment`, `manual_review`, or `blocked`. |
| `reason` | Why the action was selected. |
| `resolver_input` | Minimal object passed to worker resolver preview. |

## Worker Resolver Inputs

Worker resolver V1 input comes from scheduler output.

Required resolver input:

| Field | Rule |
|---|---|
| `packet_id` | Required. |
| `lane` | Required when known; unknown becomes manual review. |
| `allowed_paths` | Required for path ownership checks. |
| `forbidden_paths` | Required; protected overlap blocks routing. |
| `risk_level` | `low` or `medium` only for preview routing. |
| `required_capabilities` | Derived from packet tags or lane. |
| `dependencies_clear` | Must be true. |

Resolver V1 output:

| Field | Rule |
|---|---|
| `packet_id` | Echo input. |
| `recommended_worker_id` | Worker id or null. |
| `resolver_status` | `resolved`, `manual_review`, or `blocked`. |
| `reason` | Required. |
| `assignment_preview` | Human-readable assignment evidence only. |

Rule:

Unknown ownership must produce `manual_review`, not fallback-to-default worker assignment.

## Validator Hooks

V1 does not execute validators. It only reserves the hook fields needed by later lanes.

Minimum validator hook:

| Field | Purpose |
|---|---|
| `validator_id` | Validator or validator route id. |
| `trigger_state` | Usually `running` -> `validated` later. |
| `required_for_states` | States that cannot proceed without this evidence. |
| `evidence_path` | Future packet-scoped result path. |
| `fail_state` | Usually `failed` or `blocked`. |

Initial hook rule:

Any packet with `risk_level` of `protected` or `unknown` must include a validator/approval hook that blocks scheduler eligibility.

## Approval Hooks

V1 does not persist approvals. It only reserves approval hook fields for later approval inbox repair.

Minimum approval hook:

| Field | Purpose |
|---|---|
| `approval_id` | Approval item id once created. |
| `required_for_transition` | Transition requiring human decision. |
| `approval_status` | `not_requested`, `pending`, `approved`, `rejected`, or `blocked`. |
| `risk_summary` | Short reason the operator must decide. |
| `evidence_paths` | Validator, packet, scheduler, and resolver evidence. |

Rule:

Approval hooks cannot self-approve. They only prepare the human decision.

## Current State -> Future State Mapping

| Current State | Future State | Consumer | Producer |
|---|---|---|---|
| packet builder `proposed` | `proposed` | Queue projection | Goal intake / packet proposal |
| packet builder `active` | `queued` when safe and unassigned | Queue projection, scheduler | Work packet builder |
| packet mover `active` | `queued` | Queue projection, scheduler | Packet state mover |
| packet mover `routed` | `assigned` | Worker inbox, resolver reports | Packet state mover / router |
| packet mover `dry_run_done` | `validated` if validator evidence exists, otherwise `running` or `blocked` | Validator/approval hooks | Packet state mover |
| packet mover `awaiting_approval` | `approval_pending` | Approval system | Packet state mover |
| packet mover `approved` | `approved` | Commit package / completion flow | Approval gate |
| packet mover `applying` | `running` | Validator/recovery | Packet state mover |
| packet mover `validated` | `validated` | Approval hooks | Validator evidence |
| packet mover `complete` | `completed` | Scorecard/recovery | Packet state mover |
| packet mover `blocked` | `blocked` | Scheduler/recovery | Any blocker owner |
| packet mover `failed` | `failed` | Scheduler/recovery | Validator/worker/projection |
| TypeScript `scheduled` | `queued` or `assigned` depending assignment evidence | Scheduler | Packet queue |
| TypeScript `executing` | `running` | Validator/recovery | Packet queue |
| TypeScript `retrying` | `queued` with retry metadata | Scheduler/recovery | Packet queue |
| TypeScript `waiting_approval` | `approval_pending` | Approval system | Packet queue |
| TypeScript `applied` | `running` or `approved` depending evidence | Commit/approval hooks | Packet queue |
| TypeScript `completed` | `completed` | Scorecard/recovery | Packet queue |
| TypeScript `dead_letter` | `failed` | Recovery/SOS | Packet queue |
| TypeScript `manual_review` | `blocked` | Human operator | Packet queue |
| Dispatcher `ASSIGNED` | `assigned` | Worker inbox/resolver | Dispatcher queue |
| Dispatcher `DONE` | `completed` | Scorecard/recovery | Dispatcher queue |

## Duplicate State Names

| State name | Duplicate locations | Contract decision |
|---|---|---|
| `active` | Packet builder, packet mover, runtime advancement | Replace with `queued` unless assignment/running evidence exists. |
| `approved` | Packet mover, runtime advancement, TypeScript queue | Keep as canonical only for human-approved state. |
| `blocked` | Packet mover, TypeScript queue | Keep canonical. |
| `failed` | Packet mover, TypeScript queue | Keep canonical. |
| `validated` | Packet mover, runtime advancement | Keep canonical only when validator evidence exists. |

## Conflicting State Names

| Current name | Conflict | Contract mapping |
|---|---|---|
| `active` | Could mean available work, current work, or simply file folder | `queued` unless stronger evidence says otherwise. |
| `routed` | Could mean selected worker, lane, or only recommendation | `assigned` only if worker id evidence exists; otherwise `queued`. |
| `dry_run_done` | Could mean execution completed or only preview completed | `validated` only with validator evidence; otherwise `blocked` for review. |
| `applying` | Protected mutation state, unsafe for unattended flow | `running` and human-gated. |
| `scheduled` | Planned but not necessarily assigned | `queued` until assignment evidence exists. |
| `applied` | Could imply mutation happened but not approval/completion | `running`, `approved`, or `blocked` depending evidence; must not auto-complete. |
| `DONE` | Dispatcher queue success term | `completed` only with packet match. |
| `ASSIGNED` | Dispatcher queue assignment term | `assigned` only with worker id and packet match. |

## Missing State Names

| Missing state | Why needed |
|---|---|
| `queued` | Durable accepted work item waiting for scheduler. |
| `assigned` | Worker resolution has happened but execution has not necessarily started. |
| `running` | Work is actively being attempted. |
| `approval_pending` | Validator/evidence package is waiting for human decision. |
| `completed` | Canonical terminal success state distinct from legacy `complete` or `DONE`. |

## Producer / Consumer Contract

| Producer | Output | Consumer | Contract rule |
|---|---|---|---|
| Goal intake | Packet proposal | Packet builder / queue projection | Produces `proposed`, not `queued`, unless accepted by future gate. |
| Work packet builder | Packet file | Queue projection | Packet file is source evidence, not queue truth by itself. |
| Queue projection | Queue read model | Scheduler | Only projection emits scheduler-ready records. |
| Scheduler | Assignment preview input | Worker resolver | Scheduler does not choose worker directly. |
| Worker resolver | Worker recommendation | Future assignment writer | Resolver preview does not persist assignment. |
| Validator router | Validator hook/evidence later | Approval hooks | Validator result must be packet-scoped before approval. |
| Approval writer | Approval item later | Commit package builder | Approval does not commit/push/merge. |

## Rollback Strategy

V1 rollback is simple because V1 should be read-only.

If a future APPLY lane creates the contract files and validation fails:

1. Remove only the newly added contract artifact or revert only the exact contract edits.
2. Do not mutate packet, queue, worker inbox, approval inbox, runtime, telemetry, or service files.
3. Restore consumers to reading legacy state fields.
4. Re-run `git diff --check`.
5. Re-run any schema validator added in that APPLY lane.

For later mutation lanes:

- Queue projection failure rolls back by deleting the generated projection file only.
- Scheduler preview failure rolls back by disabling projection input and returning to preview-only mode.
- Worker resolver failure rolls back by not writing assignment state.
- Assignment writer failure must never partially write inbox state; use temp file plus atomic replace in later implementation.

## Smallest Safe APPLY

The smallest safe APPLY should create the state contract and mapping only. It should not alter active packet, queue, scheduler, resolver, validator, approval, runtime, or telemetry behavior.

Recommended lane:

```text
AIOS-CLOSED-LOOP-STATE-CONTRACT-APPLY-001
```

Exact files that would require modification or creation later:

| File | Action | Why |
|---|---|---|
| `schemas/aios/orchestration/AIOS_CLOSED_LOOP_STATE_CONTRACT_V1.schema.json` | create | Machine-readable contract for packet and queue projection records. |
| `docs/workflows/WORKER_TASK_LIFECYCLE_STANDARD.md` | update only if approved | Add pointer to canonical `current_state` vocabulary. |
| `automation/orchestration/work_packets/New-AiOsWorkPacket.ps1` | later update | Emit or preserve fields needed for projection; not in first APPLY. |
| `automation/orchestration/work_packets/Move-AiOsPacketState.ps1` | later update | Map legacy transitions to canonical state; not in first APPLY. |
| `automation/orchestration/runtime/Invoke-AiOsRuntimePacketAdvancement.ps1` | later update | Stop direct divergent status mutation; not in first APPLY. |
| `services/dispatcher/packetQueue.ts` | later update | Align TypeScript packet states with canonical mapping. |
| `services/dispatcher/autonomousScheduler.ts` | later update | Consume canonical queue projection. |
| `services/runtime/runtimeTick.ts` | later update | Pass packet queue snapshot/projection into scheduler. |
| `automation/orchestration/workers/Resolve-AiOsWorkerForPacket.DRY_RUN.ps1` | later update | Accept scheduler resolver input and manual-review unknown ownership. |
| `automation/orchestration/workers/inbox/Add-AiOsWorkerInboxItem.DRY_RUN.ps1` | later replace or supplement | Current path is preview-only; assignment writer must be separate. |
| `automation/orchestration/validators/Get-AiOsValidatorRecommendation.DRY_RUN.ps1` | later update | Accept packet id and packet-scoped changed-file inputs. |
| `automation/orchestration/approval_inbox/New-AiOsPacketApprovalRequest.DRY_RUN.ps1` | later update | Consume packet-scoped validation evidence. |
| `automation/orchestration/commit_packages/New-AiOsCommitPackageRecommendation.DRY_RUN.ps1` | later update | Consume packet id, approval id, validator evidence, and allowed files. |

First APPLY allowed scope should be only:

```text
schemas/aios/orchestration/AIOS_CLOSED_LOOP_STATE_CONTRACT_V1.schema.json
```

Optional docs pointer:

```text
docs/workflows/WORKER_TASK_LIFECYCLE_STANDARD.md
```

Do not include automation or services in the first APPLY.

## V1 Acceptance Criteria

V1 is done when:

1. The canonical states exist in one schema.
2. Legacy state mapping exists in one table.
3. Queue projection records can be validated against the schema.
4. Scheduler eligibility can be determined from `current_state`, `risk_level`, dependencies, blockers, and path safety.
5. Worker resolver input can be produced without writing worker inbox state.
6. Unknown ownership routes to `manual_review` or `blocked`, never fallback assignment.
