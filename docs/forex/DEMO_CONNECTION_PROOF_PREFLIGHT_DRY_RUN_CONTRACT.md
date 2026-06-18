# Demo Connection Proof Preflight Dry-Run Contract

Status: FOREX_DELIVERY dry-run contract. This document defines the exact preflight boundary for a future one-shot broker demo/practice connection proof. It does not authorize broker connection, credential access, endpoint activation, network API calls, live market-data fetch, paper orders, live orders, scheduler, daemon, webhook, queue execution, retry loop, autonomous re-entry, commit, push, or merge.

## Objective

Packet 03 prepares the sanitized preflight contract required before any separately approved external demo/practice connection attempt can be reviewed.

This packet is dry-run only:

- no broker SDK or broker client integration
- no broker connection
- no credentials requested, read, printed, stored, or inferred
- no account IDs requested, read, printed, stored, or inferred
- no endpoint URLs or endpoint values requested, read, printed, stored, or inferred
- no network API calls
- no real-time market data
- no paper orders
- no live orders
- no order route
- no scheduler, daemon, webhook, queue execution, retry loop, or autonomous re-entry

## Required Sanitized Preflight Fields

| Field | Required value shape |
|---|---|
| broker_family_label | Category label only, such as OANDA_PRACTICE or OANDA_PRACTICE_DEMO. No SDK/client integration. |
| demo_practice_mode_confirmed | Boolean true. |
| runtime_auth_reference_label | Sanitized reference label only. No token value, credential value, account ID, endpoint value, or runtime secret. |
| external_connector_readiness_flag | Boolean true for future external connector review only. |
| protected_action_approval_status | Boolean false by default for this dry-run packet. |
| network_approval_status | Boolean false by default for this dry-run packet. |
| endpoint_class | Demo/practice class only. No live endpoint and no endpoint value. |
| account_identifier_status | ABSENT or SANITIZED only. No account ID, partial account ID, or masked account ID. |
| credential_material_status | ABSENT only. |
| order_route_approval | Boolean false. |
| market_data_fetch_approval | Boolean false. |
| timeout_seconds | Positive integer timeout for a future proof packet. |
| one_shot_stop_requirement | Boolean true. |
| retry_count | Integer zero. |
| scheduler_enabled | Boolean false. |
| daemon_enabled | Boolean false. |
| webhook_enabled | Boolean false. |
| evidence_bundle_path | Sanitized repo evidence path only. |
| human_owner_approval_future_proof | Human Owner approval field for future proof review only. |

## Execution Boundary

Passing this preflight means the future demo/practice proof packet may be reviewed. It does not make the proof executable.

Required final capabilities remain false:

- proof_executable_now
- broker_connection_allowed
- connection_attempt_performed
- broker_request_sent
- network_allowed
- network_api_allowed
- network_used
- market_data_allowed
- market_data_fetched
- credentials_used
- credential_material_present
- account_access_allowed
- order_route_allowed
- order_placed
- scheduler_enabled
- daemon_enabled
- webhook_enabled
- retry_loop_present
- autonomous_reentry_present
- live_endpoint_allowed
- live_execution_allowed

## Forbidden Evidence

The preflight result and any future evidence bundle must not contain:

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
- live market-data payloads
- order IDs
- fill IDs
- transaction IDs
- private account data
- command output containing private values
- logs or telemetry containing private values

## Fail-Closed Conditions

The dry-run preflight validator must fail closed if any of these are present:

- missing protected-action approval status field
- missing runtime auth reference label
- credential-like field name or value
- account-ID-like field name or value
- live endpoint class, live endpoint URL, live endpoint value, or live endpoint flag
- protected-action approval status set true in this dry-run packet
- network approval status set true in this dry-run packet
- order route approval or order route request
- market-data fetch approval or market-data request
- missing timeout
- missing one-shot stop confirmation
- retry count above zero
- scheduler flag true
- daemon flag true
- webhook flag true
- missing sanitized evidence bundle path
- missing Human Owner future proof approval field

## Next Safe Packet

The next safe packet may draft a protected demo/practice connection proof approval review. It must remain value-free and must stop before any broker-facing action unless separate Human Owner approval and all protected-action gates pass.
