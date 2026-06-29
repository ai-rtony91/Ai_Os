# AIOS Forex 110 C2 Walk-Forward OOS Evidence Generation V1

Packet ID: `PKT-FOREX-110-C2-WALKFORWARD-OOS-EVIDENCE-GENERATION-V1`
C2 evidence status: `PROVEN`
Target candidate id: `c2-eur-buy-stronger-review-ready`
Top candidate id: `c2-eur-buy-stronger-review-ready`
Candidate alignment: `ALIGNED`
Evidence source classification: `REAL_LOCAL_DETERMINISTIC`

## Required Proof Fields
- proof_candidate: `c2-eur-buy-stronger-review-ready`
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
- candidate_alignment: `ALIGNED`

## Blockers
- none

## Source Classification
- Real C2 walk-forward/OOS proof was not created unless complete sanitized local evidence was already present.
- Sample/test-style C2 references were not promoted into proof.
- No broker, credential, demo, live, scheduler, commit, push, PR, or merge action was performed.

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
- test_file: tests/forex_engine/test_forex_110_c2_walkforward_oos_evidence_generation_v1.py
- runner_script: scripts/forex_delivery/run_forex_110_c2_walkforward_oos_evidence_generation_v1.py
- missing_evidence_field: NONE
- unlock_status_required: PROVEN
- next_packet_name: NONE
- owner_action_required: NONE
- stop_condition: NONE
- no_bloat_guard: Reuse existing walk-forward intake and do not promote sample/test C2 data into proof.

## Next Safe Action
Rerun the Forex 110 walk-forward/OOS sufficiency truth lock. No trading authority is created.
