# AIOS Forex OANDA Demo P/L Result Quality Gate V1

## Purpose

Evaluate whether an accepted sanitized read-only OANDA demo P/L result is proof-ready, review-ready, or blocked.

This packet does not execute trades. No trade placed by this packet. No broker call was made by this packet.

## Quality Classification Rules

- `OANDA_DEMO_PL_RESULT_QUALITY_PROOF_READY`: safe accepted profit, reconciled and sanitized, with absolute realized R multiple at or above the configured threshold.
- `OANDA_DEMO_PL_RESULT_QUALITY_REVIEW_READY`: accepted loss, breakeven, or non-strict low-signal profit that can be reviewed but not used alone to claim repeated expectancy.
- `OANDA_DEMO_PL_RESULT_QUALITY_BLOCKED_INCOMPLETE`: intake result is incomplete or unreconciled.
- `OANDA_DEMO_PL_RESULT_QUALITY_BLOCKED_UNSAFE`: intake result is unsafe or not sanitized.
- `OANDA_DEMO_PL_RESULT_QUALITY_BLOCKED_LOW_SIGNAL`: strict low-signal handling blocks proof routing.

## Proof-Ready vs Review-Ready

Proof-ready means the first result may be routed to a local proof preview for owner review. It does not mean profitable trading is proven.

Review-ready means the result may be inspected as evidence, but proof routing is not allowed as a profit claim.

## Realized R Multiple

Realized R multiple is calculated as:

`realized_pl / planned_risk`

The deterministic profit sample produces `0.6000R` from realized P/L `1.20` and planned risk `2.00`.

## Low Signal Handling

Profit below the configured minimum absolute R threshold is review-ready by default. Strict mode blocks it as low signal.

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
