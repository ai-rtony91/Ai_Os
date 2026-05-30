# AI_OS Telemetry Event Contract

## MISSION

Define the minimum durable telemetry event contract for AI_OS governed automation.

Telemetry is an accountable evidence layer. It exists to make orchestration activity inspectable, traceable, replayable, and auditable. It does not grant command authority, APPLY authority, approval authority, dashboard authority, or runtime execution authority.

Human authorization is the default. Automation is the exception.

## CURRENT STATUS: PARTIAL / Evidence-Only

Status label: `PARTIAL / Evidence-Only`

Current repo evidence shows that telemetry scaffolding exists, including:

- `telemetry/work_ledger.jsonl` as the intended durable ledger path.
- `services/telemetry/telemetryEvent.ts` for event construction.
- `services/telemetry/telemetryWriter.ts` for append behavior.
- `services/telemetry/telemetryReplay.ts` and `services/telemetry/automationAuditReplay.ts` for replay and audit views.
- `services/telemetry/runtimeVisibility.ts` for runtime visibility projections.
- `scripts/telemetry/Write-AIOSTelemetryEvent.ps1` and `scripts/telemetry/Get-AiOsAuditTimeline.ps1` for script-level telemetry write/replay support.

This status is not production-ready telemetry. Schema alignment is incomplete. Validator coverage is incomplete. Dashboard and runtime projections must be treated as derived evidence views, not authority. Any live dashboard wiring, worker automation, or runtime decision-making based on telemetry requires implementation review and a stable validator first.

## CANONICAL TELEMETRY PATH

The canonical durable telemetry ledger for Phase 1 is:

```text
telemetry/work_ledger.jsonl
```

Telemetry events must be append-only JSON Lines records. Runtime projections, dashboards, summaries, and replay views may read from telemetry, but they must not become authority over approval, APPLY, commit, push, merge, runtime execution, worker launch, dashboard launch, trading, broker access, or live automation.

## AUTHORITY

Telemetry is allowed to prove:

- that a recorded event was emitted by a stated source at a stated time;
- that a worker, lane, script, packet, operator action, validator, PR action, or recovery action produced evidence;
- that a validator, guard, checkpoint, or recovery step reported a result;
- that a derived dashboard or replay view had specific source evidence at the time it was generated;
- that a later reviewer can reconstruct the event sequence when the event records are complete and valid.

Telemetry is not allowed to approve:

- APPLY;
- operator approval;
- command execution;
- worker launch;
- runtime mutation;
- registry changes;
- dashboard live wiring;
- commits, pushes, merges, branch deletion, or PR approval;
- trading, broker, webhook, scheduled-task, startup-task, or live execution behavior.

Telemetry events are evidence, not execution authority. Operator approval remains separate from telemetry records. A telemetry record may document that an approval decision happened, but it is not the approval mechanism and must not replace the human-controlled approval process.

## CHAIN OF CUSTODY

Every durable event should support traceability from source action to recorded event.

When available, telemetry events must identify:

- originating lane;
- originating worker or operator;
- emitting script, service, dashboard, validator, or helper;
- packet, approval, checkpoint, PR, branch, or validation reference;
- repository path and branch;
- input evidence used to produce the event;
- output evidence created by the event;
- result and next safe action.

Events should preserve enough context to reconstruct what happened later without relying on screenshots, memory, or informal chat notes. If a field is unknown at emission time, the event should use an explicit governed value such as `UNKNOWN`, `null`, or `requires implementation review`; it must not invent authority or imply certainty.

## SCHEMA ALIGNMENT STATUS

Current implemented telemetry shape appears to use camelCase fields and short timestamp names. Repo evidence includes fields such as:

- `eventId`
- `eventType`
- `packetId`
- `approvalId`
- `status`
- `risk`
- `ts`

The governance/canonical target uses snake_case fields and explicit authority fields, including:

- `event_id`
- `event_type`
- `timestamp_utc`
- `mode`
- `authority_token`
- `authority_note`
- `result`
- `risk_level`
- `next_safe_action`
- `validation_status`

