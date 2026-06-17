# AIOS Forex Builder OANDA Demo Connection Gate

This packet defines the repo-side gate specification for a future one-shot OANDA practice/demo connection attempt.

It does not connect to OANDA, read `.env`, read credentials, import an OANDA SDK, call a network API, access an account, route an order, or place trades.

## Purpose

AI_OS can now validate whether a future protected connection packet has enough sanitized repo-side evidence to be reviewed.

The gate is readiness-only. A passing result means the next packet may be reviewed by the Human Owner. It does not permit a broker connection in the current packet.

## Contracts Added

- One-shot demo connection gate contract.
- Runtime-only auth boundary requirements.
- Sanitized connection evidence schema.
- No-order and no-account-ID logging rules.
- Network/broker-call approval gate requirements.
- Timeout and stop controls.
- Fail-closed gate evaluation.

## Required Sanitized Gate Metadata

A future protected connection packet may provide only sanitized gate metadata:

- `broker_id: OANDA`
- `account_mode: PRACTICE_DEMO` or `PAPER_DEMO`
- `environment: OANDA_PRACTICE_DEMO` or `PRACTICE_REFERENCE_ONLY`
- `endpoint_classification: OANDA_PRACTICE_DEMO` or `PRACTICE_REFERENCE_ONLY`
- `approval_scope: oanda_demo_connection_gate_spec_only`
- `gate_mode: CONNECTION_READINESS_ONLY`
- `external_auth_reference_present: true`
- `external_auth_reference_format: SANITIZED_REFERENCE_ONLY`
- `auth_material_location: EXTERNAL_OPERATOR_CONTROLLED_RUNTIME_ONLY`
- `runtime_auth_boundary_confirmed: true`
- `runtime_auth_proof_present: true`
- `repo_storage_confirmed_absent: true`
- `account_identifier_present: false`
- `human_owner_connection_gate_approved: true`
- `network_broker_call_gate_approved: true`
- `one_shot_only: true`
- `timeout_seconds` from `1` through `30`
- `stop_on_success_or_failure: true`
- `no_order_route_confirmed: true`
- `no_account_id_logging_confirmed: true`
- `audit_logging_acknowledged: true`

These fields are not credentials. They prove only that the future connection packet boundary is complete and sanitized.

## Runtime-Only Auth Boundary

The repository must not store, print, log, fixture, report, or request:

- credential values
- API keys
- access or refresh tokens
- passwords
- private keys
- account identifiers
- broker order identifiers
- raw request payloads
- raw broker response payloads
- live account data

The gate accepts only proof that auth material would remain under external operator-controlled runtime handling in a later packet.

## Sanitized Evidence Schema

Gate evidence may include only sanitized fields such as:

- status
- classification
- readiness boolean
- blocker list
- forbidden field paths
- credential-like value paths
- unauthorized execution field paths
- timeout setting
- one-shot control status

Evidence must exclude auth values, account identifiers, broker payloads, order payloads, account data, and live data.

## Fail-Closed Conditions

The gate fails closed when it detects:

- missing Human Owner approval
- missing runtime auth proof
- account identifier presence
- credential-like fields or values
- unsupported account mode
- live account or live endpoint classification
- order route request
- broker request attempt
- network/API enablement
- timeout outside the allowed range
- missing stop control
- missing no-order or no-account-ID logging confirmation

Every failure keeps broker SDK use, network/API calls, broker requests, account access, order routing, real-money routing, and live execution false.

## Governed Flow Wiring

`src/forex_delivery/governed_readiness.py` includes `OANDA DEMO CONNECTION GATE` as a chain link.

Default behavior is fail-closed because no protected gate approval metadata is present. A sanitized example can pass connection-readiness review, but the result remains `CONNECTION_READINESS_ONLY` and still keeps the actual connection attempt blocked.

## Stop Point

Stop at OANDA demo connection gate readiness.

No credentials are requested or stored. No OANDA connection, account access, broker request, order routing, real-money functionality, or live execution is authorized.
