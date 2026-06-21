# AIOS FOREX ATTEMPT RECORD SPEC V1

## Purpose

Define all attempt-oriented evidence record families required for safe transition through block/reject/execute consideration phases.

## Shared Attempt Family Pattern

All records use one shared header:

- `record_type`
- `record_id`
- `timestamp`
- `correlation_id`
- `strategy_id`
- `candidate_id`
- `governance_status`
- `risk_summary`
- `approval_status`
- `endpoint_mode`
- `kill_switch_state`
- `evidence_references`
- `replay_references`
- `execution_authority_granted` (must be false in pre-live phase)
- `operator_restriction_ok` (must be true)

## Required Fields by Record

### Blocked Attempt Record (`AIOS_FOREX_BLOCKED_ATTEMPT_RECORD_V1`)
- `blockers` (list)
- `blocker_reason`
- `halt_type`
- `replay_summary_ref`

### Rejected Attempt Record (`AIOS_FOREX_REJECTED_ATTEMPT_RECORD_V1`)
- `rejection_reason`
- `rejection_code`
- `upstream_status_ref`
- `reapproval_path`

### Execution Attempt Record (`AIOS_FOREX_EXECUTION_ATTEMPT_RECORD_V1`)
- `attempt_outcome`
- `attempt_status`
- `next_safe_action`
- `final_disarm_required`
- `terminal_disposition`
- `attempt_error_codes` (if any)

## Validation Rules

- `timestamp` required and monotonic within a correlation chain.
- `attempt_outcome` must be one of:
  - `DENIED`
  - `BLOCKED`
  - `DEFERRED`
  - `REJECTED`
  - `FORWARDED_FOR_APPROVAL`
- `endpoint_mode` must match approved mode used by chain.
- `kill_switch_state` must be captured at block/reject/review moment.
- `execution_authority_granted` must remain false.
- Attempts cannot include broker IDs, account IDs, credentials, network endpoints, or order execution artifacts.

## Blocked Attempt Semantics

- `blocked` indicates a governance barrier.
- `halt_type` must be one of:
  - `CREDENTIAL_BOUNDARY`
  - `ACCOUNT_BOUNDARY`
- `ENDPOINT_MODE_VIOLATION`
  - `KILL_SWITCH_ACTIVE`
  - `HARD_GATE_FAIL`
  - `REPLAY_MISSING`

## Rejected Attempt Semantics

- `rejection_code` must include reason taxonomy for audit.
- `upstream_status_ref` must reference the blocking evaluator status record.
- Rejection records are immutable and must be replay-safe.

## Future Execution Attempt Semantics

- `attempt_status` must remain `NOT_EXECUTED` in current phase.
- `terminal_disposition` must be explicit (`BLOCKED`, `DEFERRED`, `REJECTED`).
- `final_disarm_required` must be true.

## Replay and Evidence

- All attempt records must reference evidence and replay refs, including:
  - intent proof
  - review proof
  - approval proof
  - readiness proof
- Replay of an attempt record must reproduce the exact reason/halt path without external state.
