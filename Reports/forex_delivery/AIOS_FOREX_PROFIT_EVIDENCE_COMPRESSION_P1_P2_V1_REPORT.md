# AIOS Forex Profit Evidence Compression P1/P2 V1 Report

## Campaign Scope

This report compresses Forex P1 Strategy Profit Evidence and P2 Candidate Scoring And Elimination only.

It reviews repo-local evidence, selects the strongest current profit candidate if evidence supports one, classifies rejected or blocked candidates, and identifies the missing evidence before walk-forward/OOS proof.

## Source Evidence

Primary authority and boundary files reviewed:

- `AGENTS.md`
- `README.md`
- `WHITEPAPER.md`
- `RISK_POLICY.md`
- `Reports/forex_delivery/AIOS_FOREX_PROFIT_TRACK_HANDOFF_V1.md`
- `Reports/forex_delivery/AIOS_FOREX_JUNE30_SLICE7_FINAL_OWNER_DECISION_BRIEF_V1.json`
- `Reports/forex_delivery/AIOS_FOREX_JUNE30_SLICE7_FINAL_OWNER_DECISION_BRIEF_V1_REPORT.md`
- `Reports/forex_delivery/AIOS_FOREX_JUNE30_FINAL_SLICE_CLOSURE_LEDGER_V1.md`
- `Reports/forex_delivery/AIOS_FOREX_FINAL_KNOWN_COUNTS_CAMPAIGN_V1_REPORT.md`
- `Reports/forex_delivery/AIOS_FOREX_FINAL_BOUNDARY_CLOSURE_CAMPAIGN_V1_REPORT.md`

Primary profit and candidate evidence reviewed:

- `Reports/forex_delivery/AIOS_FOREX_CANDIDATE_LEADERBOARD_V1.md`
- `Reports/forex_delivery/AIOS_FOREX_TOP_10_PROFIT_CANDIDATES_V1.md`
- `Reports/forex_delivery/AIOS_FOREX_BEST_PROFIT_CANDIDATE_V1.md`
- `Reports/forex_delivery/AIOS_FOREX_PROFITABILITY_VERDICT_V1.md`
- `Reports/forex_delivery/AIOS_FOREX_C1_EUR_BUY_EVIDENCE_DEPTH_SCOREBOARD_V1.md`
- `Reports/forex_delivery/AIOS_FOREX_C1_EUR_BUY_WALK_FORWARD_STABILITY_SCOREBOARD_V1.md`
- `Reports/forex_delivery/AIOS_FOREX_WALK_FORWARD_DEPTH_PACKET_R_V1_REPORT.md`
- `Reports/forex_delivery/AIOS_FOREX_WALK_FORWARD_WINDOW_MATRIX_V1.md`
- `Reports/forex_delivery/AIOS_FOREX_WALK_FORWARD_FAILURE_ROOT_CAUSE_MATRIX_V1.md`
- `Reports/forex_delivery/AIOS_FOREX_BEFORE_AFTER_WALK_FORWARD_COMPARISON_V1.md`
- `Reports/forex_delivery/AIOS_FOREX_WALKFORWARD_ROOT_CAUSE_DRYRUN_V2.md`
- `Reports/forex_delivery/readiness_state_recalculation_v1_report.json`
- `Reports/forex_delivery/review_chain_end_to_end_candidate_journey.json`
- `Reports/forex_delivery/proof_bundle_to_candidate_bridge_report.json`
- `automation/forex_engine/next_candidate_discovery_u_v1.py`
- `automation/forex_engine/candidate_scoring_v1.py`

## Discovery Results

Candidate inventory found 12 real candidate IDs:

- `c1-eur-buy`
- `c5-gbp-buy`
- `c2-usd-buy`
- `c3-eur-sell`
- `c4-jpy-buy`
- `c3-nzd-buy`
- `c1-gbp-sell`
- `c1-aud-buy`
- `c2-eur-sell`
- `c2-cad-buy`
- `c3-chf-sell`
- `c3-eur-dup`

The strongest current P1 candidate is `c1-eur-buy`. The strongest runner-up is `c5-gbp-buy`.

The repo also contains source conflicts for `c1-eur-buy`: some bridge and recalculation artifacts report demo-review-ready candidate metrics, while C1-specific walk-forward, failure-regime, and root-cause artifacts report failed windows, a rejected mitigation path, or unresolved blockers. These conflicts block a P3-ready decision.

## Candidate Scoreboard

