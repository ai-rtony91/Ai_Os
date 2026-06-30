# OANDA Demo Broker Adapter Runtime Binding V1

## Purpose
Provide a read-only runtime-binding layer that accepts OANDA demo order evidence, validates required operator and safety gates, and routes to an injected fake transport only.

## Relationship to supervised order-execution controller
This packet builds the adapter object consumed by `execute_oanda_demo_supervised_order_v1`:
- the adapter class exposes `submit_demo_order(order_request: dict) -> dict`.
- transport execution remains owner-approved and sandboxed.

## Relationship to demo capital cadence proof
This packet is the next runtime stage after live-proof and demo capital cadence proof packets.
It converts the same order information into a transport-safe envelope for a fake/injected binding.

## Injected transport-only design
Binding is only possible with an injected object that exposes:
- `submit_oanda_demo_order(envelope: dict)`
- or `submit_demo_order(envelope: dict)`

No transport is contacted when a transport is missing.

## No direct broker API import
The module imports only standard library helpers.
No broker SDK, HTTP client, or API transport module imports are used in this packet.

## No real OANDA call
The packet does not import requests/socket/urllib/subprocess/os.environ/broker_sdk/schedule modules.
It only emits sanitized outputs and does not perform external I/O.

## No credentials
- `credential_storage_allowed = False`
- `credential_read_allowed = False`
- `credential_values_provided` must be false in runtime context.

## No account IDs
- `account_identifier_storage_allowed = False`
- `account_identifier_values_provided` must be false in runtime context.

## No bank access
- `bank_access_allowed` must be false in runtime context and demo boundary.

## No money movement
- `money_movement_allowed = False`
- `real_money_allowed = False`
- `live_account_allowed = False`

## Runtime context requirements
- `runtime_context` requires:
  - `broker_name: OANDA`
  - `broker_mode` in `{DEMO, PRACTICE, OANDA_DEMO}`
  - `account_environment` in `{PRACTICE, DEMO, OANDA_DEMO}`
  - `demo_account_reference_present: True`
  - `account_identifier_values_provided: False`
  - `credential_values_provided: False`
  - `runtime_credentials_managed_by_owner: True`
  - `live_trading_allowed: False`

## Owner approval token requirements
- `owner_name` default `Anthony` and may be provided explicitly.
- `owner_approval_required: True`
- `owner_accepts_demo_only_boundary: True`
- `owner_accepts_injected_transport_only: True`
- `owner_accepts_no_credentials_in_repo: True`
- `owner_accepts_no_real_money: True`
- `owner_can_cancel: True`
- `approval_token_metadata_present: True`
- `approval_phrase_matches: True`
- `approval_action_matches: True`
- `approval_mode_matches: True`
- `approval_token_unexpired: True`
- `approval_token_unused: True`
- `owner_cancel_phrase_detected: False`

## Demo boundary
- `demo_boundary` requires:
  - `demo_only: True`
  - `broker_name` OANDA (or equivalent demo mode)
  - `broker_mode` in `{DEMO, PRACTICE, OANDA_DEMO}`
  - `account_environment` in `{PRACTICE, DEMO, OANDA_DEMO}`
  - false live/money values (`live_account_allowed`, `real_money_allowed`, `live_execution_allowed`, `money_movement_allowed`, `bank_access_allowed`).

## Order request requirements
- `order_request` requires:
  - `schema`, `mode`
  - `broker_name` OANDA or unspecified
  - `broker_mode` in `{DEMO, PRACTICE, OANDA_DEMO}`
  - `account_environment` in `{PRACTICE, DEMO, OANDA_DEMO}`
  - `strategy_id`, `candidate_id`, `instrument`
  - `side in {BUY, SELL, LONG, SHORT}`
  - `order_type in {MARKET, LIMIT, PREP_ONLY}`
  - `units > 0`
  - `stop_loss_present: True`
  - `take_profit_present: True`
  - `max_spread_pips` present
  - `max_slippage_pips` present
  - `demo_only: True`
  - `live_execution_allowed: False`
  - `credentials_included: False`

## Risk envelope
- `risk_envelope` requires:
  - `max_risk_per_trade_pct <= 0.01`
  - `max_daily_loss_pct <= 0.03`
  - `one_order_only: True`
  - `kill_switch_active: False`
  - `daily_loss_stop_active: False`
  - `duplicate_order_detected: False`

## Sanitized OANDA demo order envelope
The binding output builds an envelope with only:
- schema, mode, broker name, broker mode, account environment
- instrument, side, order type, units
- stop-loss/take-profit presence
- spread/slippage limits
- risk limits block
- strategy/candidate IDs
- demo-only flags (`demo_only`, `live_execution_allowed`, `credentials_included`, `account_identifiers_included`)
- `transport_injected`

No account number, token, password, key, credential, or secret values are included.

## Fake transport test path
When a valid transport is supplied:
- binding status becomes `OANDA_DEMO_FAKE_TRANSPORT_ACCEPTED`
- transport `submit` is called exactly once
- transport result is sanitized before output
- status stays owner-gated and non-live

## Owner action queue
Action IDs include:
- `REVIEW_RUNTIME_CONTEXT`
- `REVIEW_OWNER_APPROVAL`
- `REVIEW_DEMO_BOUNDARY`
- `REVIEW_ORDER_REQUEST`
- `REVIEW_RISK_ENVELOPE`
- `REVIEW_TRANSPORT_CONTRACT`
- `REVIEW_SANITIZED_ORDER_ENVELOPE`
- `REVIEW_TRANSPORT_RESULT`
- `REVIEW_NEXT_PACKET`

Every action reports:
- `owner_decision_required: True`
- `live_execution_allowed: False`
- `safe_action`
- `blocked_by`

## Blocker summary
Binding can return:
- `INCOMPLETE_INPUTS`
- `BLOCKED_BY_SENSITIVE_DATA`
- `BLOCKED_BY_LIVE_OR_MONEY_AUTHORITY`
- `BLOCKED_BY_RUNTIME_CONTEXT`
- `BLOCKED_BY_OWNER_APPROVAL`
- `BLOCKED_BY_DEMO_BOUNDARY`
- `BLOCKED_BY_ORDER_REQUEST`
- `BLOCKED_BY_RISK_ENVELOPE`
- `BLOCKED_BY_TRANSPORT_CONTRACT`

## Safety boundary
- `read_only_binding = True`
- `direct_broker_api_allowed = False`
- `broker_api_import_allowed = False`
- `network_call_allowed = False`
- `live_trading_allowed = False`
- `real_money_allowed = False`
- `money_movement_allowed = False`
- `bank_access_allowed = False`
- `credential_storage_allowed = False`
- `credential_read_allowed = False`
- `account_identifier_storage_allowed = False`
- `scheduler_created = False`
- `daemon_created = False`
- `webhook_created = False`
- `dashboard_runtime_created = False`

## Next packet
- Without transport: `AIOS_FOREX_OANDA_DEMO_OWNER_RUNTIME_TRANSPORT_PACKET_V1`
- With injected fake transport accepted: `AIOS_FOREX_OANDA_DEMO_POST_EXECUTION_REVIEW_V1`
