# Forex Demo Candidate Review Readiness V1

## Purpose

This packet defines a deterministic read-only evaluator for deciding whether a Forex profit candidate is mature enough for owner review toward a later supervised demo readiness lane.

The evaluator reviews sanitized evidence only. It does not authorize demo execution, live execution, broker access, bank access, credential use, strategy execution changes, background services, dashboard runtimes, or money movement.

## Input Sources

Expected sanitized inputs may include:

- `evidence_sufficiency`
- `profit_candidate_quality`
- `risk_controls`
- `observability`
- `owner_gate`
- `broker_boundary`
- `data_quality`
- `readiness_snapshot`
- `remaining_work_closure_index`
- `thresholds`
- `as_of_date`
- `owner_name`

Sensitive input keys such as routing numbers, account numbers, card values, passwords, API keys, tokens, secrets, or credentials block the evaluator. Sensitive values are not echoed.

## No Fixed Return Promise

This packet does not promise fixed returns and does not authorize profit claims. It evaluates readiness evidence, safety boundaries, and owner-review blockers only.

## Opportunity-Capture Objective

The governing objective is:

`maximize validated risk-adjusted opportunity capture while preserving capital and proving edge`

The evaluator uses that objective to organize readiness evidence without granting execution authority.

## Threshold Policy

Default thresholds:

- `min_readiness_score`: 0.80
- `min_evidence_sufficiency_score`: 0.75
- `min_candidate_quality_score`: 0.75
- `min_risk_control_score`: 0.80
- `min_observability_score`: 0.75
- `min_data_quality_score`: 0.80

Numeric overrides are accepted only when they remain conservative enough:

- `min_readiness_score` cannot go below 0.70
- `min_evidence_sufficiency_score` cannot go below 0.70
- `min_candidate_quality_score` cannot go below 0.70
- `min_risk_control_score` cannot go below 0.75
- `min_observability_score` cannot go below 0.70
- `min_data_quality_score` cannot go below 0.75

Rejected overrides are reported as `threshold_override_rejected`, and the default threshold remains active.

## Evidence Sufficiency Summary

Evidence sufficiency evaluates `evidence_status`, demo-candidate sufficiency, sample sufficiency, walk-forward clearance, OOS stability, regime coverage, and `evidence_sufficiency_score`.

Weak or incomplete evidence blocks with `BLOCKED_BY_EVIDENCE_SUFFICIENCY`.

## Candidate Quality Summary

Candidate quality evaluates `quality_status`, `candidate_quality_score`, `demo_review_ready`, `can_queue_demo_candidate_review_readiness`, improvement blockers, and blocker summaries from the prior quality-improvement lane.

Weak or not-ready candidate quality blocks with `BLOCKED_BY_CANDIDATE_QUALITY`.

## Risk Control Summary

Risk controls evaluate `risk_control_score`, drawdown evidence, daily loss stop configuration, kill-switch presence, max-loss gates, position-size limits, and risk blocks.

Missing or weak controls block with `BLOCKED_BY_RISK_CONTROLS`.

## Observability Summary

Observability evaluates `observability_score`, audit-log presence, sanitized evidence, owner-review packet presence, monitoring plan presence, dashboard projection safety, and observability blocks.

Weak observability blocks with `BLOCKED_BY_OBSERVABILITY`.

## Owner Gate Summary

Owner gate evidence must show owner review is required, owner approval is required, owner review is ready, execution is not allowed, and manual review remains the only path.

Weak owner-gate evidence blocks with `BLOCKED_BY_OWNER_GATE`.

## Broker Boundary Summary

Broker boundary evidence must show broker API access, trade execution, credential use, demo execution, money movement, and bank access are not allowed.

Any true broker, execution, credential, bank, or money flag blocks with `BLOCKED_BY_BROKER_BOUNDARY`.

## Data Quality Summary

Data quality evaluates `data_quality_score`, missing fields, invalid rows, duplicate trades, malformed timestamps, and sensitive-data presence.

Weak data quality or sensitive input blocks with `BLOCKED_BY_DATA_QUALITY`.

## Owner Action Queue

The evaluator returns ordered owner-review actions:

- `REVIEW_EVIDENCE_SUFFICIENCY`
- `REVIEW_CANDIDATE_QUALITY`
- `REVIEW_RISK_CONTROLS`
- `REVIEW_OBSERVABILITY`
- `REVIEW_OWNER_GATE`
- `REVIEW_BROKER_BOUNDARY`
- `REVIEW_DATA_QUALITY`
- `REVIEW_NEXT_PACKET`

Every action has `owner_decision_required = True` and `execution_allowed = False`.

## Blocker Summary

The evaluator aggregates blockers from missing inputs, threshold guardrails, evidence sufficiency, candidate quality, risk controls, observability, owner gate, broker boundary, and data quality.

Readiness statuses are:

- `DEMO_REVIEW_READY`
- `NEEDS_MORE_EVIDENCE`
- `BLOCKED_BY_EVIDENCE_SUFFICIENCY`
- `BLOCKED_BY_CANDIDATE_QUALITY`
- `BLOCKED_BY_RISK_CONTROLS`
- `BLOCKED_BY_OBSERVABILITY`
- `BLOCKED_BY_OWNER_GATE`
- `BLOCKED_BY_BROKER_BOUNDARY`
- `BLOCKED_BY_DATA_QUALITY`
- `INCOMPLETE_INPUTS`

## Safety Boundary

This packet is read-only and manual-review only.

## No Money Movement

The evaluator cannot deposit, withdraw, transfer, wire, automate, or otherwise alter funds.

## No Bank/Broker Access

The evaluator cannot access bank accounts, broker accounts, broker APIs, or broker execution surfaces.

## No Demo Execution

The evaluator cannot place, route, modify, close, schedule, or supervise demo trades.

## No Live Trade Execution

The evaluator cannot place, route, modify, close, schedule, or supervise live trades.

## No Credentials

The evaluator must not request, store, read, or use credentials, API keys, tokens, account numbers, card data, passwords, or secrets.

## No Scheduler/Daemon/Webhook

The evaluator does not create schedulers, daemons, webhooks, background monitors, dashboard runtimes, or server processes.

## Next Packet

If demo-candidate review readiness is ready, the next packet is:

`AIOS_FOREX_SUPERVISED_DEMO_READINESS_PACKET_V1`

If readiness is blocked or incomplete, rerun:

`AIOS_FOREX_DEMO_CANDIDATE_REVIEW_READINESS_V1`
