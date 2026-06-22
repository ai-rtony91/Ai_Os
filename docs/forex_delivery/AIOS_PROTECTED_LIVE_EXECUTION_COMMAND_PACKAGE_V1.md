# AIOS Protected Live Execution Command Package V1

## Purpose

`AIOS_PROTECTED_LIVE_EXECUTION_COMMAND_PACKAGE_V1` is the final non-executing command contract before any separately approved governed single live micro-trade. It builds a sanitized, one-order-only command package for human review, then seals that package without enabling execution.

This package does not place orders, read credentials, read environment variables, load `.env`, call OANDA, start background work, or persist broker/account material.

## Position In The Live Trading Spine

The protected live spine remains:

1. `AIOS_LIVE_PREFLIGHT_EVIDENCE_BUNDLE_V1`
2. `AIOS_PROTECTED_LIVE_EXECUTION_COMMAND_PACKAGE_V1`
3. `live_runtime_executor_v1`
4. `OandaLiveRuntimeConnectorV2`
5. `OandaLiveHttpTransportV1`

This package sits after preflight evidence and before the live runtime executor. It prepares the executor-compatible request preview but never calls the executor execution path.

## Consuming Live Preflight Evidence Bundle V1

The command package accepts injected preflight dictionaries. It recognizes the ready shape from `live_preflight_evidence_bundle_v1`, including final bridge readiness, runtime injection readiness, OANDA connector readiness, OANDA transport readiness, account/risk readiness, instrument readiness, quote/spread readiness, order intent readiness, and mobile operator readiness.

Even when the preflight bundle is ready, `execution_allowed` must remain false.

## Consuming Protected Runtime Credential Injection V1

The package imports the protected runtime injection readiness constants and treats runtime credential injection as readiness evidence only. It does not invoke runtime auth providers and does not receive or return credential values.

Credential and account persistence flags are forced false in sanitized command output.

## Consuming OANDA Live HTTP Transport V1

The package recognizes OANDA live HTTP transport readiness constants and sanitized transport evidence. It does not instantiate the transport, call an HTTP client, call `post`, build an order submission, or contact OANDA.

## Non-Executing Boundary

The package keeps these fields false in all outputs:

- `execution_requested`
- `execution_allowed`
- `order_executed`
- `broker_call_performed`
- `credential_persisted`
- `account_id_persisted`
- `raw_broker_payload_persisted`

The executor request preview is marked `preview_only` and is suitable for human review only.

## Command Sealing

`seal_protected_live_execution_command` accepts an already-ready command package and returns `PROTECTED_LIVE_COMMAND_SEALED` only when blockers are clear. Sealing does not change execution flags and does not call any connector, transport, HTTP client, or broker.

If blockers exist, the package remains unsealed.

## Samsung/Mobile Operator Readiness

The mobile summary exposes compact truth fields for command status, sealed status, instrument, side, units, stop loss, take profit, max loss gate, daily stop gate, kill switch, execution allowed, blockers, and next safe action.

The mobile summary is display-only and does not provide an execution control.

## Remaining Before Live Micro-Trade Execution

Before any live micro-trade can occur, AIOS still needs a separate current-session Human Owner-approved protected live execution command outside Codex, runtime-only credential entry outside repo files, final risk evidence review, a fake-client-free runtime operator session, and a stop-after-one-order procedure.
