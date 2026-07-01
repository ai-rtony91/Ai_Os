# Forex Completion Campaign Part 2 V1

## Campaign Packet Boundary

`AIOS_FOREX_COMPLETION_CAMPAIGN_PART2_V1` is a local APPLY campaign for Trading Lab / Forex metadata evaluation and owner-validation readiness. It creates control-plane evaluators, tests, one local safe runner, this docs packet, and a delivery report.

The campaign is metadata-only. It does not create broker calls, trade execution, credential reads, credential storage, money movement, schedulers, daemons, webhooks, or dashboard runtime.

## Part 2 Purpose

Part 2 consolidates follow-on readiness lanes after `AIOS_FOREX_LIVE_EXECUTION_AND_CAPITAL_OPERATION_CAMPAIGN_V1`. It builds deterministic evidence and gate evaluators for protected one-order review, owner runtime credential/session metadata, post-execution review, supervised 22h/6d operation readiness, and five-lane completion review.

## Consolidated Follow-On Lanes

The packet consolidates these lanes into one validation bundle:

- protected one-order runtime execution gate.
- owner runtime credential/session bridge.
- post-execution review loop.
- 22h/6d supervised operation readiness.
- five-lane completion finisher.

## Protected One-Order Runtime Execution Gate

The protected runtime gate evaluates whether a single order candidate has sanitized metadata for owner review. It requires exact approval-token metadata, an allowed OANDA mode, no account identifier value, no credential value, one-order-only policy, stop loss, take profit, max trade risk, max daily loss, spread/slippage limits, inactive kill switch, inactive daily-loss stop, and next-order lock until review.

This gate does not execute an order and does not call a broker.

## Owner Runtime Credential/Session Bridge

The credential/session bridge validates only metadata proving credentials stay outside the repo and outside chat. It requires runtime-only handoff, no stored API key, no stored account identifier, no master password, no vault password, no raw token, redaction, secret scan, session expiry, unexpired session metadata, and one-order session scope.

It does not request, read, persist, log, or validate actual credentials.

## Post-Execution Review Loop

The post-execution review loop supports two safe states:

- sanitized receipt review when a sanitized execution receipt exists.
- metadata-only not-applicable review when no execution has occurred.

Both states require owner review, audit metadata, secret-scan metadata, no raw secret logging, no raw account identifier logging, and next-order lock until review.

## 22h/6d Supervised Operation Readiness

The 22h/6d readiness evaluator scores ten components at 0 or 10 points each:

- broker session readiness.
- monitoring readiness.
- kill-switch readiness.
- post-trade review readiness.
- audit readiness.
- capital planner readiness.
- SOS readiness.
- owner approval readiness.
- credential boundary readiness.
- recovery readiness.

Passing requires 100/100. Anything less remains incomplete.

## Five-Lane Completion Finisher

The finisher combines:

- Profit Proof.
- Return Target Validation.
- Broker + Runtime Evidence.
- Safety / Real-Money Gate.
- Dashboard Truth / Owner Control.

It also summarizes protected runtime, credential/session bridge, post-execution review, 22h/6d readiness, capital operation metadata, SOS metadata, and owner-control metadata.

## Profit Proof Lane

Profit Proof requires evidence sample count, positive expectancy, profit-factor threshold, drawdown limit, walk-forward gate, out-of-sample pass, spread/slippage model, and evidence quality marked `PROVEN` or `REVIEW_READY`.

This lane does not claim profit.

## Return Target Validation Lane

Return Target Validation requires a defined target, allowed evidence status, no fixed return promise, no guaranteed profit claim, owner target review, and evidence that supports review. Partial evidence routes to continued evidence capture, not pass.

## Broker + Runtime Evidence Lane

Broker + Runtime Evidence requires protected runtime readiness, credential/session bridge readiness, declared OANDA mode, one-order protected gate metadata, no broker API call, and no credential read.

## Safety / Real-Money Gate Lane

Safety / Real-Money Gate requires kill switch readiness, daily-loss stop readiness, max-loss gate readiness, required stop loss, required take profit, one-order-only policy, money movement disabled, live trading disabled, and owner live-exception requirement.

## Dashboard Truth / Owner Control Lane

Dashboard Truth / Owner Control requires dashboard truth contract metadata, owner action queue metadata, SOS readiness, audit readiness, manual owner control, and proof that no dashboard runtime was created.

## Local Runner Script

`scripts/forex_delivery/run_forex_completion_campaign_part2_v1.py` runs one deterministic safe sample through the campaign finisher and prints JSON. It is local-only and uses no broker, credential, environment, background runtime, or dashboard runtime.

## Safe Metadata-Only Boundary

This packet is review and evidence machinery only:

- no broker call.
- no trade.
- no credential read.
- no credential storage.
- no money movement.
- no scheduler, daemon, webhook, or dashboard runtime.

## Remaining Path After This Packet

If validation passes, the next safe packet is:

`AIOS_FOREX_COMPLETION_CAMPAIGN_PART3_OWNER_VALIDATION_AND_PR_LANDING_V1`

That packet should review the Part 2 evidence, decide whether the local changes are ready for PR landing, and preserve all approval, credential, broker, live trading, money movement, and commit/push gates.

## Next Safe Owner Validation Action

Anthony can review the generated report, the focused tests, and the local runner output. No staging, commit, push, PR, merge, broker action, credential entry, or money movement is authorized by this packet.
