# AIOS Forex 110 C2 Walk-Forward OOS Source Collection V1

Packet ID: `PKT-FOREX-110-C2-WALKFORWARD-OOS-SOURCE-COLLECTION-V1`
Source collection status: `PROVEN_REAL_SANITIZED_LOCAL_C2_SOURCE`
Evidence source classification: `REAL_SANITIZED_LOCAL_SOURCE_FOUND`
Target candidate: `c2-eur-buy-stronger-review-ready`
Top candidate: `c2-eur-buy-stronger-review-ready`
C2 source found: `true`
C2 source generated: `false`
Source path: `Reports/forex_delivery/AIOS_FOREX_110_C2_REAL_WALKFORWARD_OOS_HARNESS_V1_REPORT.md`
Source is test or sample: `false`
Source is real sanitized local: `true`
Candidate alignment: `ALIGNED`

## Required Source Fields
- candidate: `MISSING`
- windows_total: `6.0`
- windows_passed: `6.0`
- oos_segments_total: `4.0`
- oos_segments_passed: `4.0`
- min_pass_rate: `0.75`
- max_drawdown: `0.22`
- max_allowed_drawdown: `0.5`
- sanitized: `True`
- evidence_age_days: `1.0`
- max_evidence_age_days: `7.0`

## Walk-Forward/OOS After Rerun
- walkforward_oos_status_after_rerun: `PROVEN`
- profit_persistence_unlocked: `true`

## Blockers
- none

## Candidate Sources Inspected
- automation/forex_engine/forex_110_c2_walkforward_oos_evidence_generation_v1.py
- automation/forex_engine/profit_proof_ledger_v1.py
- automation/forex_engine/review_ready_candidate_selector_v1.py
- tests/forex_engine/test_forex_110_c2_walkforward_oos_source_collection_v1.py
- tests/forex_engine/test_forex_110_walkforward_oos_sufficiency_truth_lock_v1.py
- tests/forex_engine/test_profit_proof_ledger_v1.py
- tests/forex_engine/test_review_ready_candidate_selector_v1.py
- Reports/forex_delivery/AIOS_FOREX_110_C2_REAL_WALKFORWARD_OOS_HARNESS_V1_REPORT.md
- Reports/forex_delivery/AIOS_FOREX_110_C2_REAL_WALKFORWARD_OOS_HARNESS_V1_SOURCE.md
- Reports/forex_delivery/AIOS_FOREX_110_C2_REAL_WALKFORWARD_OOS_HARNESS_V1_STATE.json
- Reports/forex_delivery/AIOS_FOREX_110_C2_WALKFORWARD_OOS_EVIDENCE_GENERATION_V1_REPORT.md
- Reports/forex_delivery/AIOS_FOREX_110_C2_WALKFORWARD_OOS_EVIDENCE_GENERATION_V1_STATE.json
- Reports/forex_delivery/AIOS_FOREX_110_C2_WALKFORWARD_OOS_SOURCE_V1.md
- Reports/forex_delivery/AIOS_FOREX_110_PROFIT_EVIDENCE_TRUTH_LOCK_V1_REPORT.md
- Reports/forex_delivery/AIOS_FOREX_110_PROFIT_EVIDENCE_TRUTH_LOCK_V1_STATE.json
- Reports/forex_delivery/AIOS_FOREX_110_TOP_CANDIDATE_WALKFORWARD_OOS_EVIDENCE_COLLECTION_V1_REPORT.md
- Reports/forex_delivery/AIOS_FOREX_110_TOP_CANDIDATE_WALKFORWARD_OOS_EVIDENCE_COLLECTION_V1_STATE.json
- Reports/forex_delivery/AIOS_FOREX_110_WALKFORWARD_OOS_SUFFICIENCY_TRUTH_LOCK_V1_REPORT.md
- Reports/forex_delivery/AIOS_FOREX_110_WALKFORWARD_OOS_SUFFICIENCY_TRUTH_LOCK_V1_STATE.json
- Reports/forex_delivery/AIOS_FOREX_PROFIT_PROOF_LEDGER_V1.md
- Reports/forex_delivery/AIOS_FOREX_PROFIT_PROOF_LEDGER_V1_REPORT.md

## Sample Or Test References
- automation/forex_engine/forex_110_c2_walkforward_oos_evidence_generation_v1.py
- automation/forex_engine/profit_proof_ledger_v1.py
- automation/forex_engine/review_ready_candidate_selector_v1.py
- tests/forex_engine/test_forex_110_c2_walkforward_oos_source_collection_v1.py
- tests/forex_engine/test_forex_110_walkforward_oos_sufficiency_truth_lock_v1.py
- tests/forex_engine/test_profit_proof_ledger_v1.py
- tests/forex_engine/test_review_ready_candidate_selector_v1.py
- Reports/forex_delivery/AIOS_FOREX_110_C2_REAL_WALKFORWARD_OOS_HARNESS_V1_STATE.json
- Reports/forex_delivery/AIOS_FOREX_110_C2_WALKFORWARD_OOS_EVIDENCE_GENERATION_V1_STATE.json
- Reports/forex_delivery/AIOS_FOREX_110_PROFIT_EVIDENCE_TRUTH_LOCK_V1_STATE.json
- Reports/forex_delivery/AIOS_FOREX_110_WALKFORWARD_OOS_SUFFICIENCY_TRUTH_LOCK_V1_STATE.json
- Reports/forex_delivery/AIOS_FOREX_PROFIT_PROOF_LEDGER_V1_REPORT.md

## Permission Locks
- next_demo_trade_allowed: `false`
- broker_action_allowed: `false`
- real_money_allowed: `false`
- compounding_allowed: `false`
- bank_movement_allowed: `false`
- live_trading_allowed: `false`
- credential_access_allowed: `false`
- order_submission_allowed: `false`
- owner_approval_created: `false`

## ATTACK_TO_FINISH
- blocker_id: NO_BLOCKER
- blocker_status: PROVEN
- exact_blocker: NONE
- canonical_owner_file: automation/forex_engine/walk_forward_evidence_intake_v1.py
- test_file: tests/forex_engine/test_forex_110_c2_walkforward_oos_source_collection_v1.py
- runner_script: scripts/forex_delivery/run_forex_110_c2_walkforward_oos_source_collection_v1.py
- missing_evidence_field: NONE
- unlock_status_required: PROVEN
- next_packet_name: NONE
- owner_action_required: NONE
- stop_condition: NONE
- no_bloat_guard: Create the C2 source report only from real sanitized local evidence.

## Next Safe Action
Rerun the walk-forward/OOS sufficiency truth lock and review the generated C2 source report. Do not trade.
