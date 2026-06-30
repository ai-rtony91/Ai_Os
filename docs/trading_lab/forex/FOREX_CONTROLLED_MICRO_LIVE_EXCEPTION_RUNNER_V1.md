# Forex Controlled Micro-Live Exception Runner V1

This packet creates the controlled micro-live exception runner.

## Purpose

- This packet transitions the pipeline after owner approval grant and protected demo-lane checks.
- Micro-live means **real-money** live trading risk.
- The packet defines the controlled one-time live execution gate before the later autonomous engine.

## Scope

- Default validation is a repo-safe dry-run.
- Runtime requires explicit flag: `--owner-approved-controlled-micro-live-exception`.
- Runtime is restricted to OANDA **live** endpoint and live environment.
- Runtime reads only live Bitwarden item `AIOS / OANDA / Live / Broker Runtime`.
- Runtime reads only fields needed for execution:
  - `broker_api_token`
  - `broker_account_id`
  - `endpoint`
  - `environment`
  - `allowed_mode`
- Runtime uses OANDA live endpoint only (`https://api-fxtrade.oanda.com`).
- Runtime requires `allowed_mode` `controlled_micro_live_exception_only`.
- Runtime can place **at most one** live micro order.
- Units default to `1` and SL/TP are required in payload fields.
- Order type is market and uses time-in-force FOK by default.

## Safety

- Default dry-run does not place live orders.
- Default dry-run does not place demo orders.
- Default dry-run does not move money.
- Default dry-run does not call a broker API.
- Default dry-run does not start a scheduler.
- Default dry-run does not start a daemon.
- Default dry-run does not start a webhook.
- Runtime mode does not start 22h/6d autonomous execution.
- Runtime mode does not start a scheduler.
- Runtime mode does not start a daemon.
- Runtime mode does not start a webhook.
- Runtime mode does not loop.

## Stage transitions

- On successful runtime-ready status, this packet advances after execution toward `micro_live_evidence_review`.
- This remains an exception-only controlled path before any broader 22h/6d live autonomy stage.
