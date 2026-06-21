# AIOS FOREX INTENT-TO-ATTEMPT EVIDENCE SCHEMA PLAN V1

This plan proposes markdown-only evidence schema structures; no executable schema files are added in this phase.

## 1) Intent Record

`AIOS_FOREX_INTENT_RECORD_V1`

- `timestamp`
- `correlation_id`
- `strategy_id`
- `candidate_id`
- `governance_status`
- `risk_summary`
- `approval_status`
- `endpoint_mode`
- `kill_switch_state`
- `evidence_references` (list)
- `replay_references` (list)

## 2) Review Record

`AIOS_FOREX_REVIEW_RECORD_V1`

- `timestamp`
- `correlation_id`
- `strategy_id`
- `candidate_id`
- `governance_status`
- `risk_summary`
- `approval_status`
- `endpoint_mode`
- `kill_switch_state`
- `evidence_references` (list)
- `replay_references` (list)
- `review_findings`
- `review_outcome`
- `reviewer`

## 3) Approval Record

`AIOS_FOREX_APPROVAL_RECORD_V1`

- `timestamp`
- `correlation_id`
- `strategy_id`
- `candidate_id`
- `governance_status`
- `risk_summary`
- `approval_status`
- `endpoint_mode`
- `kill_switch_state`
- `evidence_references` (list)
- `replay_references` (list)
- `approval_scope`
- `approval_window_expires_at`
- `operator_id`
- `manual_arming_required`
- `timeout_seconds`

## 4) Readiness Record

`AIOS_FOREX_READINESS_RECORD_V1`

- `timestamp`
- `correlation_id`
- `strategy_id`
- `candidate_id`
- `governance_status`
- `risk_summary`
- `approval_status`
- `endpoint_mode`
- `kill_switch_state`
- `evidence_references` (list)
- `replay_references` (list)
- `readiness_gates` (list)
- `freshness_ok`
- `replay_proof_ok`
- `rollback_proof_ok`
- `kill_switch_proof_ok`
- `reconciliation_proof_ok`
- `final_disarm_proof_ok`

## 5) Blocked Attempt Record

`AIOS_FOREX_BLOCKED_ATTEMPT_RECORD_V1`

- `timestamp`
- `correlation_id`
- `strategy_id`
- `candidate_id`
- `governance_status`
- `risk_summary`
- `approval_status`
- `endpoint_mode`
- `kill_switch_state`
- `evidence_references` (list)
- `replay_references` (list)
- `blockers`
- `blocker_reason`
- `halt_type`

## 6) Rejected Attempt Record

`AIOS_FOREX_REJECTED_ATTEMPT_RECORD_V1`

- `timestamp`
- `correlation_id`
- `strategy_id`
- `candidate_id`
- `governance_status`
- `risk_summary`
- `approval_status`
- `endpoint_mode`
- `kill_switch_state`
- `evidence_references` (list)
- `replay_references` (list)
- `rejection_reason`
- `rejection_code`
- `upstream_status_ref`

## 7) Future Execution Attempt Record

`AIOS_FOREX_EXECUTION_ATTEMPT_RECORD_V1` (future phase)

- `timestamp`
- `correlation_id`
- `strategy_id`
- `candidate_id`
- `governance_status`
- `risk_summary`
- `approval_status`
- `endpoint_mode`
- `kill_switch_state`
- `evidence_references` (list)
- `replay_references` (list)
- `attempt_outcome`
- `attempt_status`
- `next_safe_action`
- `final_disarm_required`
- `terminal_disposition`

## Common Field Constraints

- All `timestamp` values are UTC ISO-8601.
- `correlation_id` must be stable across intent-review-approval-readiness-attempt flow.
- `evidence_references` and `replay_references` must be immutable pointers (hash/path/classification).
- Schemas must be versioned with suffix `_V1`.
- All records in this packet path enforce `execution_authority_granted=false`.
