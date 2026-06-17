# AIOS Forex Builder OANDA Demo Connection Probe

This packet adds the guarded repo-side path for a future one-shot OANDA practice/demo connection probe.

It does not connect to OANDA, authenticate, read `.env`, read auth values, import an OANDA SDK, call a network API, access an account, route an order, or place trades.

## Purpose

AI_OS can now validate the exact safety envelope for a future protected probe command:

1. Load only a runtime-auth reference presence signal.
2. Verify OANDA practice/demo mode.
3. Prepare a one-shot connection-probe envelope.
4. Record sanitized in-memory success/failure evidence.
5. Stop immediately after the result.

The current command is validation-only. A later packet must provide separate Human Owner approval before any real broker connection attempt.

The probe now depends on the OANDA demo runtime handoff intake and runtime handoff layers. Runtime handoff intake must validate sanitized metadata first, then runtime handoff must validate that auth material and account identifiers remain outside the repository and chat before probe readiness can pass.

## Probe Command

```powershell
python scripts/forex_delivery/run_oanda_demo_connection_probe.py --demo-probe-approved --network-broker-call-approved --runtime-auth-reference-present --runtime-auth-boundary-confirmed --repo-storage-confirmed-absent --one-shot-only --stop-on-success-or-failure --no-order-route-confirmed --no-account-id-logging-confirmed --audit-logging-acknowledged
```

This command emits sanitized JSON evidence. It does not perform a network call.

## Runtime-Only Auth Reference Interface

The command accepts only metadata:

- `runtime_auth_reference_present`
- `runtime_auth_reference_format: SANITIZED_REFERENCE_ONLY`
- `auth_material_location: EXTERNAL_OPERATOR_CONTROLLED_RUNTIME_ONLY`
- `runtime_auth_boundary_confirmed`

The command must not accept auth values, account identifiers, raw payloads, order payloads, or broker response bodies.

Runtime handoff intake validation is defined in `docs/trading_lab/AIOS_FOREX_BUILDER_OANDA_DEMO_RUNTIME_HANDOFF_INTAKE.md` and `automation/forex_engine/oanda_demo_runtime_handoff_intake.py`.

Runtime handoff validation is defined in `docs/trading_lab/AIOS_FOREX_BUILDER_OANDA_DEMO_RUNTIME_HANDOFF.md` and `automation/forex_engine/oanda_demo_runtime_handoff.py`.

## Required Guard Fields

- `broker_id: OANDA`
- `account_mode: PRACTICE_DEMO` or `PAPER_DEMO`
- `environment: OANDA_PRACTICE_DEMO` or `PRACTICE_REFERENCE_ONLY`
- `endpoint_classification: OANDA_PRACTICE_DEMO` or `PRACTICE_REFERENCE_ONLY`
- `probe_scope: oanda_demo_connection_probe_only`
- `probe_mode: PROBE_VALIDATE_ONLY`
- `demo_probe_approval_flag: true`
- `network_broker_call_gate_approved: true`
- `runtime_auth_reference_present: true`
- `runtime_auth_reference_format: SANITIZED_REFERENCE_ONLY`
- `auth_material_location: EXTERNAL_OPERATOR_CONTROLLED_RUNTIME_ONLY`
- `runtime_auth_boundary_confirmed: true`
- `repo_storage_confirmed_absent: true`
- `account_identifier_present: false`
- `one_shot_only: true`
- `timeout_seconds` from `1` through `30`
- `stop_on_success_or_failure: true`
- `no_order_route_confirmed: true`
- `no_account_id_logging_confirmed: true`
- `audit_logging_acknowledged: true`

## Fail-Closed Conditions

The probe path fails closed for:

- missing demo/probe approval
- missing network/broker-call approval
- live account or live endpoint labels
- account identifier presence
- auth-value or credential-like CLI arguments
- missing runtime-auth reference signal
- failed runtime-handoff intake
- order route attempts
- retry-loop attempts
- timeout outside bounds
- missing one-shot or stop controls

## Evidence Boundary

Probe evidence may record only:

- status
- classification
- outcome
- probe readiness
- blocker list
- timeout seconds
- one-shot status
- stop-after-result status
- sanitized audit event

Evidence must exclude auth values, account identifiers, broker payloads, order payloads, live account data, and raw request or response bodies.

## Stop Point

Stop at guarded OANDA demo connection probe validation.

No credentials are requested or stored. No account IDs are accepted or stored. No broker connection, account access, order routing, real-money functionality, or live execution is authorized.
