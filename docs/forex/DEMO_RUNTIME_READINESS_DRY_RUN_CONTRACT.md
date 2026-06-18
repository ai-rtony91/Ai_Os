# Demo Runtime Readiness Dry-Run Contract

Status: FOREX_DELIVERY dry-run contract. This document defines sanitized repo-side readiness checks for a future broker demo/practice proof. It does not authorize broker connection, credential access, endpoint activation, market-data fetch, paper order placement, live order placement, scheduler, daemon, retry loop, autonomous re-entry, commit, push, or merge.

## Objective

Packet 02 prepares the value-free runtime proof boundary that must be complete before any future externally approved broker demo/practice connection proof can be reviewed.

The contract is dry-run only:

- no broker connection
- no credentials requested, read, printed, stored, or inferred
- no account IDs requested, read, printed, stored, or inferred
- no endpoint values requested, read, printed, stored, or inferred
- no network API calls
- no real-time market data
- no paper orders
- no live orders
- no order route
- no scheduler, daemon, webhook, queue execution, retry loop, or autonomous re-entry

## Required Value-Free Fields

| Field | Required value shape |
|---|---|
| broker_family_label | Category label only, such as OANDA_PRACTICE or OANDA_PRACTICE_DEMO. No credential, account, endpoint, or private value. |
| practice_demo_mode_confirmed | Boolean true. |
| runtime_auth_reference_label | Sanitized reference label only. No token value, credential value, account ID, endpoint value, or runtime secret. |
| external_connector_readiness_flag | Boolean true for future external connector review only. |
| network_approval_status | Boolean false by default for this dry-run packet. |
| account_identifier_status | ABSENT or SANITIZED only. No account ID or partial/masked account ID. |
| endpoint_class | Demo/practice class only, such as OANDA_PRACTICE_DEMO or PRACTICE_REFERENCE_ONLY. No live endpoint and no endpoint value. |
| no_order_route_approval | Boolean true. |
| no_live_endpoint | Boolean true. |
| no_credential_value | Boolean true. |
| no_account_id_value | Boolean true. |
| timeout_seconds | Positive integer timeout for a future proof packet. |
| one_shot_stop_requirement | Boolean true. |
| evidence_bundle_path | Sanitized repo evidence path only. |
| human_owner_approval_future_proof | Human Owner approval field for future proof review only. |

## Sanitized Evidence Boundary

Allowed evidence is status-only and value-free. It may record categories, booleans, pass/fail statuses, blocker names, sanitized report paths, timeout value, and stop-point text.

Forbidden evidence:

- credentials
- tokens
- secrets
- credential values
- account IDs
- partial or masked account IDs
- endpoint URLs
- endpoint values
- exact balances
- screenshots
- raw broker payloads
- raw request or response bodies
- order IDs
- fill IDs
- transaction IDs
- private account data
- command output containing private values
- logs or telemetry containing private values

## Fail-Closed Conditions

The dry-run readiness validator must fail closed if any of these are present:

- missing runtime auth reference label
- credential-like field name or value
- account-ID-like field name or value
- live endpoint class or live endpoint flag
- endpoint value or endpoint URL
- order route approval or order route request
- network approval status set true in this dry-run packet
- missing timeout
- missing one-shot stop confirmation
- missing evidence bundle path
- missing Human Owner future proof approval field
- scheduler, daemon, webhook, queue, retry, or autonomous re-entry behavior

## Dry-Run Readiness Result

A complete sanitized fixture may pass demo/runtime dry-run readiness only. Passing dry-run readiness means the future proof packet may be reviewed; it does not authorize a broker connection.

Required final capabilities remain false:

- broker_connection_allowed
- connection_attempt_performed
- broker_request_sent
- network_used
- credentials_used
- credential_material_present
- account_access_allowed
- order_route_allowed
- order_placed
- live_endpoint_allowed
- live_execution_allowed

## Next Safe Packet

The next safe packet may draft the externally approved broker demo connection proof preflight. It must remain value-free and must stop before any broker-facing action unless separate Human Owner approval and all protected-action gates pass.
