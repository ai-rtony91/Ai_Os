# Demo Connection Proof Approval Review Dry-Run Contract

Status: FOREX_DELIVERY dry-run contract. This document defines the approval-review boundary for a future one-shot broker demo/practice connection proof request. It does not authorize broker connection, credential access, endpoint activation, network API calls, live market-data fetch, paper orders, live orders, scheduler, daemon, webhook, queue execution, retry loop, autonomous re-entry, approval mutation, commit, push, or merge.

## Objective

Packet 04 classifies whether a future demo/practice proof request is complete enough for Human Owner review. It does not approve the request and does not make any proof executable.

## Review Outcomes

The approval-review dry-run must return exactly one classification:

- REJECTED
- INCOMPLETE
- READY_FOR_HUMAN_REVIEW

REJECTED means forbidden private data, live endpoint exposure, order route approval, market-data approval, retry behavior, scheduler/daemon/webhook behavior, or another unsafe execution request is present.

INCOMPLETE means required value-free review fields are missing or not confirmed.

READY_FOR_HUMAN_REVIEW means the request is sanitized, complete, and reviewable by the Human Owner only. It does not grant approval and does not authorize execution.

## Required Sanitized Review Fields

| Field | Required value shape |
|---|---|
| broker_family_label | Category label only, such as OANDA_PRACTICE. |
| demo_practice_mode_confirmed | Boolean true. |
| runtime_auth_reference_label | Sanitized reference label only. No token value, credential value, account ID, endpoint value, or runtime secret. |
| external_connector_readiness_flag | Boolean true for future external connector review only. |
| protected_action_approval_requested | Boolean true, meaning review is requested. This is not approval granted. |
| network_approval_requested | Boolean true, meaning review is requested. This is not network approval granted. |
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
| human_owner_review | Human Owner review field. |
| future_proof_stop_point | Explicit future-proof stop point. |

## Non-Mutation Boundary

The approval-review dry-run must not mutate approval state.

Required final capabilities remain false:

- proof_executable_now
- approval_state_mutated
- approval_state_changed
- protected_action_approval_granted
- network_approval_granted
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

The review result and any future evidence bundle must not contain:

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

## Required Fail-Closed Rules

Return INCOMPLETE when:

- Human Owner review field is missing
- protected-action approval request field is missing
- network approval request field is missing
- timeout is missing
- evidence bundle path is missing
- future-proof stop point is missing
- one-shot stop confirmation is missing

Return REJECTED when:

- credential-like values appear
- account-ID-like values appear
- live endpoint references appear
- credential material is not absent
- account identifier status is not absent or sanitized
- order route approval is true
- market-data fetch approval is true
- retry count is above zero
- scheduler flag is true
- daemon flag is true
- webhook flag is true
- any broker, network, credential, market-data, order, scheduler, daemon, webhook, retry, or autonomous re-entry execution request appears

## Next Safe Packet

The next safe packet may draft a protected demo/practice connection proof request package only after this review returns READY_FOR_HUMAN_REVIEW. It must remain value-free and must stop before any broker-facing action unless separate Human Owner approval and all protected-action gates pass.
