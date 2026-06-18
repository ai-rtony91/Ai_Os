# Live Micro-Trade One-Shot Approval Template

Status: Non-executing approval template. This document does not authorize a trade, does not grant broker access, does not store credentials, does not store account IDs, does not store endpoint values, does not call broker APIs, does not fetch market data, does not place paper orders, does not place live orders, and does not enable live trading.

## Purpose

This template defines the minimum value-free approval record Anthony must complete later before AI_OS can review a single real-money forex micro-trade for possible execution under `RISK_POLICY.md`.

Completing this template is not enough by itself to place a trade. A later protected APPLY packet must still verify every field, fail closed on any ambiguity or risk, and stop if live trading is not explicitly authorized for exactly one trade.

## Required Approval Record

Approval authority:
- Anthony Meza / Human Owner

Required explicit approval statement:
- "I approve exactly one live real-money forex micro-trade"

Required trade parameters:
- instrument / pair: REQUIRED
- side: BUY or SELL only
- maximum units or notional size: REQUIRED, micro-only
- maximum loss cap in dollars: REQUIRED
- stop-loss requirement: REQUIRED
- take-profit setting: OPTIONAL, but must be explicitly set to used or not used
- maximum spread allowed: REQUIRED
- maximum slippage allowed: REQUIRED
- approval expiration window: REQUIRED
- kill switch / stop condition: REQUIRED
- post-trade reconciliation requirement: REQUIRED
- sanitized evidence requirement: REQUIRED

Required safety confirmations:
- no retry: REQUIRED
- no loop: REQUIRED
- no autonomous repeat: REQUIRED
- one trade only: REQUIRED
- no scheduler: REQUIRED
- no daemon: REQUIRED
- no webhook: REQUIRED
- live token controlled only by approved secret vault or operator-controlled local runtime: REQUIRED
- live endpoint category explicitly approved without endpoint URL or endpoint value exposure: REQUIRED
- account ID must not be printed, stored, logged, or written to reports: REQUIRED
- credential value must not be printed, stored, logged, or written to reports: REQUIRED
- raw broker payload must not be printed, stored, logged, or written to reports: REQUIRED
- order evidence must be sanitized: REQUIRED

## Approval Wording Block

Anthony may later provide a value-free approval in this shape:

```text
I approve exactly one live real-money forex micro-trade.

Approval authority: Anthony Meza / Human Owner
Approval timestamp: [operator-provided timestamp]
Approval expiration window: [operator-provided expiration window]
Instrument / pair: [operator-provided pair]
Side: BUY or SELL
Maximum units or notional size: [operator-provided micro-only size]
Maximum loss cap in dollars: [operator-provided cap]
Stop-loss requirement: [operator-provided stop-loss rule]
Take-profit setting: [used with rule OR not used]
Maximum spread allowed: [operator-provided cap]
Maximum slippage allowed: [operator-provided cap]
Kill switch / stop condition: [operator-provided stop condition]
Post-trade reconciliation requirement: required
Sanitized evidence requirement: required
No retry / no loop / no autonomous repeat: confirmed
One trade only: confirmed
Live token control: approved secret vault or operator-controlled local runtime only
Live endpoint category: explicitly approved by category only, with no endpoint URL or endpoint value exposed
Account ID exposure: prohibited
Credential exposure: prohibited
Raw payload exposure: prohibited
```

Do not include account IDs, credential values, token values, endpoint URLs, endpoint values, raw broker payloads, screenshots, exact account balances, private account data, or unsanitized command output in the approval record.

## Fail-Closed Blockers

Reject or block the live micro-trade review if any of these are present:

- missing approval
- stale approval
- ambiguous instrument
- ambiguous side
- missing maximum loss
- missing stop-loss
- size not micro
- live token not operator-controlled
- live endpoint not explicitly approved by category
- live endpoint URL or endpoint value exposed
- market closed or broker unavailable
- spread above cap
- slippage above cap
- account ID would be exposed
- credential value would be exposed
- raw payload would be logged
- market data payload would be logged
- order ID would be exposed outside sanitized evidence rules
- any retry loop
- any autonomous repeat
- any scheduler
- any daemon
- any webhook
- approval window missing or expired
- kill switch / stop condition missing
- post-trade reconciliation requirement missing
- sanitized evidence requirement missing

## Risk Statement

The first live trade is a system validation trade, not a profit guarantee and not a trade recommendation. Profitability is unknown and loss is possible. Live trading remains NOT_AUTHORIZED until a later explicit one-shot approval record is complete and a protected APPLY packet passes every fail-closed gate.

## Allowed Next Packet

AIOS-LIVE-MICRO-TRADE-ONE-SHOT-APPROVAL-RECORD-V1
