# AIOS Demo Connector Read-Only Contract

## Purpose

`automation/forex_engine/demo_connector_readonly.py` validates sanitized demo snapshots before downstream AIOS forex stages consume them.

It does not connect to brokers, submit network traffic, resolve credentials, or place orders.

## Contract Inputs

- Snapshot payload fields handled in normalized form:
  - `mode` (`PAPER_ONLY_COMPATIBLE` or `DEMO_READONLY`)
  - `balance_is_present`
  - `currency`
  - `instruments`
  - `prices`
  - `positions_summary`
  - `last_read_timestamp`
  - `stale`
  - `blocked_reasons`

## Allowed Output Shape

- `allowed`
- `decision`
- `blocked_reason`
- `blocked_reasons`
- `warnings`
- `paper_only`
- `mode`
- `demo_readonly`
- `account_summary`
- `price_summary`
- `position_summary`
- `data_age_seconds`
- `fresh`
- `safety`
- `next_safe_action`
- `metadata`

## Safety requirements

- Fixed safety envelope in every response:
  - `paper_only: True`
  - `demo_readonly: True`
  - `broker_write: False`
  - `live_trading: False`
  - `credentials: False`
  - `real_orders: False`
  - `network_submit: False`

## Rejection policy

The snapshot is rejected if it indicates any of the following:

- `account_identifier_detected`
- `runtime_material_present`
- `live_control_enabled`
- `broker_write_enabled`
- `order_submission_enabled`
- `network_submission_enabled`
- stale demo data
- unsupported mode

When rejected, `decision` is `blocked`, `allowed` is false, and `next_safe_action` requests a sanitized fresh read-only snapshot.

## Normalization behavior

- Balances are read as read-only scalar values.
- Prices are normalized into float bid/ask/mid values for deterministic downstream use.
- Positions are summarized to counts and symbol lists.
- Missing balance information is surfaced as warning `missing_balance`.
