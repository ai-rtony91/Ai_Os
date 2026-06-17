# AIOS Forex Builder OANDA Demo Protected Connection Attempt

This packet adds the protected one-shot OANDA practice/demo connection attempt boundary.

It does not store credentials, account IDs, raw broker responses, account state, market data, order payloads, or live endpoint data in the repository.

## Purpose

AI_OS can now validate and execute one bounded connection/auth-proof attempt only when all protected fields pass:

1. Human Owner approval is present.
2. OANDA practice/demo mode is selected.
3. Runtime auth material remains external operator-controlled.
4. Runtime handoff intake, runtime handoff, connection gate, and connection probe all validate.
5. Timeout and one-shot stop controls are present.
6. Account-state, market-data, order-route, retry-loop, credential, account-ID, and live endpoint requests are rejected.
7. Evidence is sanitized before it is returned.

The repo owns the contract and sanitizer. The runtime connector remains external operator-controlled and must return sanitized status only.

## Protected Attempt Command

```powershell
python scripts/forex_delivery/run_oanda_demo_protected_connection_attempt.py --human-owner-protected-demo-connection-approved --network-broker-call-approved --runtime-handoff-intake-ready --runtime-handoff-ready --connection-gate-ready --runtime-auth-reference-present --runtime-auth-boundary-confirmed --repo-storage-confirmed-absent --no-account-id-storage-confirmed --no-auth-value-storage-confirmed --one-shot-only --timeout-seconds 10 --stop-on-success-or-failure --no-order-route-confirmed --no-account-id-logging-confirmed --audit-logging-acknowledged
```

This command validates the protected envelope and emits sanitized JSON. Without an injected external runtime connector, it fails closed before any connection attempt.

## Runtime Connector Boundary

The repo-side connector boundary accepts only sanitized metadata:

- `runtime_auth_reference_present`
- `runtime_auth_reference_format: SANITIZED_REFERENCE_ONLY`
- `auth_material_location: EXTERNAL_OPERATOR_CONTROLLED_RUNTIME_ONLY`
- `runtime_auth_boundary_confirmed`
- `timeout_seconds`
- one-shot and stop controls

It must not accept auth values, credential fields, account identifiers, raw request or response bodies, account-state requests, market-data requests, order routes, or live endpoints.

## Required Approval Fields

- `human_owner_protected_demo_connection_approved: true`
- `approval_scope: oanda_demo_protected_connection_attempt_only`
- `connection_attempt_mode: ONE_SHOT_PRACTICE_DEMO_CONNECT_ONLY`
- `broker_id: OANDA`
- `account_mode: PRACTICE_DEMO`
- `environment: OANDA_PRACTICE_DEMO`
- `endpoint_classification: OANDA_PRACTICE_DEMO`
- `network_broker_call_gate_approved: true`
- `runtime_handoff_intake_ready: true`
- `runtime_handoff_ready: true`
- `connection_gate_ready: true`
- `one_shot_only: true`
- `timeout_seconds: 10`
- `stop_on_success_or_failure: true`
- `no_order_route_confirmed: true`
- `no_account_id_logging_confirmed: true`
- `audit_logging_acknowledged: true`

## Runtime Boundary Fields

- `runtime_auth_reference_present: true`
- `runtime_auth_reference_format: SANITIZED_REFERENCE_ONLY`
- `auth_material_location: EXTERNAL_OPERATOR_CONTROLLED_RUNTIME_ONLY`
- `runtime_auth_boundary_confirmed: true`
- `repo_storage_confirmed_absent: true`
- `account_identifier_present: false`
- `credential_value_present: false`
- `no_account_id_storage_confirmed: true`
- `no_auth_value_storage_confirmed: true`

## Fail-Closed Conditions

The protected attempt fails closed for:

- missing Human Owner approval
- missing runtime auth reference
- malformed runtime boundary proof
- credential-like input
- account-ID input
- live account or live endpoint labels
- order-route request
- account-state request
- market-data request
- retry-loop request
- missing timeout
- missing one-shot or stop controls
- missing external runtime connector
- connector output that contains credentials, account IDs, raw payloads, live references, account data, market data, order data, or unsafe side effects

## Evidence Boundary

Attempt evidence may include only:

- status
- classification
- outcome
- preflight status
- timeout seconds
- attempt count
- one-shot status
- stop-after-result status
- retry-loop status
- endpoint classification
- blocker list
- sanitized status family

Evidence must exclude credential values, account identifiers, broker payloads, request or response bodies, account state, market data, order payloads, and live endpoint URLs.

## Stop Point

Stop after success, failure, timeout, connector rejection, connector absence, or validation rejection.

Do not proceed to market data, account state, demo orders, live endpoints, live orders, or live trading.
