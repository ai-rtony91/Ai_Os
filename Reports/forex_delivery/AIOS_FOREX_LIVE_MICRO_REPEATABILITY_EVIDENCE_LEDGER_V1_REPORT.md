# AIOS Forex Live Micro Repeatability Evidence Ledger V1

## Purpose
Local-only repeatability evidence ledger that compares redacted read-only snapshots. This packet does not place trades and does not send orders.

## Input
- evidence_state_paths: ['Reports\\forex_delivery\\AIOS_FOREX_LIVE_MICRO_EVIDENCE_REVIEW_V1_STATE.json']
- evidence_files_found: ['Reports\\forex_delivery\\AIOS_FOREX_LIVE_MICRO_EVIDENCE_REVIEW_V1_STATE.json']
- evidence_files_missing: []
- local_only: True
- broker_api_called: False
- bitwarden_called: False
- order_endpoint_called: False
- post_request_called: False
- trade_close_called: False
- position_close_called: False
- live_order_execution: False
- demo_order_execution: None
- money_movement: False
- scheduler_started: False
- daemon_started: False
- webhook_started: False

## Result
- repeatability_status: LIVE_MICRO_REPEATABILITY_OPEN_TRADE_STILL_NEGATIVE
- current_stage: live_micro_repeatability_evidence_ledger
- next_stage: owner_supervised_repeatability_decision
- safe_next_action: Capture a later snapshot to confirm whether P/L recovers or degrades.

## Blockers
- none

## Runtime summary
- snapshot_count: 1
- open_trade_seen_count: 1
- closed_or_not_visible_count: 0
- profit_positive_count: 0
- profit_flat_count: 0
- profit_negative_count: 1
- pnl_values: [-0.0002]
- latest_pnl_value: -0.0002
- latest_pnl_classification: negative
- sltp_complete_count: 1
- sltp_missing_count: 0
- sltp_latest_complete: True
- risk_controls_consistent: True
- forbidden_action_flags_clear: True
- live_execution_flags_clear: True
- money_movement_clear: True
- readiness_for_next_supervised_decision: True
- evidence_fingerprints: ['sha256:8bd8e2890e6d64b5dcc011439928e5e3560a4b5cdd7eacec2e12d0c7c9b94f31']

## Classification taxonomy
- LIVE_MICRO_REPEATABILITY_LEDGER_READY
- LIVE_MICRO_REPEATABILITY_INSUFFICIENT_SNAPSHOTS
- LIVE_MICRO_REPEATABILITY_OPEN_TRADE_STILL_NEGATIVE
- LIVE_MICRO_REPEATABILITY_OPEN_TRADE_FLAT
- LIVE_MICRO_REPEATABILITY_OPEN_TRADE_POSITIVE
- LIVE_MICRO_REPEATABILITY_SLTP_EVIDENCE_MISSING
- LIVE_MICRO_REPEATABILITY_FORBIDDEN_FLAG_DETECTED
- LIVE_MICRO_REPEATABILITY_MONEY_MOVEMENT_FLAG_DETECTED
- LIVE_MICRO_REPEATABILITY_REPAIR_REQUIRED

## Safety invariants
- No broker API calls.
- No Bitwarden reads.
- No order POSTs or /orders endpoint use.
- No trade/position close calls.
- No money movement or live scheduler/daemon/webhook actions.

## Validation
- python -m py_compile scripts/forex_delivery/run_forex_live_micro_repeatability_evidence_ledger_v1.py
- python -m pytest tests/forex_engine/test_forex_live_micro_repeatability_evidence_ledger_v1.py -q
- python scripts/forex_delivery/run_forex_live_micro_repeatability_evidence_ledger_v1.py
- repeatability_status: LIVE_MICRO_REPEATABILITY_OPEN_TRADE_STILL_NEGATIVE
- safe_next_action: continue only if repeatability status supports supervised progression.
