# AIOS Live Preflight Evidence Bundle V1

## Purpose

`AIOS_LIVE_PREFLIGHT_EVIDENCE_BUNDLE_V1` is the final non-executing evidence package before any later governed single live micro-trade execution command. It consolidates injected readiness evidence and proves that the system is still blocked from execution until Anthony issues a separate protected live action command.

## Position In The Live Trading Spine

The current live spine is:

1. `AIOS_FOREX_FINAL_LIVE_OPERATOR_BRIDGE_V1`
2. `AIOS_PROTECTED_RUNTIME_CREDENTIAL_INJECTION_V1`
3. `OandaLiveRuntimeConnectorV2`
4. `OandaLiveHttpTransportV1`
5. `AIOS_LIVE_PREFLIGHT_EVIDENCE_BUNDLE_V1`

This bundle sits after the bridge, injection, connector, and transport readiness surfaces. It gathers their final non-executing evidence into one operator-review object.

## Required Evidence Before Live Execution

The bundle requires ready evidence for:

- final live operator bridge
- protected runtime credential injection
- OANDA live runtime connector
- OANDA live HTTP transport
- account and risk envelope
- instrument envelope
- quote and spread envelope
- order intent envelope
- mobile operator readiness
- authenticated operator state
- protected action authorization
- live exception request
- live risk acknowledgement

It also requires `execution_requested` false, `order_executed` false, `broker_call_performed` false, no default network behavior, no repeat behavior, and one-order-only mode.

## Avoiding `.env`, Persistence, And Real Network Calls

The bundle accepts injected dictionaries only. It does not load `.env`, read environment variables, read files, write files, import a network library, call an HTTP client, call OANDA, or place an order.

All broker/account/quote values are treated as supplied evidence. They are not live fetches.

## Connection To Final Live Operator Bridge V1

The bundle recognizes bridge readiness from `FINAL_LIVE_OPERATOR_BRIDGE_READY` or an explicit `final_bridge_ready` truth field. The bridge remains the operator arming surface and does not place orders.

## Connection To Protected Runtime Credential Injection V1

The bundle recognizes protected runtime injection readiness from the injection contract or local harness status. It records readiness and sanitizes all evidence so credential values and account identifiers do not appear in the preflight output.

## Connection To OANDA Live Runtime Connector V2

The bundle accepts `OANDA_LIVE_CONNECTOR_CONFIG_READY` connector evidence and verifies that connector readiness is present before the preflight can become ready.

## Connection To OANDA Live HTTP Transport V1

The bundle accepts OANDA HTTP transport config or readiness evidence and verifies that the one-shot transport is ready without invoking `http_client.post`.

## Samsung/Mobile Operator Readiness

The mobile summary exposes compact operator truth fields:

- mode
- status
- blockers
- next safe action
- instrument
- side
- units
- stop loss
- take profit
- max loss gate
- daily stop gate
- kill switch
- spread
- quote freshness

The mobile summary is display-only. It does not enter credentials and does not authorize execution.

## Remaining Before Live Micro-Trade Execution

Before any live micro-trade execution, AIOS still needs a separate human-approved protected live execution command, runtime-only credential entry outside the repo, a fake-client-free runtime operator session, final risk evidence review, and a stop-after-one-order procedure.
