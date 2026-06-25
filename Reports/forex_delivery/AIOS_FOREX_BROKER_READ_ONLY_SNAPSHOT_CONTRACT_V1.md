# AIOS Forex Broker Read-Only Snapshot Contract V1

## Purpose

The broker read-only snapshot contract defines the sanitized shape AIOS can review before a supervised demo trade package is prepared.

No trade was placed.

## Sanitized Broker Snapshot Fields

- account_present
- account_reference
- balance_present
- balance
- margin_available_present
- margin_available
- open_trades_present
- open_trades
- open_positions_present
- open_positions
- pending_orders_present
- pending_orders
- last_transaction_id_present
- last_transaction_id
- market_hours_open
- instrument_tradeable
- spread_present
- spread
- timestamp_present
- read_only_reconciled
- no_unknown_open_exposure
- source
- sanitized

## Read-Only Boundary

The contract accepts only local sanitized review data. It does not call a broker, connect to OANDA, use credentials, or place orders.

## Account Reference Rule

Only the placeholder value `DEMO_ACCOUNT_REFERENCE_PRESENT` is accepted. Real account identifiers must not be requested, stored, printed, or persisted.

## Blocked Conditions

- Missing account placeholder
- Missing balance
- Missing margin
- Unknown open exposure
- Market closed
- Instrument not tradeable
- Missing spread
- Stale or unreconciled snapshot
- Unsanitized snapshot

## Next Safe Action

Use this contract only to validate a sanitized read-only demo snapshot before account readiness review.
