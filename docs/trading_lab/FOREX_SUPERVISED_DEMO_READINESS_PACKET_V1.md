# Forex Supervised Demo Readiness Packet V1

## Purpose

This packet defines a deterministic read-only evaluator for deciding whether AIOS is ready to queue an owner-reviewed OANDA demo supervised execution preparation packet.

The evaluator reviews sanitized evidence only. It does not authorize demo execution, live execution, broker access, bank access, credential use, strategy execution changes, background services, dashboard runtimes, or money movement.

## Input Sources

Expected sanitized inputs may include:

- `demo_candidate_review_readiness`
- `oanda_demo_boundary`
- `owner_approval_gate`
- `runtime_credential_boundary`
- `risk_controls`
- `order_safety`
- `telemetry`
- `post_demo_review`
- `data_quality`
- `readiness_snapshot`
- `remaining_work_closure_index`
- `thresholds`
- `as_of_date`
- `owner_name`

Sensitive input keys such as routing numbers, account numbers, card values, passwords, API keys, tokens, secrets, or credential material block the evaluator. Sensitive values are not echoed. Safety boundary fields such as `credential_use_allowed`, `broker_api_allowed`, and `demo_execution_allowed` are allowed as boolean evidence, and any true value blocks readiness.

## No Fixed Return Promise

This packet does not promise fixed returns and does not authorize profit claims. It evaluates supervised-demo readiness evidence, safety boundaries, and owner-review blockers only.

## Opportunity-Capture Objective

The governing objective is:

`maximize validated risk-adjusted opportunity capture while preserving capital and proving edge`

The evaluator uses that objective to organize readiness evidence without granting execution authority.

## Threshold Policy

Default thresholds:

- `min_readiness_score`: 0.85
- `min_demo_candidate_review_score`: 0.80
- `min_oanda_demo_boundary_score`: 0.90
- `min_owner_approval_gate_score`: 0.90
- `min_runtime_credential_boundary_score`: 0.90
- `min_risk_control_score`: 0.85
- `min_order_safety_score`: 0.90
- `min_telemetry_score`: 0.80
- `min_post_demo_review_score`: 0.75
- `min_data_quality_score`: 0.80

Numeric overrides are accepted only when they remain conservative enough:

- `min_readiness_score` cannot go below 0.80
- `min_demo_candidate_review_score` cannot go below 0.75
- `min_oanda_demo_boundary_score` cannot go below 0.85
- `min_owner_approval_gate_score` cannot go below 0.85
- `min_runtime_credential_boundary_score` cannot go below 0.85
- `min_risk_control_score` cannot go below 0.80
- `min_order_safety_score` cannot go below 0.85
- `min_telemetry_score` cannot go below 0.75
- `min_post_demo_review_score` cannot go below 0.70
- `min_data_quality_score` cannot go below 0.75

Rejected overrides are reported as `threshold_override_rejected`, and the default threshold remains active.

## Demo Candidate Review Summary

Demo candidate review evidence evaluates `readiness_status`, `demo_review_ready`, `readiness_score`, `next_best_packet`, and `readiness_blockers`.

Weak or not-ready candidate review evidence blocks with `BLOCKED_BY_DEMO_CANDIDATE_REVIEW`.

## OANDA Demo Boundary

OANDA demo boundary evidence evaluates `broker_name`, `broker_mode`, `demo_account_only`, `live_account_allowed`, `real_money_allowed`, `broker_api_allowed`, `trade_execution_allowed`, `demo_execution_allowed`, and `credential_use_allowed`.

Readiness requires a demo-account-only boundary, no live account authority, no real-money authority, no broker API authority, no trade authority, no demo execution authority, and no credential-use authority in this packet.

Weak or unsafe boundary evidence blocks with `BLOCKED_BY_OANDA_DEMO_BOUNDARY`.

## Owner Approval Gate

Owner approval gate evidence must show owner approval is required, owner review is required, named-owner approval is required, manual execution only remains true, execution is not allowed, an approval packet is required, and the owner can cancel.

Weak owner-gate evidence blocks with `BLOCKED_BY_OWNER_APPROVAL_GATE`.

## Runtime Credential Boundary

Runtime credential boundary evidence must show credentials are not persisted, credentials are not requested, runtime-only credentials are required for any future approved runtime, redaction is required, secret scanning is required, and credential use is not allowed in this packet.

Weak runtime credential boundary evidence blocks with `BLOCKED_BY_RUNTIME_CREDENTIAL_BOUNDARY`.

## Risk Controls