This mismatch is intentional to document, not resolve, in this governance lane. Telemetry remains `PARTIAL / Evidence-Only` until a separate implementation PR reconciles the implemented event schema with the canonical governance schema and adds validation coverage.

No document, dashboard, script, or runtime component should claim production-ready telemetry until schema reconciliation and validator coverage are implemented.

## LEGACY FIELD MAPPING

Phase 1 read-side validators may classify existing camelCase records as legacy-mapped evidence when the core legacy fields are present and parseable. This mapping is compatibility evidence only; it must not rewrite `telemetry/work_ledger.jsonl`, silently repair prior events, or promote legacy records into command authority.

| Legacy field | Canonical field | Mapping note |
|---|---|---|
| `eventId` | `event_id` | Direct identifier mapping. |
| `eventType` | `event_type` | Direct event-type mapping. |
| `ts` | `timestamp_utc` | Must parse as an ISO 8601 timestamp. |
| `status` | `result` | Legacy status is evidence-only until taxonomy reconciliation. |
| `risk` | `risk_level` | Legacy risk is evidence-only until taxonomy reconciliation. |
| `packetId` | `authority_token` or `input_reference` | Packet reference only; it does not grant approval. |
| `approvalId` | `authority_token` or `input_reference` | Approval reference only; it does not replace approval inbox authority. |
| `source` | `source` | Direct source mapping when present. |
| `summary` | `output_reference` or `next_safe_action` | Human-readable evidence summary, not command authority. |

Canonical snake_case records are preferred for new writers. Legacy camelCase records remain readable as evidence-only until a separate approved migration or corrective-event strategy exists.

## TARGET CANONICAL EVENT FIELDS

Every durable telemetry event should converge on these target canonical fields:

| Field | Purpose |
|---|---|
| `event_id` | Unique event identifier for audit reference and corrective-event linking. |
| `timestamp_utc` | UTC ISO 8601 event timestamp for chronological reconstruction. |
| `event_type` | Controlled event name from the approved telemetry taxonomy. |
| `source` | Script, service, worker, dashboard, validator, or operator-controlled process that emitted the event. |
| `actor` | Human operator, Codex worker, Claude reviewer, ChatGPT planner, script identity, or service identity when known. |
| `lane` | Approved work lane or `UNKNOWN` when not applicable. |
| `repo_path` | Repository path where the action occurred. |
| `branch` | Git branch associated with the action when applicable. |
| `mode` | Governed mode such as `READ_ONLY`, `DRY_RUN`, `APPLY`, `VALIDATION`, or `RECOVERY`. |
| `authority_token` | Reference to the governing work packet, approval token, or `null` when not applicable. |
| `authority_note` | Plain-language statement that telemetry is evidence and not approval authority. |
| `input_reference` | File, packet, command, PR, validator, or source evidence used as input. |
| `output_reference` | Ledger entry, report, checkpoint, PR, validation output, or derived artifact created. |
| `result` | Governed outcome such as `PASS`, `WARN`, `FAIL`, `BLOCKED`, `RECORDED`, or `PARTIAL`. |
| `risk_level` | Risk classification such as `LOW`, `MEDIUM`, `HIGH`, or `BLOCKED`. |
| `next_safe_action` | One concrete next safe action or stop condition. |
| `validation_status` | Validation state such as `NOT_RUN`, `PASS`, `FAIL`, `PARTIAL`, or `requires implementation review`. |

Telemetry records must not contain secrets, API keys, credentials, broker tokens, private keys, recovery keys, live order payloads, or sensitive environment values.

## CONTROL CATEGORIES

Telemetry events should be organized into control categories that make audit review and dashboard provenance clear:

| Control Category | Purpose |
|---|---|
| `operator_approval` | Evidence of approval request, review, decision, expiration, or rejection. |
| `worker_start` | Evidence that a bounded worker lane started under stated authority. |
| `worker_stop` | Evidence that a worker stopped, completed, or blocked. |
| `validation_result` | Evidence of validator, diff, test, or check output. |
| `registry_guard_result` | Evidence of registry or protected-scope guard outcome. |
| `checkpoint_created` | Evidence that a governed checkpoint was created. |
| `pr_created` | Evidence that a PR was opened for a lane. |
| `pr_checked` | Evidence that PR checks or review state were inspected. |
| `pr_merged` | Evidence that an approved PR merge occurred. |
| `blocked_action` | Evidence that a rule, scope gate, validator, or approval gate blocked action. |
| `error_recovery` | Evidence of a failure recovery response and next safe action. |
| `dashboard_snapshot` | Evidence backing a dashboard status view at a point in time. |
| `telemetry_health_check` | Evidence of ledger parseability, schema validity, or replay health. |

