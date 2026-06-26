# AIOS Forex OANDA Demo Expectancy Sufficiency Gate V1

## Purpose

Decide whether accumulated OANDA demo repeated expectancy evidence is ready for owner proof review, needs more evidence, or must be rejected.

No trade placed by this packet. No broker call was made by this packet.

## Owner Proof Review Criteria

Owner proof review requires:

- sample size at or above the ready threshold.
- expectancy per trade greater than zero.
- profit factor at or above the ready threshold.
- average R at or above the ready threshold.
- win rate at or above the ready threshold.
- no unsafe or incomplete inputs.

## More-Evidence Criteria

A sample requires more evidence when the expectancy is non-negative but sample size, average R, win rate, or other signal remains below owner proof review threshold.

## Rejection Criteria

- Negative expectancy.
- Sufficient sample size with low profit factor.
- Unsafe or blocked input is not review-ready and must be repaired before repeated expectancy review.

## Live Authority Boundary

Repeated expectancy proof is not live execution authority. Live profitable execution remains blocked until a separate live evidence bundle and Human Owner-approved exception exist.

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