| rank | candidate | score | status | reason |
|---:|---|---:|---|---|
| 1 | `c1-eur-buy` | 85 | NEEDS_MORE_EVIDENCE | Strong P1 anchor metrics, but walk-forward/OOS proof fails and readiness artifacts conflict. |
| 2 | `c5-gbp-buy` | 70 | NEEDS_MORE_EVIDENCE | Positive paper metrics, but sample is 15 and walk-forward/OOS proof is missing. |
| 3 | `c2-usd-buy` | 70 | NEEDS_MORE_EVIDENCE | Positive paper metrics, but sample sufficiency is not settled and walk-forward/OOS proof is missing. |
| 4 | `c3-eur-sell` | 70 | NEEDS_MORE_EVIDENCE | Positive paper metrics, but sample is 16 and walk-forward/OOS proof is missing. |
| 5 | `c3-nzd-buy` | 70 | REJECTED_INSUFFICIENT_SAMPLE | Strong one-shot paper metrics, but current reports reject it for insufficient sample. |
| 6 | `c4-jpy-buy` | 40 | REJECTED_NEGATIVE_EXPECTANCY | Candidate leaderboard reports negative expectancy. |
| 7 | `c1-gbp-sell` | 25 | REJECTED_LOW_PROFIT_FACTOR | Non-productive profit-factor geometry and sample deficit. |
| 8 | `c1-aud-buy` | 25 | REJECTED_LOW_PROFIT_FACTOR | Non-positive expectancy, low profit factor, and sample deficit. |
| 9 | `c2-eur-sell` | 25 | REJECTED_LOW_PROFIT_FACTOR | Non-productive profit-factor geometry and sample deficit. |
| 10 | `c2-cad-buy` | 25 | REJECTED_LOW_PROFIT_FACTOR | Non-positive expectancy, low profit factor, and sample deficit. |
| 11 | `c3-chf-sell` | 25 | REJECTED_LOW_PROFIT_FACTOR | Non-productive profit-factor geometry and sample deficit. |
| 12 | `c3-eur-dup` | 25 | REJECTED_LOW_PROFIT_FACTOR | Non-positive expectancy, low profit factor, and sample deficit. |

## Best Candidate

Best current candidate: `c1-eur-buy`.

Evidence strength:

- Strategy: `paper_long_run_supervisor_v2`.
- Direction: LONG.
- P1 anchor evidence reports expectancy `200.00`, profit factor `999.00`, win rate `1.00`, max drawdown `0.00`, sample size `30`, and paper-only safety.
- C1 walk-forward evidence reports 4 windows, 1 passing window, 3 failing windows, stable expectancy `-325.45`, controlled drawdown `75.20`, and blockers `negative_expectancy_window`, `low_profit_factor_window`, and `excessive_drawdown_window`.

Decision: `c1-eur-buy` is the best current candidate for evidence-gap closure, not a P3-ready candidate.

## Evidence Gaps

- Resolve conflicting `c1-eur-buy` readiness reports before any stronger readiness claim.
- Repair or replace the mitigation path that leaves `walk_forward_gate_cleared: False`.
- Produce stable walk-forward/OOS evidence with source-backed passing windows.
- Close `drawdown_containment` and `insufficient_sample` blockers.
- Expand runner-up candidate samples and run candidate-specific walk-forward/OOS proof.
- Re-run candidate scoring after source conflicts and walk-forward/OOS gaps are closed.

## P3 Readiness Decision

P3 cannot start immediately as a proof-complete lane.

Campaign status: `MORE_EVIDENCE_REQUIRED`.

Reason: no candidate has non-conflicting source-backed evidence across expectancy, profit factor, win/loss, drawdown, sample depth, and passing walk-forward/OOS proof.

## What This Completes

- P1/P2 profit evidence compression is complete.
- Candidate inventory is established.
- `c1-eur-buy` is selected as the best current candidate for evidence-gap closure.
- Rejected and blocked candidates are classified.
- The next evidence gaps are isolated.

## What This Does Not Approve

- no live trading approved
- no broker/API approved
- no credentials approved
- no account access approved
- no order action approved
- no money movement approved
- no production/autonomy approved
- 100-120 percent return remains a target, not verified
- vacation/luxury mode remains a vision, not active operating status
- 22/6 remains a target, not approved autonomy

## Next Required Lane

`P1_EVIDENCE_GAP_CLOSURE`

The next lane should resolve the `c1-eur-buy` readiness conflict and repair the walk-forward/OOS evidence gap before any P3 walk-forward/OOS proof decision.

## Final Owner Sentence

AIOS Forex profit track P1/P2 is complete: no P3-ready profit candidate is proven yet, and the next required work is evidence-gap closure before walk-forward/OOS proof; live trading, broker/API, credentials, money movement, 22/6 autonomy, vacation/luxury mode, and 100-120 percent return claims remain blocked until separately proven and approved.