## EVENT CONTRACT TABLE

| Event | Required When | Purpose | Authority Boundary |
|---|---|---|---|
| `operator_approval_requested` | Human approval is requested | Record that operator review is needed | Does not imply approval |
| `operator_approval_recorded` | A human approval decision is recorded | Preserve decision evidence | Decision must come from human-controlled approval process |
| `worker_started` | A governed worker begins a lane | Record lane, branch, mode, and authority evidence | Does not expand worker scope |
| `worker_stopped` | A worker completes, stops, or blocks | Record result and next safe action | Does not approve follow-up work |
| `validation_result_recorded` | Validator, diff, check, or test output exists | Preserve validation evidence | Validator output does not approve APPLY |
| `registry_guard_result_recorded` | Registry or protected-scope guard is inspected | Preserve guard evidence | Guard evidence is not execution authority |
| `checkpoint_created` | A governed checkpoint is created | Preserve reporting and recovery point evidence | Checkpoint does not approve execution |
| `pr_created` | A PR is created | Preserve PR traceability | PR existence does not approve merge |
| `pr_checked` | PR checks or review state are inspected | Preserve CI/review evidence | Passing checks do not replace operator approval |
| `pr_merged` | An approved PR merge occurs | Preserve merge evidence | Requires separate merge authority |
| `blocked_action_recorded` | A rule, gate, validator, or scope check blocks action | Preserve stop reason and recovery path | Block remains until resolved by approved process |
| `error_recovery_recorded` | A failure recovery response is produced | Preserve failure and next safe action | Recovery evidence does not authorize mutation |
| `dashboard_snapshot_recorded` | A dashboard status view is generated | Preserve source provenance | Dashboard output is a derived view |
| `telemetry_health_checked` | Ledger/schema/replay health is inspected | Preserve telemetry health evidence | Health status does not grant automation authority |

Legacy or currently implemented event names such as `packet_dispatched`, `packet_blocked`, `packet_applied`, `approval_requested`, `approval_decided`, `clean_state_checked`, and `policy_decision` require implementation review before being promoted, mapped, or deprecated.

## AUDIT REQUIREMENTS

Future telemetry must support:

- chronological reconstruction of the governed work sequence;
- worker accountability by lane, branch, actor, and source;
- PR and branch traceability from work packet to commit and PR outcome;
- validation evidence attached to the relevant action;
- blocked-action evidence with rule, gate, or validator reason;
- failure recovery evidence with the next safe action;
- dashboard status provenance showing which ledger events support each visible status;
- detection of invalid, incomplete, or schema-mismatched lines;
- corrective events that reference prior event IDs without overwriting history.

## RISK CONTROLS

Telemetry must not trigger automation by itself.

Telemetry must not:

- approve execution;
- mask failed validations;
- overwrite evidence;
- silently repair or delete invalid evidence;
- convert dashboard state into command authority;
- treat mock, fixture, sample, or replay data as live/read-only operational data;
- write secrets, credentials, private keys, broker tokens, or live order payloads;
- authorize runtime launchers, daemons, worker loops, startup tasks, or scheduled tasks.

Telemetry must distinguish mock/fixture data from live/read-only data. Dashboard wiring must wait until schema reconciliation and telemetry validators are stable.

## CHECKPOINT ALIGNMENT

Telemetry checkpoints must align with `docs/AI_OS/reporting/AIOS_REPORTING_AND_CHECKPOINT_STANDARD.md`.

Required checkpoint types:

- `pre_execution_checkpoint`
- `post_execution_checkpoint`
- `validation_checkpoint`
- `pr_checkpoint`
- `recovery_checkpoint`
- `end_of_day_checkpoint`

