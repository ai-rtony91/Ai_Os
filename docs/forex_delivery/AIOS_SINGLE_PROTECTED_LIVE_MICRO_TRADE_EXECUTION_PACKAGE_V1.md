# AIOS Single Protected Live Micro-Trade Execution Package V1

## Purpose

`AIOS_SINGLE_PROTECTED_LIVE_MICRO_TRADE_EXECUTION_PACKAGE_V1` is the final Codex-safe package around a sealed single-live-micro-trade command. It builds readiness evidence, validates final human authority fields, validates the sealed command and runtime inputs, supports one fake-only injected-client submission for tests, and returns sanitized result evidence.

It does not place a real order, read credentials, read environment variables, load `.env`, call OANDA, start background work, or persist broker/account material.

## Position In The Live Trading Spine

The live spine remains:

1. `AIOS_FOREX_FINAL_LIVE_OPERATOR_BRIDGE_V1`
2. `AIOS_PROTECTED_RUNTIME_CREDENTIAL_INJECTION_V1`
3. `OandaLiveRuntimeConnectorV2`
4. `OandaLiveHttpTransportV1`
5. `AIOS_LIVE_PREFLIGHT_EVIDENCE_BUNDLE_V1`
6. `AIOS_PROTECTED_LIVE_EXECUTION_COMMAND_PACKAGE_V1`
7. `AIOS_SINGLE_PROTECTED_LIVE_MICRO_TRADE_EXECUTION_PACKAGE_V1`

This package sits after the sealed protected command package. Inside Codex it remains fake-only and explicitly sets real execution flags false.

## Consuming Protected Live Execution Command Package V1

The package accepts the sealed output from `protected_live_execution_command_package_v1`. It requires:

- protected command ready
- protected command sealed
- live preflight ready
- final bridge ready
- runtime injection ready
- OANDA connector ready
- OANDA transport ready
- execution allowed false
- order executed false
- broker call performed false
- credential and account persistence false

The sealed command is treated as evidence. It is not an execution instruction inside Codex.

## Fake-Only Inside Codex

`execute_single_live_micro_trade_fake_only` may call only an injected fake object with `place_live_micro_order` or `submit_live_micro_order`, and only when the package is ready and `fake_client_mode` is true.

The fake path returns `SINGLE_LIVE_MICRO_TRADE_FAKE_SUBMITTED`, sets fake execution fields true, and keeps real execution fields false. A second fake submission attempt returns `second_order_blocked`.

## Human-Approved Runtime Outside Codex

Real runtime remains blocked inside Codex. Any real live micro-trade would require a later current-session Human Owner-approved runtime command outside Codex with runtime-only credential entry, current risk evidence, fake-client-free runtime wiring, and a stop-after-one-order procedure.

This package does not weaken `AGENTS.md`, `RISK_POLICY.md`, protected-action gates, commit gates, push gates, or live execution approval rules.

## One-Order-Only Enforcement

The package requires:

- one trade only
- micro size only
- max order count of one
- no retry
- no loop
- maximum units of 1000
- stop loss
- take profit

The fake-only executor records one in-memory fake submission on the supplied package object and blocks a second fake submission.

## Fake Result Evidence Vs Real Result Evidence

Fake result evidence is labeled as fake. It can show `fake_order_executed=true` and `fake_broker_call_performed=true`.

Real result evidence is never claimed by this package. Outputs force:

- `real_order_executed=false`
- `real_broker_call_performed=false`
- `order_executed=false`
- `credential_persisted=false`
- `account_id_persisted=false`
- `raw_broker_payload_persisted=false`

Sensitive fields such as credential values, authorization material, account identifiers, broker order identifiers, raw requests, raw responses, and raw payloads are removed from returned evidence.

## Samsung/Mobile Operator Truth

The mobile summary exposes compact truth fields:

- status
- instrument
- side
- units
- stop loss
- take profit
- max loss gate
- daily stop gate
- kill switch
- fake execution status
- real execution blocked status
- next safe action

The mobile summary is display-only. It does not enter credentials and does not authorize execution.

## Remaining Work

Before post-trade ledger, replay, and closeout, AIOS still needs a separate human-approved real runtime command, runtime-only credential entry outside repo files, final live result capture, sanitized post-trade ledger contract, replay evidence shape, and closeout/review procedure.
