# Forex Profit Candidate Quality Improvement V1

## Purpose

This packet defines a deterministic read-only evaluator for improving the quality of a Forex profit candidate before any later demo-candidate review readiness packet.

The evaluator reviews sanitized candidate-quality evidence only. It does not trade, access brokers, access banks, move funds, use credentials, create background services, or alter strategy execution logic.

## Input Sources

Expected sanitized inputs may include:

- `evidence_sufficiency`
- `profitability_evaluation`
- `candidate_quality_snapshot`
- `walk_forward_validation`
- `regime_results`
- `opportunity_leakage`
- `entry_exit_review`
- `false_positive_review`
- `risk_review`
- `thresholds`
- `remaining_work_closure_index`
- `as_of_date`
- `owner_name`

Sensitive input keys such as routing numbers, account numbers, card values, passwords, API keys, tokens, secrets, or credentials block the evaluator. Sensitive values are not echoed.

## No Fixed Return Promise

This packet does not promise fixed returns and does not authorize profit claims. It evaluates evidence quality and owner-review blockers only.

## Opportunity-Capture Objective

The governing objective is:

`maximize validated risk-adjusted opportunity capture while preserving capital and proving edge`

The evaluator uses that objective to rank improvement actions without authorizing execution.

## Threshold Policy

Default thresholds:

- `min_candidate_quality_score`: 0.75
- `min_expectancy_quality_score`: 0.70
- `min_profit_factor_quality_score`: 0.70
- `min_drawdown_efficiency_score`: 0.70
- `min_regime_quality_score`: 0.65
- `max_missed_opportunity_count`: 0
- `max_false_positive_count`: 0
- `max_late_entry_count`: 0
- `max_early_exit_count`: 0
- `min_risk_adjusted_quality_score`: 0.70
- `min_data_quality_score`: 0.80

Numeric overrides are accepted only inside conservative guardrails. Rejected overrides are reported as `threshold_override_rejected` and the default threshold remains active.

## Expectancy Quality

Expectancy quality evaluates `expectancy_quality_score` or a derived score from sanitized expectancy evidence. Weak expectancy blocks with `BLOCKED_BY_EXPECTANCY`.

## Profit Factor Quality

Profit factor quality evaluates `profit_factor_quality_score` or a derived score from sanitized profit-factor evidence. Weak profit factor blocks with `BLOCKED_BY_PROFIT_FACTOR`.

## Drawdown Efficiency

Drawdown efficiency evaluates `drawdown_efficiency_score` or a derived score from maximum drawdown evidence. Weak drawdown efficiency blocks with `BLOCKED_BY_DRAWDOWN_EFFICIENCY`.

## Regime Quality

Regime quality evaluates `regime_quality_score`, covered regimes, and weak regimes. Regime-specific weakness blocks with `BLOCKED_BY_REGIME_WEAKNESS`.

## Missed-Opportunity Leakage

Missed-opportunity leakage evaluates missed valid setups and rejected winners. Any count above the active threshold blocks with `BLOCKED_BY_MISSED_OPPORTUNITY_LEAKAGE`.

## False Positive Quality

False positive quality evaluates rejected or invalid signals that should not have been candidates. Any count above the active threshold blocks with `BLOCKED_BY_FALSE_POSITIVES`.

## Entry/Exit Timing Quality

Entry and exit timing quality evaluates late entries and early exits. Timing leakage above the active threshold blocks with `BLOCKED_BY_ENTRY_EXIT_QUALITY`.

## Risk-Adjusted Quality

Risk-adjusted quality evaluates whether opportunity capture remains disciplined after expectancy, profit factor, and drawdown are considered together. Weak or missing risk-adjusted evidence keeps the lane in `NEEDS_MORE_EVIDENCE`.

## Improvement Actions

The evaluator returns ordered owner-review actions:

- `IMPROVE_EXPECTANCY_QUALITY`
- `IMPROVE_PROFIT_FACTOR_QUALITY`
- `IMPROVE_DRAWDOWN_EFFICIENCY`
- `IMPROVE_REGIME_WEAKNESS`
- `REVIEW_MISSED_OPPORTUNITY_LEAKAGE`
- `REVIEW_FALSE_POSITIVES`
- `REVIEW_ENTRY_EXIT_TIMING`
- `REVIEW_RISK_ADJUSTED_QUALITY`
- `REVIEW_NEXT_PACKET`

Every action has `owner_decision_required = True` and `execution_allowed = False`.

## Blocker Summary

The evaluator separates blockers into candidate, expectancy, profit-factor, drawdown, regime, missed-opportunity, false-positive, entry/exit, risk-adjusted, data-quality, threshold, and all-blocker groups.

## Owner Action Queue

The owner action queue mirrors the improvement actions. It is an owner-review queue only and does not approve trading, broker access, bank access, credential use, or money movement.

## Safety Boundary

This packet is read-only and manual-review only.

## No Money Movement

The evaluator cannot deposit, withdraw, transfer, wire, automate, or otherwise move funds.

## No Bank/Broker Access

The evaluator cannot access bank accounts, broker accounts, broker APIs, or broker execution surfaces.

## No Trade Execution

The evaluator cannot place, route, modify, close, or schedule trades.

## No Credentials

The evaluator must not request, store, read, or use credentials, API keys, tokens, account numbers, card data, passwords, or secrets.

## No Scheduler/Daemon/Webhook

The evaluator does not create schedulers, daemons, webhooks, background monitors, dashboard runtimes, or server processes.

## Next Packet

If quality is ready, the next packet is:

`AIOS_FOREX_DEMO_CANDIDATE_REVIEW_READINESS_V1`

If quality is blocked or incomplete, rerun:

`AIOS_FOREX_PROFIT_CANDIDATE_QUALITY_IMPROVEMENT_V1`
