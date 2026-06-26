# AIOS Forex OANDA Demo Read-Only P/L Result Intake V1

## Purpose

Provide a local-only intake contract for one sanitized OANDA demo filled-trade P/L result.

This packet does not execute trades. No trade placed by this packet. No broker call was made by this packet.

## Sanitized Read-Only Evidence Contract

Accepted evidence must be sanitized, demo-only, broker-reconciled, and read-only captured. It must not include raw broker payloads, account IDs, credentials, broker order IDs, or private account data.

Required safety warning:

`Read-only P/L evidence intake only. Codex is not authorized to execute, call a broker, access credentials, or place orders.`

## Accepted Fields

- broker: `OANDA_DEMO`
- environment: `DEMO`
- trade_reference: sanitized local reference only
- strategy_id
- candidate_id
- instrument
- direction
- planned_units and actual_units
- planned_entry and actual_entry
- planned_stop_loss and actual_stop_loss
- planned_take_profit and actual_take_profit
- planned_risk
- realized_pl
- result
- open_time and close_time
- broker_reconciled
- read_only_capture
- notes

## Blocked Unsafe Fields

- raw_payload_included
- account_id_included
- credential_included
- broker_order_id_included
- private_account_data_included
- broker value other than `OANDA_DEMO`
- environment value other than `DEMO`
- read_only_capture false

## Profit/Loss/Breakeven Classification Rules

- `PROFIT`: realized P/L greater than zero.
- `LOSS`: realized P/L less than zero.
- `BREAKEVEN`: realized P/L equal to zero.
- `INCOMPLETE`: missing P/L, result text, instrument, direction, positive planned risk, positive actual units, or timestamps.

The result string is normalized from realized P/L. One result is a proof-intake object, not a repeated expectancy claim.

## Permissions False

- demo_execution_allowed: false
- broker_action_allowed: false
- real_money_allowed: false
- compounding_allowed: false
- bank_movement_allowed: false
- live_trading_allowed: false
- credential_access_allowed: false
- account_id_persistence_allowed: false
- autonomous_execution_allowed: false
- scheduler_allowed: false
- daemon_allowed: false
- webhook_allowed: false
