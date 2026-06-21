# AIOS Live-Candidate Readiness Spine V1

## Objective
Produce a deterministic, paper/demo-only readiness artifact that classifies a portfolio as a live-candidate review item after the completed demo governance chain.

## Scope
- `automation/forex_engine/live_candidate_readiness_spine.py`
- `tests/forex_engine/test_live_candidate_readiness_spine.py`

## Required Output
The spine returns:
- `readiness_completed`
- `live_candidate_review_ready`
- `live_candidate_status`
- `demo_validation_passed`
- `demo_phase_status`
- `performance_state`
- `risk_status`
- `operator_decision`
- `stable_winner`
- `readiness_reasons`
- `blocked_reasons`
- `next_safe_action`
- `operator_approval_required`
- `safety`

## Deterministic Rules
- Builds upon `run_demo_validation_result_aggregator`, `run_demo_phase_operator_review_packet`, and `run_demo_phase_risk_escalation_engine` outputs.
- Enforces paper/demo safety boundary:
  - paper-only and demo-review mode only
  - no broker, credential, network, demo execution, live trading authorization, order execution, or capital allocation changes
- Requires:
  - demo validation passed
  - stable winner present
  - acceptable demo phase status
  - performance state IMPROVING or STABLE
  - no risk violation and no suspension escalation
  - operator decision `APPROVE_CONTINUE_DEMO_PHASE`
  - no unsafe evidence reasons
- Emits:
  - `LIVE_CANDIDATE_REVIEW_READY` when all checks pass
  - `LIVE_CANDIDATE_MORE_DEMO_EVIDENCE_REQUIRED` for incomplete demo phase readiness
  - `LIVE_CANDIDATE_REJECTED` for hard blockers (missing stable winner, demo validation failure)
  - `LIVE_CANDIDATE_BLOCKED` for risk/degradation/unsafe/operator-not-approved conditions
- Includes explicit blocked codes:
  - `missing_stable_winner`
  - `demo_validation_not_passed`
  - `demo_phase_not_validated`
  - `performance_degrading`
  - `risk_violation_present`
  - `operator_review_missing`
  - `operator_review_not_approved`
  - `unsafe_evidence`
  - `live_execution_forbidden`
  - `broker_access_forbidden`
  - `credential_access_forbidden`

## Validator Chain
- `python -m pytest tests/forex_engine/test_live_candidate_readiness_spine.py -q`
- `python -m py_compile automation/forex_engine/live_candidate_readiness_spine.py tests/forex_engine/test_live_candidate_readiness_spine.py`