Risk controls evaluate max-loss gates, daily loss stops, kill switch presence, position-size limits, max position units, max risk per trade, max daily loss, risk score, and risk blocks.

Readiness requires max risk per trade at or below 0.01, max daily loss at or below 0.03, and no risk blocks.

Weak risk control evidence blocks with `BLOCKED_BY_RISK_CONTROLS`.

## Order Safety

Order safety evaluates stop loss, take profit, one-order-only review, market-order allowance, pending-order allowance, order-size cap, pair whitelist, spread checks, slippage checks, order score, and order blockers.

Readiness requires stop loss, take profit, one-order-only review, capped order size, pair whitelist, spread checks, slippage checks, no market-order authority, no pending-order authority, and no order-safety blocks.

Weak order-safety evidence blocks with `BLOCKED_BY_ORDER_SAFETY`.

## Telemetry

Telemetry evaluates audit log requirement, sanitized evidence requirement, pre-trade snapshot requirement, post-trade snapshot requirement, exception capture requirement, owner review report requirement, telemetry score, and telemetry blocks.

Weak telemetry evidence blocks with `BLOCKED_BY_TELEMETRY`.

## Post-Demo Review

Post-demo review evaluates post-trade review, PnL review, risk review, execution-quality review, screenshot or snapshot review, next-trade block until review, post-demo review score, and post-demo review blocks.

Weak post-demo review evidence blocks with `BLOCKED_BY_POST_DEMO_REVIEW`.

## Data Quality

Data quality evaluates `data_quality_score`, `missing_fields`, `invalid_rows`, `duplicate_trades`, and `malformed_timestamps`.

Weak data quality or sensitive input blocks with `BLOCKED_BY_DATA_QUALITY`.

## Owner Action Queue

The evaluator returns ordered owner-review actions:

- `REVIEW_DEMO_CANDIDATE_READINESS`
- `REVIEW_OANDA_DEMO_BOUNDARY`
- `REVIEW_OWNER_APPROVAL_GATE`
- `REVIEW_RUNTIME_CREDENTIAL_BOUNDARY`
- `REVIEW_RISK_CONTROLS`
- `REVIEW_ORDER_SAFETY`
- `REVIEW_TELEMETRY`
- `REVIEW_POST_DEMO_REVIEW`
- `REVIEW_NEXT_PACKET`

Every action has `owner_decision_required = True` and `execution_allowed = False`.

## Blocker Summary

The evaluator aggregates blockers from missing inputs, threshold guardrails, demo-candidate review, OANDA demo boundary, owner gate, runtime credential boundary, risk controls, order safety, telemetry, post-demo review, and data quality.

Readiness statuses are:

- `SUPERVISED_DEMO_READY`
- `NEEDS_MORE_EVIDENCE`
- `BLOCKED_BY_DEMO_CANDIDATE_REVIEW`
- `BLOCKED_BY_OANDA_DEMO_BOUNDARY`
- `BLOCKED_BY_OWNER_APPROVAL_GATE`
- `BLOCKED_BY_RUNTIME_CREDENTIAL_BOUNDARY`
- `BLOCKED_BY_RISK_CONTROLS`
- `BLOCKED_BY_ORDER_SAFETY`
- `BLOCKED_BY_TELEMETRY`
- `BLOCKED_BY_POST_DEMO_REVIEW`
- `BLOCKED_BY_DATA_QUALITY`
- `INCOMPLETE_INPUTS`

## Safety Boundary

This packet is read-only and manual-review only.

## No Money Movement

The evaluator cannot deposit, withdraw, transfer, wire, automate, or otherwise alter funds.

## No Bank/Broker Access

The evaluator cannot access bank accounts, broker accounts, broker APIs, or broker execution surfaces.

## No Demo Execution In This Packet

The evaluator cannot place, route, modify, close, schedule, or supervise demo orders.

## No Live Trade Execution

The evaluator cannot place, route, modify, close, schedule, or supervise live trades.

## No Credentials

The evaluator must not request, store, read, or use credentials, API keys, tokens, account numbers, card data, passwords, or secrets.

## No Scheduler/Daemon/Webhook

The evaluator does not create schedulers, daemons, webhooks, background monitors, dashboard runtimes, or server processes.

## Next Packet

If supervised demo readiness is ready, the next packet is:

`AIOS_FOREX_OANDA_DEMO_SUPERVISED_EXECUTION_PREP_V1`

If readiness is blocked or incomplete, rerun:

`AIOS_FOREX_SUPERVISED_DEMO_READINESS_PACKET_V1`
