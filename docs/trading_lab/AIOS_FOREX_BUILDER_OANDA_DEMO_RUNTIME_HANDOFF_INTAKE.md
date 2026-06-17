# AIOS Forex Builder OANDA Demo Runtime Handoff Intake

This packet defines the protected intake layer for sanitized OANDA practice/demo runtime-handoff metadata.

It does not connect to OANDA, authenticate, read `.env`, read auth values, import an OANDA SDK, call a network API, access an account, route an order, or place trades.

## Purpose

AI_OS can now validate sanitized runtime-handoff intake metadata before any future protected broker connection packet can execute.

The layer accepts metadata only. A passing result does not authorize broker connection, authentication, account access, order routing, live execution, or any credential/account identifier storage.

## Contracts Added

- Runtime-handoff intake contract.
- Intake metadata acceptance rules.
- Intake metadata rejection rules.
- Sanitized intake evidence schema.
- Fail-closed intake evaluation.

## Required Sanitized Intake Metadata

- `broker_id: OANDA`
- `account_mode: PRACTICE_DEMO` or `PAPER_DEMO`
- `environment: OANDA_PRACTICE_DEMO` or `PRACTICE_REFERENCE_ONLY`
- `endpoint_classification: OANDA_PRACTICE_DEMO` or `PRACTICE_REFERENCE_ONLY`
- `intake_scope: oanda_demo_runtime_handoff_intake_only`
- `intake_mode: INTAKE_VALIDATE_ONLY`
- `metadata_intake_authorized: true`
- `runtime_reference_present: true`
- `runtime_reference_format: SANITIZED_REFERENCE_ONLY`
- `auth_material_location: EXTERNAL_OPERATOR_CONTROLLED_RUNTIME_ONLY`
- `runtime_boundary_confirmed: true`
- `external_operator_controlled_runtime_confirmed: true`
- `repo_storage_confirmed_absent: true`
- `account_identifier_present: false`
- `credential_value_present: false`
- `no_account_id_storage_confirmed: true`
- `no_auth_value_storage_confirmed: true`
- `audit_logging_acknowledged: true`

These fields are not credentials and are not account identifiers. They only prove the external runtime boundary is described in sanitized form.

## Rejection Rules

The intake layer fails closed for:

- account identifier presence
- auth value presence
- credential-like values
- live account labels
- live endpoint references
- malformed runtime references
- repo auth material storage
- unauthorized intake attempts
- broker request attempts
- account access attempts
- order route attempts

Every failure keeps broker SDK use, network/API calls, broker requests, account access, order routing, real-money routing, and live execution false.

## Evidence Boundary

Intake evidence may record only:

- status
- classification
- intake readiness
- metadata acceptance state
- runtime-boundary enforcement state
- blocker list
- sanitized audit event

Evidence must exclude auth values, runtime reference values, account identifiers, broker payloads, order payloads, live account data, and raw request or response bodies.

## Governed Flow Wiring

Runtime handoff intake is wired into:

- `automation/forex_engine/oanda_demo_runtime_handoff.py`
- `automation/forex_engine/oanda_demo_connection_probe.py`
- `src/forex_delivery/governed_readiness.py`

Default governed readiness remains fail-closed because no sanitized intake metadata is provided by default.

## Stop Point

Stop at runtime handoff intake validation.

No credentials are requested or stored. No account IDs are requested or stored. No OANDA connection, account access, broker request, order routing, real-money functionality, or live execution is authorized.
