# AI_OS Telemetry Event Contract

## MISSION

Define the minimum durable telemetry event contract for AI_OS Phase 1.

This contract exists to make orchestration activity inspectable and replayable as evidence. It does not grant command authority, APPLY authority, approval authority, or runtime execution authority.

Human authorization is the default. Automation is the exception.

## CANONICAL TELEMETRY PATH

The canonical durable telemetry ledger for Phase 1 is:

```text
telemetry/work_ledger.jsonl
```

Telemetry events must be append-only JSON Lines records. Runtime projections, dashboards, summaries, and replay views may read from telemetry, but they must not become authority over approval, APPLY, commit, push, merge, or runtime execution.

## EVENT CONTRACT TABLE

| Event | Required When | Purpose | Authority Boundary |
|---|---|---|---|
| `packet_created` | A work packet is created | Record the start of a packet lifecycle | Does not authorize work beyond the approved packet scope |
| `packet_transition_requested` | A packet state transition is requested or previewed | Record intent before state changes | Does not authorize the transition |
| `packet_transition_applied` | An approved packet state transition is applied | Record the completed state change | Requires prior approval when entering protected states |
| `approval_requested` | Human approval is requested | Record that operator review is needed | Does not imply approval |
| `approval_gate_checked` | An approval gate is inspected | Record the gate result used for review | Does not grant APPLY authority |
| `approval_decision_recorded` | A human approval decision is recorded | Preserve decision evidence | Decision must come from human-controlled approval process |
| `operator_control_snapshot` | Operator control-loop state is captured | Record readiness, blockers, and next safe action | Snapshot is guidance, not authority |
| `mission_state_exported` | Mission state is exported for review | Record mission status evidence | Export is evidence, not command authority |
| `automation_blocked` | Automation stops because a rule, gate, validator, or scope check blocks it | Preserve the stop reason and recovery path | Block remains until resolved by approved process |
| `validator_evidence_recorded` | Validator output is associated with a packet or action | Preserve validation evidence | Validator output does not approve APPLY |

## REQUIRED EVENT FIELDS

Every durable telemetry event must include:

| Field | Requirement |
|---|---|
| `schema` | Stable schema name for the event record |
| `event_type` | One of the required Phase 1 event names |
| `event_id` | Unique event identifier |
| `timestamp_utc` | UTC timestamp in ISO 8601 format |
| `source` | Script, service, worker, or system component that emitted the event |
| `mode` | `DRY_RUN`, `APPLY`, `READ_ONLY`, or another explicit governed mode |
| `packet_id` | Packet identifier when applicable; otherwise `null` |
| `worker_id` | Worker or operator identifier when known; otherwise `UNKNOWN` |
| `lane_id` | Lane identifier when known; otherwise `UNKNOWN` |
| `summary` | Human-readable event summary |
| `authority_note` | Plain statement that telemetry is evidence and not approval authority |
| `approval_id` | Approval identifier when applicable; otherwise `null` |
| `validator_id` | Validator identifier when applicable; otherwise `null` |
| `result` | `PASS`, `WARN`, `BLOCKED`, `RECORDED`, or another governed result value |
| `next_safe_action` | One concrete next action or stop condition |
| `metadata` | Structured supplemental context; must not contain secrets |

Telemetry records must not contain secrets, API keys, credentials, broker tokens, private keys, recovery keys, live order payloads, or sensitive environment values.

## APPEND-ONLY DOCTRINE

Telemetry is evidence, not authority.

Durable telemetry must be append-only. Existing telemetry records must not be edited in place to change history. If an event is wrong, stale, incomplete, or superseded, emit a new corrective event that references the prior event.

Append-only telemetry may support:

- audit review
- replay
- status reconstruction
- validator evidence tracking
- operator visibility
- automation stop reasons
- readiness trend analysis

Append-only telemetry must not:

- approve APPLY
- override approval gates
- mutate packet state by itself
- grant commit, push, merge, or branch authority
- authorize runtime, dashboard, trading, broker, webhook, startup task, or scheduled task execution

DRY_RUN may emit telemetry evidence only when doctrine explicitly allows that evidence write. A DRY_RUN evidence write must still be append-only and must not mutate command state, approval state, packet state, runtime state, or validator state.

## AUTHORITY BOUNDARIES

Approval gates remain human-controlled.

Telemetry may report that an approval was requested, checked, granted, rejected, blocked, or expired. Telemetry must not be treated as the approval itself.

Validator output is evidence and validation guidance only. Validators do not grant APPLY authority.

Runtime projections, dashboard views, mission exports, status summaries, and replay output are derived views. They may inform operator decisions, but they must not become canonical command authority.

APPLY requires operator approval. Commit and push require separate operator approval after validation and exact-file review.

## PHASE 1 MINIMUM BASELINE

AI_OS Phase 1 telemetry is not considered minimally ready for governed automation until these durable event flows exist:

1. Packet creation emits `packet_created`.
2. Packet transition preview/request emits `packet_transition_requested`.
3. Approved packet transition application emits `packet_transition_applied`.
4. Approval inbox or gate review emits `approval_requested` and `approval_gate_checked`.
5. Human approval decisions emit `approval_decision_recorded`.
6. Operator control-loop reports emit `operator_control_snapshot`.
7. Mission state exports emit `mission_state_exported`.
8. Automation stops emit `automation_blocked`.
9. Validator outputs tied to packets or actions emit `validator_evidence_recorded`.
10. Replay can read the durable ledger without treating replay output as authority.

Until this baseline exists, automation must remain read-only, operator-triggered, or explicitly scoped to evidence collection.

## NON-GOALS

This contract does not:

- implement telemetry writers
- change runtime behavior
- change validator behavior
- create approval authority
- create automation authority
- authorize APPLY
- authorize commit or push
- authorize dashboard changes
- authorize trading, broker, OANDA, webhook, real order, API key, startup task, or scheduled task behavior
- define a complete long-term event-sourcing system
- replace approval inbox, approval gate, validator chain, worker registry, worker profiles, lock registry, or source-of-truth governance

## DECISION-NEEDED ITEMS

The operator must decide before Phase 1 instrumentation:

1. Whether append-only telemetry writes are allowed from DRY_RUN scripts.
2. Which script or service owns the canonical Phase 1 telemetry writer interface.
3. Whether existing TypeScript telemetry field names should be adapted to this governance contract or this contract should mirror the current TypeScript schema names.
4. Which validator should verify telemetry event shape after instrumentation.
5. Whether telemetry schema definitions belong in `docs/governance/`, `schemas/`, or both.
6. How corrective events should reference prior events.
7. Whether packet and approval identifiers must be required for all orchestration events or nullable where not applicable.
8. Which mission-control exports are allowed to emit evidence without changing runtime state.
