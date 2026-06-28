# AIOS Forex C1 Demo Order Intent Final Review Card V1 Report

## Campaign Scope

This report applies the P6D C1 demo-order intent final review card for `c1-eur-buy` only. It consumes the P6C owner snapshot approval validation gate and creates review-only evidence for later mock/dry-run rehearsal routing.

This report does not collect secrets, read credentials, access accounts, access brokers, calculate live or account-specific position size, place demo orders, place live orders, close orders, move money, activate schedulers, activate daemons, activate webhooks, activate production, or authorize autonomous trading.

## Trader Meaning

AIOS is preparing the final review-only demo-order intent card for the EUR/USD buy setup, readying it for mock/dry-run rehearsal only after owner input validates cleanly.

## P6C Validation Status

- p6c_validation_status: `P6C_VALIDATION_BLOCKED_OWNER_INPUT_REQUIRED`
- p6c_owner_decision_status: `OWNER_DECISION_NOT_SUPPLIED`

## Final Demo Intent Review Card

- final review card is blocked until owner input validates through P6C

## Risk Limits

| field | value |
|---|---|
| `max_risk_per_trade_percent` | `0.25` |
| `max_daily_loss_percent` | `1.0` |
| `max_weekly_loss_percent` | `2.0` |
| `max_open_positions` | `1` |
| `max_orders_per_signal` | `1` |
| `minimum_reward_to_risk` | `1.2` |

## Safety Verifications

| field | value |
|---|---|
| `stop_loss_required` | `True` |
| `take_profit_required` | `True` |
| `one_order_rule_verified` | `False` |
| `daily_stop_verified` | `False` |
| `weekly_stop_verified` | `False` |
| `kill_switch_verified` | `False` |
| `audit_record_required` | `True` |

## Blocked Actions

- demo-order placement authorization
- live trading
- broker/API access
- credential access
- account access
- order-placement execution
- order closure
- money movement
- scheduler activation
- daemon activation
- webhook activation
- production activation
- autonomous trading
- claiming owner approval as supplied by automation
- claiming demo-order authority
- claiming live trading authority
- claiming 22/6 autonomy readiness
- claiming vacation/luxury mode as active
- claiming 100-120 percent return evidence

## Final Review Status

- p6d_final_review_status: `P6D_FINAL_REVIEW_BLOCKED_OWNER_INPUT_REQUIRED`
- final_review_status: `NOT_READY`
- post_p6d_score: `100`
- demo_order_placement_authorized: `False`

## Next Required Lane

`P6B_OWNER_SUPPLY_SANITIZED_SNAPSHOT_AND_APPROVAL_INPUT`

## What This Completes

- creates the deterministic P6D final review-card gate
- routes only validated approve-intent input to P7 mock/dry-run rehearsal
- keeps demo-order placement, live-trading, broker/API, credential, money-movement, and autonomy blocks active

## What This Does Not Approve

- demo-order placement authorization
- live trading
- broker/API access
- credential access
- account access
- order-placement execution
- order closure
- money movement
- scheduler activation
- daemon activation
- webhook activation
- production activation
- autonomous trading
- claiming owner approval as supplied by automation
- claiming demo-order authority
- claiming live trading authority
- claiming 22/6 autonomy readiness
- claiming vacation/luxury mode as active
- claiming 100-120 percent return evidence

## Final Owner Sentence

AIOS Forex P6D C1 final review card is blocked until sanitized owner input validates through P6C; demo-order placement, live trading, broker/API, credentials, money movement, and autonomy remain blocked.
