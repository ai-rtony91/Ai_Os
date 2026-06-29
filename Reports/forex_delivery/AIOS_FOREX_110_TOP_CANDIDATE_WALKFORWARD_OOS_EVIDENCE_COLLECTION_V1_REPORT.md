# AIOS Forex 110 Top Candidate Walk-Forward/OOS Evidence Collection V1

Packet ID: `PKT-FOREX-110-TOP-CANDIDATE-WALKFORWARD-OOS-EVIDENCE-COLLECTION-V1`
Mode: `LOCAL_APPLY`
Lane: `forex-110-walkforward-oos-evidence-collection`
Worktree: `C:\Dev\Ai.Os`
Branch observed: `main`

## Scope

Collect and classify current local sanitized walk-forward/OOS evidence for the Forex 110 profit-ledger top candidate.

This packet did not trade, contact brokers, read credentials, start runtime services, approve demo/live execution, approve compounding, move money, stage, commit, push, PR, or merge.

## Top Candidate

- top_candidate_id: `c2-eur-buy-stronger-review-ready`
- source: `Reports/forex_delivery/AIOS_FOREX_110_PROFIT_EVIDENCE_TRUTH_LOCK_V1_STATE.json`
- profit truth-lock status: `REVIEW_READY_PERSISTENCE_BLOCKED`
- profit proof status: `BLOCKED`

## Evidence Collection Result

- walk_forward_intake_status: `WALK_FORWARD_OOS_INCOMPLETE`
- walk_forward_oos_status: `BLOCKED_TOP_CANDIDATE_MISMATCH`
- truth_lock_status: `REVIEW_READY_WALKFORWARD_OOS_CANDIDATE_MISMATCH`
- profit_persistence_unlocked: `false`
- top_candidate_alignment: `MISMATCHED`
- walkforward_source_candidate_ids: `c1-eur-buy`

## Missing Evidence

- `oos_segments_total`
- `oos_segments_passed`
- top-candidate aligned walk-forward/OOS source naming `candidate: c2-eur-buy-stronger-review-ready`

## Current Normalized Walk-Forward/OOS Summary

- windows_total: `4.0`
- windows_passed: `1.0`
- min_pass_rate: `1.0`
- max_drawdown: `75.2`
- max_allowed_drawdown: `0.12`
- sanitized: `true`
- evidence_age_days: `0.0`
- max_evidence_age_days: `1.25`

## Evidence Limits

The current repository evidence does not contain real sanitized OOS segment counts for the top candidate. The only `c2-eur-buy-stronger-review-ready` walk-forward/OOS-ready examples found are test/sample data in code, not production evidence. Those values were not promoted into proof.

## Validators Run

- `git status --short --branch` -> `## main...origin/main`
- `python scripts\forex_delivery\run_walk_forward_evidence_intake_v1.py --json` -> completed, status `WALK_FORWARD_OOS_INCOMPLETE`
- `python scripts\forex_delivery\run_forex_110_walkforward_oos_sufficiency_truth_lock_v1.py --write-state --write-report` -> completed, status `BLOCKED_TOP_CANDIDATE_MISMATCH`

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

## Safe Next Action

Provide a sanitized walk-forward/OOS evidence report for `c2-eur-buy-stronger-review-ready` containing `candidate`, `windows_total`, `windows_passed`, `oos_segments_total`, `oos_segments_passed`, `min_pass_rate`, `max_drawdown`, `max_allowed_drawdown`, `sanitized`, `evidence_age_days`, and `max_evidence_age_days`, then rerun:

```powershell
python scripts\forex_delivery\run_forex_110_walkforward_oos_sufficiency_truth_lock_v1.py --write-state --write-report
```

Status: `BLOCKED_MISSING_TOP_CANDIDATE_OOS_EVIDENCE`, no commit, no push.
