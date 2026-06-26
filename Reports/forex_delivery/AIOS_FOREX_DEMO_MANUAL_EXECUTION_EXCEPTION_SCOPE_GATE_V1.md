# AIOS Forex Demo Manual Execution Exception Scope Gate V1

## Purpose

The Demo Manual Execution Exception Scope Gate V1 validates whether a local manual execution exception request is scoped only to Anthony's manual owner review. It does not approve Codex execution, broker action, credential access, account identifier use, live trading, real money, compounding, or bank movement.

No broker call was made. No trade placed.

## Exact Exception Phrase

`I, Anthony, request manual review of this supervised demo execution exception packet only. I understand Codex is not authorized to execute, call a broker, or place orders.`

## Why It Is Manual-Review-Only

The phrase can only make a local exception packet review-ready for Anthony. It does not authorize Codex to execute, call a broker, access credentials, persist account identifiers, or place orders.

## Forbidden Scopes

- Codex execution authority
- AI execution authority
- Bot execution authority
- Broker action authority
- OANDA action authority
- Credential use
- Account ID use or persistence
- Live trading
- Real money
- Compounding
- Bank movement

## Blocked Protected Actions

- Demo execution
- Broker action
- Credential access
- Account ID persistence
- Live trading
- Real money
- Compounding
- Bank movement

## Permission Status

All protected permissions remain false:

- `demo_execution_allowed`: false
- `broker_action_allowed`: false
- `real_money_allowed`: false
- `compounding_allowed`: false
- `bank_movement_allowed`: false
- `live_trading_allowed`: false
- `credential_access_allowed`: false
- `account_id_persistence_allowed`: false

## Next Safe Action

Anthony may review the exception scope manually. Codex must not execute, call a broker, request credentials, request account IDs, or place orders.
