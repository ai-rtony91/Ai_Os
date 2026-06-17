# AIOS Forex Builder Broker-Paper Demo Adapter

This packet implements the paper/demo broker adapter required after the broker-paper adapter plan approval gate.

The adapter is deterministic and in-memory. It does not import a broker SDK, connect to a real broker, read credentials, read `.env`, call a network API, route a real order, place broker-paper orders with an external broker, or place live orders.

## Contracts Added

- Broker adapter interface
- Paper/demo connection contract
- Paper/demo authentication contract
- Local market-data contract
- Sanitized paper account-state contract
- Paper order-state contract
- Simulated fill contract
- Paper position-state contract
- Paper position-close contract
- Sanitized evidence contract

## Adapter Capabilities

The adapter supports:

- `connect`
- `authenticate`
- `get_market_data`
- `get_account_state`
- `create_order`
- `get_position_state`
- `close_position`
- `build_evidence_bundle`

Unsupported broker actions fail closed through `UNSUPPORTED_ACTION_BLOCKED`.

Live execution attempts return `LIVE_EXECUTION_BLOCKED`.

## Safety Boundary

The adapter always keeps these fields false:

- `broker_sdk_allowed`
- `network_api_allowed`
- `credentials_allowed`
- `env_secret_read_allowed`
- `broker_paper_orders_allowed`
- `live_orders_allowed`
- `live_execution_allowed`
- `live_ready`
- `live_trade_ready`
- `real_order_ready`
- `would_place_order`
- `order_placed`
- `broker_request_sent`
- `network_used`
- `credentials_used`

The adapter rejects payloads containing credential, token, key, password, secret, account identifier, broker order identifier, or raw live payload fields.

## Governed Flow Wiring

`src/forex_delivery/governed_readiness.py` now uses the paper/demo adapter for:

- broker connect
- authentication
- market data
- account state
- paper order simulation
- simulated fill verification
- position state
- position close
- adapter evidence

The governed flow still returns a sanitized paper-only final report and still blocks live arming unless the Human Owner activates the Single Live Micro-Trade Exception under `RISK_POLICY.md`.

## Stop Point

Stop after paper/demo broker adapter validation. Live broker integration, broker credentials, network/API execution, real-money routing, and live orders remain blocked.