Each checkpoint should identify the lane, actor, repo path, branch, mode, source evidence, validation status, result, risk level, and next safe action. Checkpoints are evidence and recovery aids. They do not approve execution or replace operator decisions.

## APPEND-ONLY DOCTRINE

Telemetry is evidence, not authority.

Durable telemetry must be append-only. Existing telemetry records must not be edited in place to change history. If an event is wrong, stale, incomplete, or superseded, emit a new corrective event that references the prior event.

Append-only telemetry may support:

- audit review;
- replay;
- status reconstruction;
- validator evidence tracking;
- operator visibility;
- automation stop reasons;
- readiness trend analysis;
- dashboard status provenance.

Append-only telemetry must not:

- approve APPLY;
- override approval gates;
- mutate packet state by itself;
- grant commit, push, merge, or branch authority;
- authorize runtime, dashboard, trading, broker, webhook, startup task, scheduled task, or worker-loop execution.

DRY_RUN may emit telemetry evidence only when doctrine explicitly allows that evidence write. A DRY_RUN evidence write must still be append-only and must not mutate command state, approval state, packet state, runtime state, or validator state.

## PHASE 1 MINIMUM BASELINE

AI_OS Phase 1 telemetry is not considered minimally ready for governed automation until these durable event flows exist and pass schema validation:

1. Operator approval requests and decisions emit auditable evidence.
2. Worker start and stop events identify lane, actor, branch, mode, and source.
3. Validation results are attached to the relevant packet, branch, PR, or action.
4. Registry guard outcomes are preserved as evidence.
5. Checkpoints are emitted for pre-execution, post-execution, validation, PR, recovery, and end-of-day events.
6. PR creation, check inspection, and merge events preserve branch and PR traceability.
7. Automation stops emit blocked-action evidence and next safe action.
8. Error recovery emits structured recovery evidence.
9. Dashboard snapshots identify source ledger entries and data freshness.
10. Telemetry health checks verify schema validity and replay health.
11. Replay can read the durable ledger without treating replay output as authority.

Until this baseline exists, automation must remain read-only, operator-triggered, or explicitly scoped to evidence collection.

## NEXT SAFE IMPLEMENTATION PR

The next safe implementation PR should be limited to telemetry schema reconciliation and validation. It should likely include:

- a telemetry event validator;
- reconciliation between implemented camelCase fields and target canonical snake_case fields;
- a ledger validation command;
- fixture/evidence samples only if explicitly approved;
- documentation of any legacy-to-canonical event mapping;
- no dashboard live wiring until the validator exists and passes.

This implementation requires review of `services/telemetry/`, `scripts/telemetry/`, dashboard readers, runtime visibility readers, and any current ledger examples before mutation.

## NON-GOALS

This contract does not:

- implement telemetry writers;
- change runtime behavior;
- change validator behavior;
- create approval authority;
- create automation authority;
- authorize APPLY;
- authorize commit or push;
- authorize dashboard live wiring;
- authorize trading, broker, OANDA, webhook, real order, API key, startup task, scheduled task, daemon, launcher, or worker-loop behavior;
- define a complete long-term event-sourcing system;
- replace approval inbox, approval gate, validator chain, worker registry, worker profiles, lock registry, or source-of-truth governance.

## DECISION-NEEDED ITEMS

The operator must decide before Phase 1 instrumentation:

1. Whether append-only telemetry writes are allowed from DRY_RUN scripts.
2. Which script or service owns the canonical Phase 1 telemetry writer interface.
3. Whether existing TypeScript and PowerShell telemetry field names should be adapted to this governance contract or mapped through a compatibility layer.
4. Which validator should verify telemetry event shape after instrumentation.
5. Whether telemetry schema definitions belong in `docs/governance/`, `schemas/`, or both.
6. How corrective events should reference prior events.
7. Whether packet and approval identifiers must be required for all orchestration events or nullable where not applicable.
8. Which mission-control exports are allowed to emit evidence without changing runtime state.
9. Which dashboard views may display telemetry as non-authoritative evidence after validator coverage exists.
