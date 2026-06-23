# AIOS Forex Demo Readiness Profit Trust Spine V1

## Purpose

This spine moves AIOS Forex closer to governed OANDA demo/sandbox preparation without authorizing any order action. It improves proof quality, evidence-depth checks, risk-policy validation, non-executable order intent preview, and integrated readiness state.

AIOS is closer to demo readiness, not live trading authorization.

## Sanitized Broker Proof

The OANDA broker proof intake accepts an in-memory sanitized dictionary only. It does not read files, credentials, account identifiers, `.env` content, or broker configuration. Unknown fields fail closed so sensitive material cannot be hidden in extra payload keys.

The proof must confirm demo/sandbox/practice environment, forex asset class, long permission, instrument tradability, stop-loss support, take-profit support, one-order-only support, low effective leverage, and broker-safe preview support.

## Short Side Disabled

This contract is long-only. `short_permission` may be false without blocking long-only preparation, but short-side activation remains disabled in every result. Future short-side work requires a separate account-permission and risk packet.

## Non-Executable Order Intent Preview

The order intent preview is not an order and is intentionally not sendable to OANDA. It uses neutral internal field names such as `preview_units` and `preview_instrument`. It does not include endpoints, URLs, authorization headers, account IDs, broker API paths, or request bodies.

The preview can show structure only. It never enables `execution_allowed`, `ready_to_execute`, `demo_order_allowed`, or `live_autonomy_allowed`.

## Readiness States

The orchestrator evaluates gates in this order:

1. Broker proof: missing or unsafe proof returns `AUTONOMOUS_BLOCKED_BY_BROKER_GATE`.
2. Evidence depth: insufficient long-only profitability evidence returns `AUTONOMOUS_BLOCKED_BY_EVIDENCE_DEPTH`.
3. Risk policy: missing stop loss, take profit, kill switch, daily loss, max drawdown, or one-order-only controls returns `AUTONOMOUS_BLOCKED_BY_RISK`.
4. Preview arming: malformed preview returns `AUTONOMOUS_BLOCKED_BY_EXECUTION_ARMING`.
5. Preparation only: broker, evidence, and risk ready without preview returns `AUTONOMOUS_DEMO_PREPARATION_READY`.
6. Preview only: all preparation gates plus valid non-executable preview returns `AUTONOMOUS_DEMO_READY_PREVIEW_ONLY`.

## Why Execution Stays False

This packet is proof infrastructure, not trading authorization. Execution stays false because Anthony has not separately armed demo order placement, broker mutation, credential handling, account ID handling, network trading automation, scheduler execution, or live exception authority.

## Owner Proof Needed Next

Anthony must provide a sanitized OANDA demo/practice broker and account permission proof dictionary with no credentials, no account identifiers, no `.env` content, no network evidence, and no executable broker payload.

After that, a separate owner-approved demo-order arming packet would be required before any demo order action. A separate live exception packet under the risk policy would be required before any live order action.

## Never Automate Without Approval

Do not automate broker connections, credential loading, account identifier loading, demo orders, live orders, schedulers, daemons, webhooks, background execution, or order routing without explicit owner approval and a dedicated packet.

## Profitability Work

Profitability remains evidence-gated and must be proven through sufficient sample depth, walk-forward validation, and owner-approved demo progression. This spine supports persistent profitability work by making the readiness decision deterministic, auditable, and fail-closed before any broker mutation is considered.
