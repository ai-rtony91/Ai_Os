# AIOS Forex Builder OANDA Demo Runtime Handoff

This packet defines the runtime-only handoff layer required before a future protected OANDA practice/demo connection attempt.

It does not connect to OANDA, authenticate, read `.env`, read auth values, import an OANDA SDK, call a network API, access an account, route an order, or place trades.

## Purpose

AI_OS can now validate sanitized runtime-handoff metadata proving that future auth material and account identifiers remain outside the repository and chat.

The layer is a boundary contract only. A passing result does not authorize broker connection, authentication, account access, order routing, or live execution.

## Contracts Added

- Runtime-handoff intake contract dependency.
- Runtime-handoff contract.
- Runtime-auth-reference validation contract.
- Runtime-boundary enforcement contract.
- Sanitized handoff evidence schema.
- Fail-closed handoff evaluation.

Runtime handoff now depends on the protected intake layer defined in `docs/trading_lab/AIOS_FOREX_BUILDER_OANDA_DEMO_RUNTIME_HANDOFF_INTAKE.md` and `automation/forex_engine/oanda_demo_runtime_handoff_intake.py`.

## Required Sanitized Runtime Handoff Metadata

- `broker_id: OANDA`
- `account_mode: PRACTICE_DEMO` or `PAPER_DEMO`
- `environment: OANDA_PRACTICE_DEMO` or `PRACTICE_REFERENCE_ONLY`
- `endpoint_classification: OANDA_PRACTICE_DEMO` or `PRACTICE_REFERENCE_ONLY`
- `handoff_scope: oanda_demo_runtime_handoff_only`
- `handoff_mode: RUNTIME_HANDOFF_VALIDATE_ONLY`
- `runtime_reference_present: true`
- `runtime_reference_format: SANITIZED_REFERENCE_ONLY`
- `auth_material_location: EXTERNAL_OPERATOR_CONTROLLED_RUNTIME_ONLY`
- `runtime_boundary_confirmed: true`
- `repo_storage_confirmed_absent: true`
- `account_identifier_present: false`
- `credential_value_present: false`
- `no_account_id_storage_confirmed: true`
- `no_auth_value_storage_confirmed: true`
- `audit_logging_acknowledged: true`

These fields are not credentials and are not account identifiers. They only prove the external runtime boundary is described in sanitized form.

## Runtime Boundary

The repository must not store, print, log, fixture, report, or request:

- auth values
- runtime reference values
- API keys
- access or refresh tokens
- passwords
- private keys
- account identifiers
- broker order identifiers
- raw request payloads
- raw broker response payloads
- live account data

The layer accepts only a presence flag and fixed reference format metadata.

## Fail-Closed Conditions

The runtime handoff fails closed for:

- missing or failed runtime handoff intake
- missing runtime reference
- malformed runtime reference
- repo auth material storage
- account identifier presence
- credential value presence
- credential-like values
- live endpoint references
- unauthorized probe attempts
- broker request attempts
- account access attempts
- order route attempts

Every failure keeps broker SDK use, network/API calls, broker requests, account access, order routing, real-money routing, and live execution false.

## Governed Flow Wiring

Runtime handoff is wired into:

- `automation/forex_engine/oanda_demo_runtime_handoff_intake.py`
- `automation/forex_engine/oanda_demo_auth_handoff.py`
- `automation/forex_engine/oanda_demo_connection_probe.py`
- `src/forex_delivery/governed_readiness.py`

Default governed readiness remains fail-closed because no sanitized runtime handoff is provided by default.

## Stop Point

Stop at runtime handoff validation.

No credentials are requested or stored. No account IDs are requested or stored. No OANDA connection, account access, broker request, order routing, real-money functionality, or live execution is authorized.
