# Runtime Proof Gate Preview

- validation_status: `PASS`
- final_verdict: `BLOCKED`
- human_gate_ready: `False`
- blocker_count: `12`
- attention_count: `1`
- safe_next_action: `Fix the blockers before the proof chain can reach human gate review.`
- stop_condition: `Stop until blockers are cleared; no execution.`

## Cross-proof consistency
{
  "attention_reasons": [
    "reduction target selector still points to a proof-planning target"
  ],
  "blockers": [
    "relay review is BLOCKED",
    "operator dependency ledger validation is BLOCKED",
    "runtime queue still lists remaining blockers"
  ],
  "contradictions": [],
  "invalid_reasons": [],
  "operator_dependency_status": "BLOCKED",
  "reduction_target_status": "UNKNOWN",
  "relay_review_status": "BLOCKED",
  "restart_timeouts_status": "PASS",
  "retention_rotation_status": "PASS",
  "runtime_queue_status": "UNKNOWN",
  "soak_status": "PASS"
}

## Validation
{
  "blockers": [],
  "checked_fields": [
    "schema",
    "generated_at_utc",
    "mode",
    "gate_type",
    "gate_version",
    "final_verdict",
    "final_verdict_reason",
    "human_gate_required",
    "human_gate_ready",
    "execution_allowed",
    "dispatch_allowed",
    "apply_allowed",
    "runtime_launch_allowed",
    "runtime_mutation_allowed",
    "telemetry_mutation_allowed",
    "scheduler_creation_allowed",
    "service_creation_allowed",
    "sos_allowed",
    "live_trading_allowed",
    "credentials_accessed",
    "approval_granted",
    "vacation_mode_complete",
    "unsafe_autonomy_claim",
    "prerequisite_inputs_present",
    "prerequisite_inputs_missing",
    "prerequisite_statuses",
    "accepted_prerequisites",
    "rejected_prerequisites",
    "attention_reasons",
    "blockers",
    "invalid_reasons",
    "unsafe_flags_detected",
    "forbidden_claims_detected",
    "cross_proof_consistency",
    "proof_chain_summary",
    "operator_dependency_summary",
    "reduction_target_summary",
    "runtime_queue_summary",
    "relay_summary",
    "restart_timeouts_summary",
    "retention_rotation_summary",
    "soak_summary",
    "gate_policy",
    "safe_next_action",
    "stop_condition"
  ],
  "final_verdict": "BLOCKED",
  "forbidden_claims": [],
  "status": "PASS",
  "unsafe_flags": []
}