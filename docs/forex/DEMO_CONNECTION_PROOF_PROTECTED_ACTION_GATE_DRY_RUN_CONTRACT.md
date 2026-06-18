# Demo Connection Proof Protected-Action Gate Dry-Run Contract

Status: FOREX_DELIVERY dry-run contract. This document defines the protected-action gate review boundary for a future one-shot broker demo/practice connection proof. It does not grant approval, mutate approval state, authorize broker connection, read credentials, request credentials, store account identifiers, activate endpoints, call network APIs, fetch market data, place paper orders, place live orders, start schedulers, start daemons, run webhooks, enable retry loops, enable autonomous re-entry, commit, push, or merge.

## Objective

Packet 06 validates whether a sanitized request draft is ready for protected-action gate review only. It does not approve execution and does not make a future proof executable.

The protected-action gate dry-run classifier must return exactly one classification:

- REJECTED
- INCOMPLETE
- REVIEW_READY

REJECTED means forbidden material, live endpoint exposure, approval mutation, network execution, order route approval, market-data approval, retry behavior, scheduler/daemon/webhook behavior, or another unsafe execution request is present.

INCOMPLETE means required value-free review fields are missing or not confirmed.

REVIEW_READY means the sanitized request can be reviewed by the Human Owner for a separate future protected-action approval. It does not grant that approval.

## Required Sanitized Fields

| Field | Requirement |
| --- | --- |
| request_draft_status | DRAFT_READY only. |
| broker_family_label | Demo/practice label only, such as OANDA_PRACTICE. |
| demo_practice_mode_confirmed | Boolean true. |
| runtime_auth_reference_label | Sanitized label only. No token, secret, credential, account, endpoint, or private value. |
| external_connector_readiness_flag | Boolean true. |
| protected_action_review | Present as value-free review text only. |
| human_owner_review | Anthony Meza only. |
| approval_mutation | Boolean false. |
| network_execution | Boolean false. |
| credential_material_status | ABSENT only. |
| account_identifier_status | ABSENT or SANITIZED only. |
| endpoint_class | Demo/practice label only. No live endpoint and no endpoint value. |
| order_route_approval | Boolean false. |
| market_data_fetch_approval | Boolean false. |
| scheduler_enabled | Boolean false. |
| daemon_enabled | Boolean false. |
| webhook_enabled | Boolean false. |
| retry_count | Zero only. |
| one_shot_stop_requirement | Boolean true. |
| timeout_seconds | Positive integer. |
| evidence_bundle_path | Sanitized repo evidence path only, with no private values. |
| future_proof_stop_point | Explicit value-free stop point. |

## Non-Mutation Boundary

The dry-run result must keep all approval and execution outputs false:

- proof_executable_now
- approval_state_mutated
- approval_state_changed
- protected_action_approval_granted
- network_approval_granted
- broker_connection_allowed
- connection_attempt_allowed
- connection_attempt_performed
- broker_request_sent
- network_allowed
- network_api_allowed
- network_used
- market_data_allowed
- market_data_requested
- market_data_fetched
- credentials_allowed
- credentials_used
- credential_material_present
- account_access_allowed
- order_route_allowed
- order_submit_allowed
- order_placed
- scheduler_enabled
- daemon_enabled
- webhook_enabled
- retry_loop_present
- autonomous_reentry_present
- live_endpoint_allowed
- live_execution_allowed

## Forbidden Material

The gate review must fail closed if any of the following appear in repo files, reports, tests, fixtures, logs, telemetry, chat, command output, or evidence:

- credentials
- tokens
- secrets
- credential values
- account IDs
- partial account IDs
- masked account IDs
- endpoint URLs
- endpoint values
- live endpoint references
- exact balances
- raw broker payloads
- order IDs
- fill IDs
- transaction IDs
- screenshots
- private account data
- live market-data payloads

## Fail-Closed Conditions

Return REJECTED when any of these are present:

- request_draft_status is not DRAFT_READY
- broker_family_label is not demo/practice only
- runtime_auth_reference_label contains credential-like, account-like, endpoint-like, or private value material
- approval_mutation is true
- network_execution is true
- credential_material_status is not ABSENT
- account_identifier_status is not ABSENT or SANITIZED
- endpoint_class references live endpoint context
- order_route_approval is true
- market_data_fetch_approval is true
- scheduler_enabled is true
- daemon_enabled is true
- webhook_enabled is true
- retry_count is greater than zero
- any field requests broker connection, network API permission, market-data fetch, order route, live endpoint, retry loop, or autonomous re-entry

Return INCOMPLETE when any required value-free field is missing or not confirmed.

Return REVIEW_READY only when every required value-free field is complete and all execution, approval mutation, broker, network, credential, market-data, order, scheduler, daemon, webhook, retry, and live endpoint controls remain disabled.

## Stop Point

Stop after dry-run validation and report generation. Do not grant approval, mutate approval state, connect to broker, read/request/write/print/store credentials, store account identifiers, call network APIs, fetch market data, place paper orders, place live orders, start schedulers, start daemons, run webhooks, commit, push, or merge.

## Next Safe Packet

AIOS-LIVE-MICRO-TRADE-EXCEPTION-PACKET-07-DEMO-CONNECTION-PROOF-EXECUTION-PACKET-DRAFT-DRY-RUN-V1
