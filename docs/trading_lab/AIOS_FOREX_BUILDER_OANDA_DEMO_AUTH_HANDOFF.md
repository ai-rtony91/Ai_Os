# AIOS Forex Builder OANDA Demo Auth Handoff

This packet defines the governed readiness layer for a future external OANDA demo authentication handoff.

It does not connect to OANDA, read `.env`, read credentials, import an OANDA SDK, call a network API, access an account, route an order, or place trades.

## Purpose

AI_OS can now evaluate sanitized external demo-auth readiness metadata without accepting credential values into the repository.

The handoff layer is a boundary and validation contract only. It prepares the repo to reject unsafe auth input before any future external handoff is considered.

The separate runtime handoff layer now defines the final sanitized runtime boundary required before a future protected probe path can be reviewed. Auth handoff readiness does not authorize broker connection or runtime auth access by itself.

## Contracts Added

- External authentication handoff contract.
- Credential boundary contract.
- Demo account validation contract.
- Authentication readiness check.
- Authentication failure-state classification.
- Authentication evidence requirements.
- Authentication audit logging requirements.

## Required Sanitized Handoff Metadata

A future external handoff may provide only sanitized metadata:

- `broker_id: OANDA`
- `account_mode: PRACTICE_DEMO` or `PAPER_DEMO`
- `environment: OANDA_PRACTICE_DEMO` or `PRACTICE_REFERENCE_ONLY`
- `external_auth_reference_present: true`
- `external_auth_reference_format: SANITIZED_REFERENCE_ONLY`
- `auth_material_location: EXTERNAL_OPERATOR_CONTROLLED_RUNTIME_ONLY`
- `external_auth_boundary_confirmed: true`
- `repo_storage_confirmed_absent: true`
- `account_identifier_present: false`
- `audit_logging_acknowledged: true`
- `handoff_scope: oanda_demo_auth_handoff_readiness_only`
- `handoff_mode: READINESS_ONLY`
- `human_owner_demo_auth_handoff_approved: true`

These fields are not credentials. They only prove that an external handoff boundary was described in sanitized form.

## Credential Boundary

The repository must not store, print, log, fixture, or report:

- credential values
- API keys
- access or refresh tokens
- passwords
- private keys
- account identifiers
- broker order identifiers
- raw broker payloads
- live account data

Any supplied auth material value or account identifier fails closed.

## Demo Account Validation

Allowed account modes:

- `PRACTICE_DEMO`
- `PAPER_DEMO`

Allowed environments:

- `OANDA_PRACTICE_DEMO`
- `PRACTICE_REFERENCE_ONLY`

Unsupported account types, live account indicators, and account identifiers fail closed.

## Failure States

The readiness layer classifies these fail-closed states:

- `MISSING_CREDENTIALS`
- `MALFORMED_CREDENTIALS`
- `UNSUPPORTED_ACCOUNT_TYPE`
- `LIVE_ACCOUNT_ATTEMPT`
- `UNAUTHORIZED_EXECUTION_ATTEMPT`

Every failure state keeps broker SDK use, network/API calls, broker requests, account access, real-money routing, order placement, and live execution false.

## Evidence And Audit Requirements

The readiness result emits sanitized in-memory evidence only:

- contract set
- validation result
- account validation result
- failure states
- sanitized audit event
- blocker list

Audit evidence must exclude credential values, account identifiers, broker payloads, live account data, and order data.

## Governed Flow Wiring

`src/forex_delivery/governed_readiness.py` includes `OANDA DEMO AUTH HANDOFF READINESS` as a chain link.

Runtime handoff is a downstream chain link. It must pass separately before any future protected probe packet can be considered.

Default behavior is fail-closed because no external sanitized auth handoff has been provided. A sanitized example handoff can pass readiness validation, but even a passing result does not allow broker connection, account access, network calls, order routing, or live trading.

## Stop Point

Stop at OANDA demo authentication handoff readiness.

No credentials are requested or stored. No OANDA connection, account access, broker request, order routing, real-money functionality, or live execution is authorized.
