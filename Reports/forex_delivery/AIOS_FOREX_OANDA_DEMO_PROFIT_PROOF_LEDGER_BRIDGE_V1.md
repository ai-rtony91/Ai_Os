# AIOS Forex OANDA Demo Profit Proof Ledger Bridge V1

## Purpose

Bridge one accepted sanitized read-only OANDA demo P/L result into local proof-routing previews.

This bridge produces preview objects only. It does not mutate an existing ledger file, hidden store, broker system, or external service.

No trade placed by this packet. No broker call was made by this packet.

## Routing Targets

- Profit Proof Ledger
- Strategy Proof Engine
- Expectancy Strength Router
- Demo Review Engine
- Strategy Promotion Router
- Real Evidence Depth Engine
- Result To Bucket And Next Allocation
- Loss To Next Profit Candidate Gate when the result bucket is `LOSS`

## Ledger Entry Preview

The ledger preview includes strategy, candidate, instrument, direction, result bucket, planned risk, realized P/L, realized R multiple, intake classification, quality classification, and `preview_only: true`.

## Expectancy Sample Preview

The expectancy preview marks the evidence as a single result only and sets `can_claim_repeated_expectancy: false`.

## Evidence Depth Preview

The evidence depth preview records the sanitized read-only result type, read-only capture status, broker reconciliation status, and quality classification.

## Bucket Recommendation

- Profit: `PROFIT_SAMPLE_ACCEPTED_FOR_REVIEW`
- Loss: `LOSS_SAMPLE_ACCEPTED_FOR_REVIEW`
- Breakeven: `BREAKEVEN_SAMPLE_ACCEPTED_FOR_REVIEW`
- Blocked result: `NO_BUCKET_RECOMMENDATION_BLOCKED`

## Next Allocation Hint

- Profit: add to repeated expectancy sample before any live review.
- Loss: route to loss review / next profit candidate gate.
- Breakeven: add to evidence depth but do not strengthen expectancy alone.

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
