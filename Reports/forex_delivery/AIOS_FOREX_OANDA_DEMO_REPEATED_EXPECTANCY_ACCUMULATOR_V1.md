# AIOS Forex OANDA Demo Repeated Expectancy Accumulator V1

## Purpose

Calculate repeated expectancy metrics from an accepted sanitized OANDA demo P/L sample.

No trade placed by this packet. No broker call was made by this packet.

## Metrics Calculated

- result count
- profit count
- loss count
- breakeven count
- win rate
- loss rate
- breakeven rate
- total realized P/L
- average realized P/L
- gross profit
- gross loss absolute value
- profit factor
- expectancy per trade
- total R
- average R
- best R
- worst R
- average win
- average loss absolute value
- max observed loss
- positive expectancy
- profitable sample
- loss-dominated sample

## Formulas

Expectancy per trade:

`total_realized_pl / result_count`

Profit factor:

`gross_profit / gross_loss_abs`

Win rate:

`profit_count / result_count`

R multiple aggregation:

`total_r = sum(realized_r_multiple)` and `average_r = total_r / result_count`

## Classification Rules

- Strong: positive expectancy, profit factor at or above strong threshold, sufficient strong sample size, and average R at or above strong threshold.
- Reviewable: positive expectancy with reviewable sample size, profit factor, and average R.
- Weak: non-negative but low-signal sample.
- Losing: negative expectancy or profit factor below 1 with losses present.
- Blocked: source sample intake is blocked.

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
