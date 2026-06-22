# AIOS OANDA Live HTTP Transport V1

## Purpose

`AIOS_OANDA_LIVE_HTTP_TRANSPORT_V1` is the real one-shot HTTP transport adapter for the governed OANDA live path. It is live-capable only when a caller injects both an HTTP client and a runtime auth provider, and only after the explicit live-runtime config gates pass.

## Position In The Live Trading Spine

The live spine remains:

1. `AIOS_FOREX_FINAL_LIVE_OPERATOR_BRIDGE_V1`
2. `live_runtime_executor_v1`
3. `oanda_live_runtime_connector_v2`
4. `oanda_live_http_transport_v1`

The bridge and executor preserve the operator approval and final execution gates. The connector preserves live connector readiness and one-order-only behavior. This transport is the last adapter that can call an injected client's `post` method for exactly one OANDA market order.

## Connector Integration

`OandaLiveRuntimeConnectorV2` accepts an injected transport object. `OandaLiveHttpTransportV1` provides `place_live_micro_order(order_intent)`, so the connector can pass sanitized order intent into the transport without knowing credential values or HTTP implementation details.

The transport returns sanitized evidence fields only: submission status, acceptance status, status code, order count, instrument, side, signed units, broker status, sanitized response, blockers, safety summary, and explicit false persistence flags.

## Human Approval Boundary

The transport remains blocked unless the config declares:

- operator-approved live runtime
- confirmed live endpoint
- one live network allowance
- runtime-only credentials
- no credential or account persistence
- one order only
- micro size only
- no repeat behavior
- injected HTTP client
- injected runtime auth provider

This file does not grant live trade approval. Real execution still requires a later explicit protected live action command from Anthony outside this packet.

## Runtime-Only Credential Doctrine

The transport does not read `.env`, does not read environment variables, does not import a network library, and does not persist credentials. The runtime auth provider is called only inside `place_live_micro_order`. Access token and account id values are local variables only and are not assigned to the transport instance or returned.

Sanitization removes token, authorization, account identifier, broker order identifier, and raw payload fields from returned evidence.

## One-Order-Only Doctrine

Each `OandaLiveHttpTransportV1` instance allows one order submission attempt. A second call returns `second_order_blocked` and does not call the injected HTTP client again.

The OANDA payload uses a market order with:

- `timeInForce` set to `FOK`
- `positionFill` set to `DEFAULT`
- stop loss on fill
- take profit on fill
- BUY units converted to positive units
- SELL units converted to negative units
- maximum micro size of 1000 units

## Samsung/Mobile Operator Relevance

This transport supports the Samsung/mobile operator surface by returning compact truth fields instead of raw broker payloads. The mobile surface can display whether the one-shot transport is ready, blocked, submitted, or accepted without exposing credentials, account identifiers, authorization headers, request URLs, or raw broker responses.

## Remaining Before Live Micro-Trade Execution

Before any real micro-trade can occur, AIOS still needs a separate human-approved protected live action command, current risk gate evidence, runtime-only credential entry outside the repo, a fake-client-free runtime operator session, final validation evidence, and an explicit stop-after-one-order procedure.
