# AIOS Forex Dashboard Source-of-Truth Projection Map V1

## 1. Status
`PARTIAL`

## 2. Existing dashboard/source-of-truth artifacts
- `docs/dashboard/AIOS_MINIMAL_OPERATOR_DASHBOARD_CONTRACT_V1.md`
- `docs/dashboard/AIOS_DASHBOARD_READ_ONLY_LIVE_DATA_BRIDGE_V1.md`
- `docs/dashboard/AIOS_DASHBOARD_PAPER_SIGNAL_EXECUTION_LOOP_V1.md`
- `docs/governance/source-of-truth-map.md`
- `Reports/aios_control_plane/AIOS_CONTROL_PLANE_STATUS_latest.json`
- `Reports/runtime_queue/runtime_execution_queue_view.json`

These artifacts already describe read-only projection behavior, blocked authority boundaries, and current-truth labeling. They do not yet provide a canonical Forex Proof Lane state model.

## 3. Required Proof Lane state fields
- `campaign_id`
- `branch`
- `base_head`
- `proof_lane_status`
- `owner_approval_status`
- `broker_boundary_status`
- `receipt_evidence_status`
- `repeatability_ledger_status`
- `validation_status`
- `claim_status`
- `next_safe_action`
- `source_of_truth_version`

## 4. State transitions
`DESIGN_ONLY -> READ_ONLY_RECON -> GAP_MAP_COMPLETE -> SCHEMA_PACKET_READY -> DRY_RUN_VALIDATED -> OWNER_REVIEW_REQUIRED -> FUTURE_DEMO_READY`

The map should only advance when a validator or reviewed artifact produces the next state. The dashboard must not invent a skipped state.

## 5. Blocked claim indicators
- `live_trading_allowed = false`
- `broker_allowed = false`
- `profit_claim_allowed = false`
- `credential_present = false`
- `execution_authority = false`
- `owner_approval_missing = true`

## 6. Owner approval status fields
- `approval_required`
- `approval_id`
- `approval_scope`
- `approval_window_utc`
- `approver_identity`
- `approval_status`

## 7. Demo/live boundary flags
- `paper_only`
- `demo_proof_pending`
- `demo_proof_ready`
- `live_blocked`
- `live_exception_required`
- `live_micro_exception_inactive`

## 8. Receipt/evidence summary fields
- `receipt_count`
- `sanitized_receipt_count`
- `raw_payload_present`
- `raw_payload_hash_present`
- `redaction_status`
- `demo_receipt_link_count`
- `live_receipt_link_count`

## 9. Repeatability ledger summary fields
- `run_count`
- `first_run_id`
- `last_run_id`
- `config_hash`
- `strategy_version`
- `sample_count`
- `drawdown_max_pct`
- `post_trade_review_state`

## 10. Safe projection rules
- Use source-backed values only.
- Show `UNKNOWN`, `STALE`, `MISMATCH`, or `BLOCKED` when evidence is incomplete.
- Never turn a projection into approval authority.
- Never infer live readiness from paper-only metrics.
- Keep ledger evidence labeled as current, stale, historical, or reference when the source-of-truth map says so.
