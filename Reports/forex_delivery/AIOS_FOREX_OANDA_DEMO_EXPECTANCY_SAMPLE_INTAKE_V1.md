# AIOS Forex OANDA Demo Expectancy Sample Intake V1

## Purpose

Accept multiple sanitized read-only OANDA demo P/L result-intake objects and validate that they can form one coherent repeated expectancy sample.

No trade placed by this packet. No broker call was made by this packet.

## Accepted Sample Contract

- Each item must be an accepted read-only P/L result-intake object.
- Each item must be sanitized, reconciled, demo-only, and read-only captured.
- Each item must keep all protected permission flags false.
- Each item must include result bucket, realized P/L, planned risk, realized R multiple, and close time.
- The module preserves chronological order by close time where possible.
- The module produces preview-only local output and never mutates an existing ledger.

## Blocked Sample Conditions

- Empty sample.
- Unsafe result.
- Incomplete result.
- Not-sanitized result.
- Unreconciled result.
- Non-demo result.
- Broker-action-enabled result.
- Missing close time.
- Planned risk less than or equal to zero.

## Strategy/Candidate/Instrument Consistency Rules

Mixed `strategy_id`, `candidate_id`, or `instrument` is blocked by default. A caller may explicitly allow each mixed field by config when a review lane requires that broader sample.

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
