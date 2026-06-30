# Forex OANDA Demo Owner-Approved Runtime Handoff V1

## Purpose

`AIOS_FOREX_OANDA_DEMO_OWNER_APPROVED_RUNTIME_HANDOFF_V1` is a deterministic read-only evaluator for sanitized OANDA demo runtime-handoff evidence. It answers whether the prior OANDA demo execution-prep package is ready for Anthony's owner review before a later supervised demo order-execution packet.

This packet does not place orders, access OANDA, request credentials, store credentials, create runtime processes, or authorize demo or live execution.

## Input Sources

The evaluator accepts sanitized in-memory evidence for:

- execution-prep package
- owner approval
- runtime credential boundary
- OANDA account boundary
- order preview
- risk gates
- abort conditions
- telemetry
- post-trade review
- data quality
- readiness snapshot
- remaining work closure index

## No Fixed Return Promise

The packet makes no fixed return promise and does not authorize a profit claim. Its opportunity-capture objective is to maximize validated risk-adjusted opportunity capture while preserving capital and proving edge.

## Threshold Policy

Default thresholds:

- runtime handoff score: `0.92`
- execution prep score: `0.90`
- owner approval score: `0.95`
- runtime credential boundary score: `0.95`
- OANDA account boundary score: `0.95`
- order preview score: `0.90`
- risk gate score: `0.90`
- abort condition score: `0.95`
- telemetry score: `0.85`
- post-trade review score: `0.80`
- data quality score: `0.80`

Threshold overrides are accepted only when numeric and not below the packet guardrails. Rejected overrides add `threshold_override_rejected` to blockers and prevent ready status.

## Execution Prep Summary

The upstream execution-prep package must report `OANDA_DEMO_EXECUTION_PREP_READY`, `READY`, or `PASS`; have `prep_ready = true`; have `runtime_handoff_ready = true`; meet the execution-prep threshold when scored; and have no prep blockers.

## Owner Approval

Owner approval evidence must preserve Anthony as Human Owner. Required evidence includes owner approval required, named owner approval required, owner review required, owner acceptance of the sanitized package, owner acceptance of demo-only boundaries, owner acceptance of runtime credential entry, owner acceptance of one-order-only scope, owner cancel authority, and execution not allowed in this packet.

## Runtime Credential Boundary

Runtime credentials may be required only for a later owner-supervised runtime step. This evaluator requires runtime-only credential entry by the owner, credential redaction, and secret scanning evidence.

The boundary must keep credentials included false, credentials persisted false, credentials requested false, and credential use allowed false.

## OANDA Account Boundary

The account boundary must remain OANDA demo/practice only. Broker mode may be `DEMO`, `OANDA_DEMO`, `PRACTICE`, or `PAPER_DEMO`; account environment may be `PRACTICE`, `DEMO`, or `OANDA_DEMO`.

Live account use, real-money authority, bank access, money movement, broker API use, trade execution, demo execution, and order placement must all remain false.

## Order Preview

The order preview must identify strategy, candidate, instrument, side, units, stop-loss presence, take-profit presence, spread cap, slippage cap, owner acceptance, and required order-preview snapshot. Supported sides are `BUY`, `SELL`, `LONG`, and `SHORT`. Supported order types, when supplied, are `MARKET`, `LIMIT`, and `PREP_ONLY`.

The preview is evidence only and does not authorize order placement.

## Risk Gates

Risk gates require max loss, daily loss stop, kill switch, position-size limit, max risk per trade no greater than `0.01`, max daily loss no greater than `0.03`, one-order-only scope, and no risk gate blockers.

## Abort Conditions

Abort conditions must fail closed when owner approval is missing, credentials are missing, broker mode is not demo, spread is above max, slippage is above max, stop loss is missing, take profit is missing, daily loss is hit, kill switch is active, duplicate order is detected, wrong account is detected, or live account is detected.

## Telemetry

Telemetry must require audit logging, sanitized ticket evidence, pre-trade snapshot, order-preview snapshot, post-trade snapshot, exception capture, owner review report, runtime handoff report, and no telemetry blockers.

## Post-Trade Review

Post-trade review evidence must require post-trade review, PnL review, risk review, execution-quality review, and next-trade blocking until review is complete.

## Data Quality

Data quality evidence must meet threshold, contain no missing fields, no invalid rows, no duplicate tickets, and no malformed timestamps. Sensitive input keys such as raw account numbers, routing numbers, card fields, passwords, API keys, tokens, or secret values block the evaluator and are not echoed.

## Sanitized Runtime Handoff Package

The sanitized package contains schema, mode, owner name, broker name, broker mode, account environment, strategy ID, candidate ID, instrument, side, order type, units, stop-loss presence, take-profit presence, spread cap, slippage cap, risk limits, runtime credential requirement, credentials-included false, owner named approval required, owner cancel authority, demo-only true, execution-authorized false, and order-placement-allowed false.

The package must not include raw secret, token, password, API key, account number, routing number, card data, or broker credential values.

## Owner Action Queue

The owner action queue always includes review actions for execution prep, owner approval, runtime credential boundary, OANDA account boundary, order preview, risk gates, abort conditions, telemetry, post-trade review, sanitized runtime handoff package, and next packet.

Each action requires owner decision and keeps execution allowed false.

## Blocker Summary

Status resolves in this order:

- sensitive data: `BLOCKED_BY_DATA_QUALITY`
- missing core evidence: `INCOMPLETE_INPUTS`
- weak execution prep: `BLOCKED_BY_EXECUTION_PREP`
- weak owner approval: `BLOCKED_BY_OWNER_APPROVAL`
- weak runtime credential boundary: `BLOCKED_BY_RUNTIME_CREDENTIAL_BOUNDARY`
- weak OANDA account boundary: `BLOCKED_BY_OANDA_ACCOUNT_BOUNDARY`
- weak order preview: `BLOCKED_BY_ORDER_PREVIEW`
- weak risk gates: `BLOCKED_BY_RISK_GATES`
- weak abort conditions: `BLOCKED_BY_ABORT_CONDITIONS`
- weak telemetry: `BLOCKED_BY_TELEMETRY`
- weak post-trade review: `BLOCKED_BY_POST_TRADE_REVIEW`
- weak data quality: `BLOCKED_BY_DATA_QUALITY`
- score below threshold or rejected threshold override: `NEEDS_MORE_EVIDENCE`
- all gates satisfied: `OANDA_DEMO_RUNTIME_HANDOFF_READY`

## Safety Boundary

This packet is read-only and manual-review only. It creates no scheduler, daemon, webhook, dashboard runtime, or server process.

There is no money movement, no bank access, no broker access, no demo execution in this packet, no live trade execution, no credentials, no order placement, and no change to trading strategy execution logic.

## Next Packet

If ready, the next packet is:

`AIOS_FOREX_OANDA_DEMO_SUPERVISED_ORDER_EXECUTION_V1`

If blocked or incomplete, the next packet remains:

`AIOS_FOREX_OANDA_DEMO_OWNER_APPROVED_RUNTIME_HANDOFF_V1`
