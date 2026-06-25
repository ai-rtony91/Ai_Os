# AIOS Forex Sanitized Broker Snapshot Intake V1

## Purpose

This module accepts a sanitized, local-only broker snapshot supplied as a Python mapping or JSON string. It rejects unsafe input before normalizing the snapshot into the landed `broker_read_only_snapshot_contract_v1` shape.

No broker call was made. No trade was placed.

## Accepted Sanitized Fields

- `account_present`
- `account_reference`
- `balance_present`
- `balance`
- `margin_available_present`
- `margin_available`
- `open_trades_present`
- `open_trades`
- `open_positions_present`
- `open_positions`
- `pending_orders_present`
- `pending_orders`
- `last_transaction_id_present`
- `last_transaction_id`
- `market_hours_open`
- `instrument_tradeable`
- `spread_present`
- `spread`
- `timestamp_present`
- `read_only_reconciled`
- `no_unknown_open_exposure`
- `source`
- `sanitized`

## Forbidden Input Types

- Account identifiers or account-number-looking values.
- API keys, tokens, authorization headers, passwords, or credential-shaped fields.
- Raw broker responses, raw payloads, request bodies, or response bodies.
- Live endpoint references.
- Hints that account identifiers or credentials should be stored, cached, retained, persisted, or written.

## Redaction Guard

`sanitized_broker_snapshot_redaction_guard_v1.py` runs before intake normalization. If the guard detects unsafe input, the intake returns `SANITIZED_BROKER_SNAPSHOT_INTAKE_BLOCKED_REDACTION_GUARD` and does not create a normalized broker snapshot.

## Account ID Rule

Only `DEMO_ACCOUNT_REFERENCE_PRESENT` is allowed for the account reference. Real account IDs, account numbers, and account-looking values are blocked and are not shown in previews.

## No Credential Storage

The intake module does not read `.env`, does not request credentials, does not store credentials, and does not persist account identifiers.

## No Broker Calls

The intake module has no broker transport, network client, runtime credential path, or execution path.

## No Trade Placed

This is a local review input path only. No trade was placed.
