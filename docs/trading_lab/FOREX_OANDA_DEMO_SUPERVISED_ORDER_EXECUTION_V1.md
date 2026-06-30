# Forex OANDA Demo Supervised Order Execution V1

## Purpose

This document describes the governed OANDA demo supervised order execution controller created for `AIOS_FOREX_OANDA_DEMO_SUPERVISED_ORDER_EXECUTION_V1`.

The controller validates a sanitized owner-approved OANDA demo order payload and may call only an injected adapter object. It does not create, configure, import, or reach a real broker client.

## Input Sources

Expected input is a sanitized payload containing:

- `runtime_handoff_package`
- `owner_approval`
- `oanda_demo_boundary`
- `order_preview`
- `risk_gates`
- `abort_conditions`
- `telemetry`
- `post_trade_review`
- optional `data_quality`

If core evidence is missing, the controller returns `INCOMPLETE_INPUTS`.

## Owner Approval

Owner approval evidence must show Anthony as owner when a name is provided, final demo execution approval, accepted order preview, accepted demo-only boundary, accepted risk limits, one-order-only acceptance, owner cancel authority, `DEMO_PRACTICE` execution mode, and live execution blocked.

## Injected Adapter-Only Design

The controller can call only a supplied in-memory object that exposes `submit_demo_order(order_request)` or `submit_order(order_request)`.

No adapter is created inside the controller. If all gates pass and no adapter is supplied, status is `READY_FOR_OWNER_SUPERVISED_DEMO_EXECUTION` and the next packet is `AIOS_FOREX_OANDA_DEMO_BROKER_ADAPTER_RUNTIME_BINDING_V1`.

## Fake Adapter Test Boundary

Tests use a fake adapter object. The fake adapter receives exactly the sanitized order request and records one call. This proves the call path without broker credentials, broker imports, live account access, or external execution.

## No Direct Broker API

The controller keeps `direct_broker_api_allowed = False`. It does not import or configure broker clients, network transports, terminal launchers, background workers, or external service hooks.

## No Live Execution

The controller always keeps `live_execution_allowed = False`, `live_trading_allowed = False`, and `real_money_allowed = False`. A demo adapter call is not live execution authority.

## No Money Movement

The controller always keeps bank access, deposits, withdrawals, fund transfer behavior, and real-money behavior blocked.

## No Credentials

The controller does not read, request, store, persist, or emit credentials. Sensitive payload keys such as password, account number, card data, token, secret, and API-key fields return `BLOCKED_BY_DATA_QUALITY`. Boundary booleans such as `credential_use_allowed`, `broker_api_allowed`, `order_placement_allowed`, and `live_execution_allowed` are treated as safety evidence, not credential material.

## OANDA Demo Boundary

The OANDA demo boundary requires:

- broker name `OANDA` or unspecified
- broker mode `DEMO`, `OANDA_DEMO`, or `PRACTICE`
- account environment `PRACTICE`, `DEMO`, or `OANDA_DEMO`
- demo account only
- live account, real money, money movement, bank access, direct broker API, credential use, and live execution blocked
- order placement allowed only as an injected-adapter demo boundary after all gates pass

## Order Preview

The order preview requires strategy ID, candidate ID, instrument, supported side, supported order type, positive units within the max-position limit when supplied, stop loss, take profit, max spread, max slippage, owner acceptance, and no order preview blockers.

## Risk Gates

Risk gates require max-loss gate, daily-loss stop, kill switch, inactive kill switch, position-size limit, risk per order at or below `0.01`, daily loss at or below `0.03`, one-order-only control, and no risk blockers.

## Abort Conditions

Abort evidence must require stop behavior for missing owner approval, missing credentials, non-demo broker mode, spread above max, slippage above max, missing stop loss, missing take profit, daily loss hit, active kill switch, duplicate order, wrong account, and live account detection.

## Telemetry

Telemetry requires audit logging, sanitized ticket, pre-order snapshot, order preview snapshot, post-order snapshot, exception capture, owner review report, execution result, and no telemetry blockers.

## Post-Trade Review

Post-trade review requires review of PnL, risk, and execution quality. The next demo order stays blocked until review is complete.

## Sanitized Order Request

The adapter receives only:

- schema and mode
- broker name, broker mode, and account environment
- strategy ID and candidate ID
- instrument, side, order type, and units
- stop-loss and take-profit presence booleans
- max spread and slippage limits
- risk limits
- owner name and final demo approval boolean
- `demo_only = True`
- `live_execution_allowed = False`
- `credentials_included = False`

Raw credentials, account identifiers, card data, tokens, secrets, notes, and arbitrary payload fields are excluded.

## Owner Action Queue

Every result includes owner review actions for runtime handoff, owner approval, OANDA demo boundary, order preview, risk gates, abort conditions, telemetry, post-trade review, adapter contract, execution result, and next packet. Each action requires owner decision and keeps live execution blocked.

## Blocker Summary

The controller resolves status in fail-closed order:

1. sensitive data or data-quality blockers
2. missing core evidence
3. runtime handoff blockers
4. owner approval blockers
5. OANDA demo boundary blockers
6. order preview blockers
7. risk gate blockers
8. abort condition blockers
9. telemetry blockers
10. post-trade review blockers
11. missing or invalid adapter contract
12. fake-adapter execution path when all gates pass

## Safety Boundary

The controller always blocks direct broker API use, live trading, real-money use, money movement, bank access, credential storage, credential reads, schedulers, daemons, webhooks, dashboard runtime creation, fixed-return claims, and profit claims.

## Next Packet

If all evidence passes and no adapter is supplied, the next packet is `AIOS_FOREX_OANDA_DEMO_BROKER_ADAPTER_RUNTIME_BINDING_V1`.

If the fake-adapter path runs successfully, the next packet is `AIOS_FOREX_OANDA_DEMO_POST_EXECUTION_REVIEW_V1`.
