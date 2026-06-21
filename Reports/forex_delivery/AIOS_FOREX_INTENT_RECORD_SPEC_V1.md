# AIOS FOREX INTENT RECORD SPEC V1

## Purpose

Define the canonical intent record required before any future broker-demo execution attempt path.

## Record Identity

- `record_type`: `AIOS_FOREX_INTENT_RECORD_V1`
- `record_id`: deterministic or stable unique identifier
- `correlation_id`: required, stable across intent → review → approval → readiness → attempt chain.

## Required Fields

- `timestamp` (UTC ISO-8601)
- `correlation_id` (stable string)
- `strategy_id`
- `candidate_id`
- `risk_summary` (structured object)
- `governance_status`
- `approval_status`
- `endpoint_mode` (`demo` only in future)
- `kill_switch_state`
- `evidence_references` (list)
- `replay_references` (list)

## Optional Fields

- `intent_notes`
- `operator_context`
- `risk_limits_snapshot`
- `symbol`
- `requested_units`
- `confidence`
- `stop_loss`
- `take_profit`
- `entry_reference`
- `upstream_trace_refs`

## Validation Rules

- `timestamp` must parse as UTC time.
- `correlation_id` must be non-empty and reused by review/approval/readiness records.
- `strategy_id` and `candidate_id` must be non-empty.
- `governance_status` must be one of approved/review states only.
- `approval_status` must not be `execution_authorized`.
- `endpoint_mode` may only be explicit `DEMO` in this phase.
- `kill_switch_state` must indicate required kill switch coverage.
- `evidence_references` and `replay_references` must be immutable references (hash/path/classification), never inline payload dumps.
- `execution_authority_granted` must be false.

## Correlation Identifiers

- `correlation_id` links:
  - `review_record_id`
  - `approval_record_id`
  - `readiness_record_id`
  - `blocked/rejected/execution attempt record ids`
- `record_id` must be deterministic for same intent payload in test fixtures.

## Governance Requirements

- No credentials allowed in intent content.
- No account identifiers allowed in intent content.
- No network endpoint values.
- No broker order identifiers.
- No live execution flags.
- Must include immutable auditable trace refs and evidence references.

## Replay Requirements

- Every intent record stores at least one replay anchor in `replay_references` when available.
- Replay references must be immutable and ordered.
- Replay replayability requirement: reconstructable evidence path without live broker state.
- Any missing or stale reference is a blocker and transitions intent to `reviewed` only after repair.
