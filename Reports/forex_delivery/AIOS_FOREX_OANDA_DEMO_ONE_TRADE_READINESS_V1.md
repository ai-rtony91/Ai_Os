# AIOS Forex OANDA Demo One Trade Readiness V1

## Current State

The owner-run OANDA demo vault-backed read-only preflight returned `VAULT_PREFLIGHT_READ_ONLY_ATTEMPTED` with no blockers and favorable read-only metadata evidence. The token/account path was reported valid for OANDA practice metadata, account details, account summary, instruments, and `EUR_USD` availability.

This readiness layer is a gate only. It does not call OANDA, read credentials, read an account ID, place an order, or create execution authority.

## Required Prior Evidence

Required prior evidence:

- first OANDA demo order-attempt 403 evidence captured.
- vault-backed read-only OANDA practice preflight completed by the owner.
- preflight result is sanitized and contains no token or account ID value.
- no order endpoint was called during preflight.
- no live endpoint was used during preflight.
- no second order attempt has been made by this lane.

## Demo One-Trade Readiness Standard

The evaluator requires all readiness confirmations to be true before returning `READY_FOR_OWNER_DEMO_ONE_TRADE_COMMAND_PACKAGE`:

- demo only confirmed.
- read-only preflight passed.
- owner runtime command remains required.
- Codex broker call was not performed.
- instrument is allowed.
- `EUR_USD` is available.
- direction is allowed.
- micro units are present.
- stop loss is present.
- take profit is present.
- max loss gate passed.
- daily stop gate passed.
- kill switch state passed.
- one-order-only cap is available.
- post-trade evidence plan is present.
- result bucket plan is present.
- next allocation plan is present.
- compound or withdraw decision is conditional.
- no live endpoint is present.
- no scheduler, daemon, or webhook is requested.
- no profit claim is made.

## Risk Gate Standard

Risk readiness requires a micro-size demo order plan, explicit stop loss, explicit take profit, max loss gate pass, daily stop gate pass, and evidence plans for post-trade capture, result bucket classification, and next allocation review.

Any missing risk element returns `BLOCKED_BY_RISK_GATE`. A kill-switch failure returns `BLOCKED_BY_KILL_SWITCH`. An unavailable one-order cap returns `BLOCKED_BY_ORDER_CAP`.

## Owner Manual Runtime Boundary

The next possible trade command package must be owner-run and demo/practice only. Codex must not run broker commands, read credentials, read account IDs, call OANDA, or place an order.

The readiness evaluator accepts only non-secret confirmation flags. It does not accept access token or account ID arguments.

## Post-Trade Evidence Standard

Any future owner-run one-trade attempt must be followed by sanitized post-trade evidence capture. Evidence must not include token values, account ID values, credentials, secrets, passwords, authorization headers, screenshots with secrets, or raw broker credential material.

The post-trade evidence layer must preserve the one-order-only cap and must not authorize a second order.

## Result Bucket Standard

Sanitized post-trade evidence must feed result-to-bucket classification before any next allocation decision. Bucket handling is accounting and decision support only; it does not create a broker command or execution authority.

## Compound Or Withdraw Decision Standard

Compounding and withdrawal decisions are conditional. They require post-trade evidence, bucket classification, owner review, and a separate approved next packet.

No automatic compounding, automatic withdrawal, unattended trade continuation, scheduler, daemon, or webhook is authorized.

## +120 Percent Campaign Interpretation

The +120 percent item remains a campaign target only. AIOS does not claim that +120 percent is achieved, achievable, or guaranteed. One trade is not a requirement or proof of the campaign target.

AIOS cannot claim profitability until validated evidence proves it.

## Live Trading Boundary

Live trading remains blocked. The readiness evaluator requires `no_live_endpoint` to be true and returns `BLOCKED_BY_LIVE_ENDPOINT` if a live endpoint is present or requested.

No live credential, live account, live order, live routing, or live trading authority is created by this readiness layer.

## Exact Next Safe Packet If READY

If and only if the evaluator returns `READY_FOR_OWNER_DEMO_ONE_TRADE_COMMAND_PACKAGE`, the next safe packet is a separate owner-command package:

```text
AIOS-FOREX-OANDA-DEMO-OWNER-ONE-TRADE-COMMAND-PACKAGE-V1
```

That packet should create a sanitized owner-run demo one-trade command package only. It must preserve demo-only scope, one-order-only cap, explicit stop loss, explicit take profit, no live endpoint, no autonomous execution, no credential/account value printing, no repo persistence, no commit, and no push.
