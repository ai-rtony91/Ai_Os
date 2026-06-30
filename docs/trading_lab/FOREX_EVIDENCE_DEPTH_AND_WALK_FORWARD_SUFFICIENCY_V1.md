# Forex Evidence Depth And Walk-Forward Sufficiency V1

## Purpose

This packet defines a deterministic read-only evaluator for deciding whether a Forex candidate has enough sanitized paper or simulated evidence to proceed toward the next profit-improvement review lane.

The objective is to maximize validated risk-adjusted opportunity capture while preserving capital and proving edge.

This packet does not promise fixed returns. It does not authorize trading, broker access, bank access, deposits, withdrawals, scheduling, daemon behavior, webhooks, dashboard runtime behavior, or credential use.

## Input Sources

Expected sanitized inputs may include:

- `strategy_evaluation`
- `walk_forward_validation`
- `profitability_evaluation`
- `evidence_promotion_gate`
- `paper_session_samples`
- `paper_session_summary`
- `candidate_quality_snapshot`
- `broker_demo_observability`
- `capital_withdrawal_owner_review_workflow`
- `remaining_work_closure_index`
- `thresholds`
- `as_of_date`
- `owner_name`

Sensitive input keys such as routing numbers, account numbers, card values, passwords, API keys, tokens, secrets, or credentials block the evaluator. The evaluator does not echo sensitive values.

## Threshold Policy

Default thresholds:

- `min_total_trades`: 100
- `min_oos_trades`: 30
- `min_walk_forward_windows`: 3
- `min_profitable_windows`: 2
- `min_regime_count`: 3
- `min_profit_factor`: 1.20
- `min_expectancy`: 0.0
- `max_drawdown_pct`: 0.10
- `min_data_quality_score`: 0.80
- `min_candidate_stability_score`: 0.70

Numeric overrides are accepted only inside conservative guardrails. Rejected overrides are reported as `threshold_override_rejected`.

## Evidence Depth Summary

The evaluator derives total trades, out-of-sample trades, in-sample trades, session count, win count, loss count, breakeven count, and win rate where available.

## Sample Sufficiency

Sample sufficiency requires enough total trades and enough out-of-sample trades. Missing or undersized samples block promotion with `BLOCKED_BY_SAMPLE_SIZE`.

## Walk-Forward Sufficiency

Walk-forward sufficiency checks total windows, profitable or passed windows, failed windows, gate status, out-of-sample pass rate, and stability score. Missing or failed walk-forward evidence blocks promotion with `BLOCKED_BY_WALK_FORWARD`.

## OOS Stability

Out-of-sample stability uses the out-of-sample trade count, stability score, and pass rate. Weak stability blocks promotion with `BLOCKED_BY_OOS_INSTABILITY`.

## Regime Coverage

Regime coverage checks covered regimes such as trend, range, volatile, low-volatility, high-spread, and news-blocked contexts. Insufficient regime diversity blocks promotion with `BLOCKED_BY_REGIME_COVERAGE`.

## Profitability Checks

Profitability checks expectancy and profit factor. Negative expectancy blocks with `BLOCKED_BY_NEGATIVE_EXPECTANCY`. Low profit factor blocks with `BLOCKED_BY_LOW_PROFIT_FACTOR`.

## Drawdown Checks

Drawdown checks maximum drawdown percentage, equity-curve drawdown where available, daily loss stop state, and risk blocks. Excessive drawdown blocks with `BLOCKED_BY_DRAWDOWN`.

## Data Quality Checks

Data quality checks score, missing fields, invalid rows, duplicate trades, malformed timestamps, spread availability, and slippage availability. Weak data quality blocks with `BLOCKED_BY_DATA_QUALITY`.

## Missed-Opportunity Leakage Summary

The evaluator summarizes missed valid setups, false positives, rejected winners, late entries, early exits, and leakage notes. This is opportunity-capture evidence only. It does not execute or recommend orders.

## Promotion Readiness

`SUFFICIENT_FOR_NEXT_PROFIT_LANE` means the candidate may move to owner review for `AIOS_FOREX_PROFIT_CANDIDATE_QUALITY_IMPROVEMENT_V1`.

Demo-candidate review remains owner-gated and execution-disabled. Promotion readiness never authorizes live execution, demo execution, broker API use, credential use, or money movement.

## Blocker Summary

The evaluator separates blockers into:

- sample blockers
- walk-forward blockers
- out-of-sample blockers
- regime blockers
- profitability blockers
- drawdown blockers
- data quality blockers
- leakage blockers
- threshold blockers
- all blockers

## Owner Action Queue

The owner action queue includes:

- `REVIEW_SAMPLE_DEPTH`
- `REVIEW_WALK_FORWARD_WINDOWS`
- `REVIEW_OOS_STABILITY`
- `REVIEW_REGIME_COVERAGE`
- `REVIEW_EXPECTANCY_AND_PROFIT_FACTOR`
- `REVIEW_DRAWDOWN_AND_RISK_LIMITS`
- `REVIEW_DATA_QUALITY`
- `REVIEW_MISSED_OPPORTUNITY_LEAKAGE`
- `REVIEW_NEXT_PROFIT_PACKET`

Every action is owner-review only and has `execution_allowed = False`.

## Safety Boundary

This packet is read-only and manual-review only.

It does not:

- move money
- access bank accounts
- access broker APIs
- execute trades
- request or use credentials
- create a scheduler
- create a daemon
- create a webhook
- create a dashboard runtime or server process

## Next Packet

If evidence is sufficient, the next packet is:

`AIOS_FOREX_PROFIT_CANDIDATE_QUALITY_IMPROVEMENT_V1`

If evidence is insufficient or incomplete, rerun:

`AIOS_FOREX_EVIDENCE_DEPTH_AND_WALK_FORWARD_SUFFICIENCY_V1`
