# Demo Connection Proof Request Draft Dry-Run Template

Status: FOREX_DELIVERY request draft template. This document is value-free and non-executing. It is for Human Owner review preparation only and does not authorize broker connection, credential access, account access, endpoint activation, network API calls, market-data fetch, paper orders, live orders, scheduler, daemon, webhook, retry loop, autonomous re-entry, commit, push, or merge.

## Draft Boundary

Use labels and template markers only. Do not paste real broker values into this file, reports, tests, logs, telemetry, chat, or command output.

Forbidden material:

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

## Request Draft Fields

| Field | Draft value requirement |
|---|---|
| broker_family_label | Label only, such as OANDA_PRACTICE. |
| demo_practice_mode_confirmed | Boolean true. |
| runtime_auth_reference_label | Sanitized label only, such as SANITIZED_REFERENCE_ONLY. No token, secret, credential, account, endpoint, or private value. |
| external_connector_readiness_flag | Boolean true for future external connector review only. |
| protected_action_approval_requested | Boolean true when Human Owner review is requested. This is not approval granted. |
| network_approval_requested | Boolean true when Human Owner review is requested. This is not network approval granted. |
| endpoint_class | Demo/practice label only, such as OANDA_PRACTICE_DEMO. No live endpoint and no endpoint value. |
| account_identifier_status | ABSENT or SANITIZED only. |
| credential_material_status | ABSENT only. |
| order_route_approval | Boolean false. |
| market_data_fetch_approval | Boolean false. |
| timeout_seconds | Positive integer timeout label for future review. |
| one_shot_stop_requirement | Boolean true. |
| retry_count | Integer zero. |
| scheduler_enabled | Boolean false. |
| daemon_enabled | Boolean false. |
| webhook_enabled | Boolean false. |
| evidence_bundle_path | Sanitized repo path label only. |
| human_owner_review | Human Owner review label only. |
| future_proof_stop_point | Explicit stop point label only. |

## Copy-Safe Draft Shape

```yaml
broker_family_label: OANDA_PRACTICE
demo_practice_mode_confirmed: true
runtime_auth_reference_label: SANITIZED_REFERENCE_ONLY
external_connector_readiness_flag: true
protected_action_approval_requested: true
network_approval_requested: true
endpoint_class: OANDA_PRACTICE_DEMO
account_identifier_status: ABSENT
credential_material_status: ABSENT
order_route_approval: false
market_data_fetch_approval: false
timeout_seconds: 10
one_shot_stop_requirement: true
retry_count: 0
scheduler_enabled: false
daemon_enabled: false
webhook_enabled: false
evidence_bundle_path: Reports/forex_delivery/sanitized-demo-connection-request-draft.md
human_owner_review: Anthony Meza
future_proof_stop_point: stop-before-any-broker-facing-action-unless-separately-approved
```

## Draft Classification

The request draft validator must return exactly one:

- INVALID
- DRAFT_READY

DRAFT_READY means the request draft is complete enough for Human Owner review preparation only. It does not grant protected-action approval, network approval, broker connection approval, credential access, market-data access, or order access.

INVALID means a required field is missing or forbidden material, live endpoint reference, order route request, market-data fetch request, retry behavior, scheduler/daemon/webhook behavior, or any execution request is present.

## Required Stop Point

Stop after request draft validation. Do not connect broker, request credentials, read credentials, activate endpoints, call network APIs, fetch market data, place paper orders, place live orders, mutate approval state, commit, push, or merge.
