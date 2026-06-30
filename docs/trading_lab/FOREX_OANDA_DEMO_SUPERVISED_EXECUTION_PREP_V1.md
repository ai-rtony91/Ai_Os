# Forex OANDA Demo Supervised Execution Prep V1

## Purpose

`AIOS_FOREX_OANDA_DEMO_SUPERVISED_EXECUTION_PREP_V1` is a deterministic read-only evaluator for sanitized OANDA demo execution-prep evidence. It answers whether the reviewed package is ready to queue an owner-approved runtime handoff packet.

This packet does not execute trades, access OANDA, request credentials, store credentials, create runtime processes, or authorize order placement.

## Input Sources

The evaluator accepts sanitized in-memory evidence for:

- supervised demo readiness packet
- owner approval gate
- OANDA runtime boundary
- candidate ticket
- order intent
- risk gates
- order safety
- telemetry plan
- abort conditions
- data quality
- readiness snapshot
- remaining work closure index

## No Fixed Return Promise

The packet makes no fixed return promise and does not authorize a profit claim. Its opportunity-capture objective is to maximize validated risk-adjusted opportunity capture while preserving capital and proving edge.

## Threshold Policy

Default thresholds:

- execution prep score: `0.90`
- supervised demo readiness score: `0.85`
- owner approval gate score: `0.90`
- OANDA runtime boundary score: `0.90`
- candidate ticket score: `0.90`
- order intent score: `0.90`
- risk gate score: `0.90`
- order safety score: `0.90`
- telemetry plan score: `0.85`
- abort condition score: `0.90`
- data quality score: `0.80`

Threshold overrides are accepted only when numeric and not below the packet guardrails. Rejected overrides add `threshold_override_rejected` to blockers.

## Supervised Demo Readiness Summary

The upstream readiness packet must be ready, have `supervised_demo_ready = true`, meet the readiness threshold when a score is supplied, and have no readiness blockers.

## Owner Approval Gate

The owner gate must preserve Anthony as Human Owner. Required evidence includes owner approval required, named owner approval required, owner review required, approval packet required, final execution approval not collected in this prep packet, execution not allowed, owner cancel authority present, and manual execution only.

## OANDA Runtime Boundary

The runtime boundary must be OANDA demo/practice only. Broker API usage, trade execution, demo execution, order placement, credential usage, credential persistence, credential requests, live account use, and real-money authority must all remain false.

Runtime credentials may be required only in a later owner-approved runtime packet. This evaluator requires credential redaction and secret scanning evidence.

## Candidate Ticket

The candidate ticket must identify strategy, candidate, instrument, side, timeframe, quality evidence, and an empty ticket-block list. Supported sides are `BUY`, `SELL`, `LONG`, and `SHORT`.

## Order Intent

Order intent is prep-only evidence. It may describe a market, limit, or prep-only order shape, units, max position units, stop-loss presence, take-profit presence, spread cap, slippage cap, and one-order-only constraint. It does not authorize order placement.

## Risk Gates

Risk gates require max loss, daily loss stop, kill switch, position-size limit, max risk per trade no greater than `0.01`, max daily loss no greater than `0.03`, and no risk gate blockers.

## Order Safety

Order safety requires pair whitelist, spread check, slippage check, stop-loss validation, take-profit validation, duplicate-order check, market-open check, and order preview.

## Telemetry Plan

Telemetry must require audit logging, sanitized ticket evidence, pre-trade snapshot, order-preview snapshot, post-trade snapshot, exception capture, and owner review report.

## Abort Conditions

Abort conditions must fail closed when owner approval is missing, credentials are missing, broker mode is not demo, spread is above max, slippage is above max, stop loss is missing, take profit is missing, daily loss is hit, kill switch is active, or duplicate order is detected.

## Data Quality

Data quality evidence must meet threshold, contain no missing fields, no invalid rows, no duplicate tickets, and no malformed timestamps.

## Sanitized Execution-Prep Package

The sanitized package contains schema, mode, broker name, broker mode, account environment, strategy ID, candidate ID, instrument, side, timeframe, order type, units, stop-loss presence, take-profit presence, spread cap, slippage cap, risk limits, required owner approval, runtime credential requirement, credentials-included false, execution-authorized false, and order-placement-allowed false.

The package must not include raw secret, token, password, API key, account number, routing number, or broker credential values.

## Owner Action Queue

The owner action queue always includes review actions for supervised demo readiness, owner approval gate, OANDA runtime boundary, candidate ticket, order intent, risk gates, order safety, telemetry plan, abort conditions, sanitized execution-prep package, and next packet.

Each action requires owner decision and keeps execution allowed false.

## Blocker Summary

Status resolves in this order:

- sensitive data: `BLOCKED_BY_DATA_QUALITY`
- missing core evidence: `INCOMPLETE_INPUTS`
- weak supervised readiness: `BLOCKED_BY_SUPERVISED_DEMO_READINESS`
- weak owner gate: `BLOCKED_BY_OWNER_APPROVAL_GATE`
- weak OANDA boundary: `BLOCKED_BY_OANDA_RUNTIME_BOUNDARY`
- weak candidate ticket: `BLOCKED_BY_CANDIDATE_TICKET`
- weak order intent: `BLOCKED_BY_ORDER_INTENT`
- weak risk gates: `BLOCKED_BY_RISK_GATES`
- weak order safety: `BLOCKED_BY_ORDER_SAFETY`
- weak telemetry plan: `BLOCKED_BY_TELEMETRY_PLAN`
- weak abort conditions: `BLOCKED_BY_ABORT_CONDITIONS`
- weak data quality: `BLOCKED_BY_DATA_QUALITY`
- score below threshold: `NEEDS_MORE_EVIDENCE`
- all gates satisfied: `OANDA_DEMO_EXECUTION_PREP_READY`

## Safety Boundary

This packet is read-only and manual-review only. It creates no scheduler, daemon, webhook, dashboard runtime, or server process.

There is no money movement, no bank access, no broker access, no demo execution in this packet, no live trade execution, no credentials, no order placement, and no change to trading strategy execution logic.

## Next Packet

If ready, the next packet is:

`AIOS_FOREX_OANDA_DEMO_OWNER_APPROVED_RUNTIME_HANDOFF_V1`

If blocked or incomplete, the next packet remains:

`AIOS_FOREX_OANDA_DEMO_SUPERVISED_EXECUTION_PREP_V1`
