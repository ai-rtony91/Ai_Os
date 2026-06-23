# AIOS Capital Flow Policy Simulation V10

## Sample Sanitized Input
| Field | Value |
|---|---|
| trading_balance | `10000.0` |
| reserve_balance | `5000.0` |
| profit_vault_balance | `0.0` |
| tax_bucket_balance | `0.0` |
| operating_account_balance | `2500.0` |
| minimum_trading_float | `8000.0` |
| maximum_trading_float | `12000.0` |
| sweep_threshold | `1000.0` |
| resupply_threshold | `8000.0` |
| compounding_threshold | `2000.0` |
| compounding_target | `15000.0` |
| max_withdrawal_per_event | `2500.0` |
| max_deposit_per_event | `2500.0` |
| cooldown_minutes | `60` |
| maintenance_window | `False` |
| emergency_freeze | `False` |
| daily_loss_lockout | `False` |
| broker_proof_status | `MISSING` |
| bank_proof_status | `MISSING` |
| payment_rail_proof_status | `MISSING` |
| live_trading_lock_status | `LIVE_LOCKED` |
| human_approval_status | `MISSING` |
| last_transfer_request_timestamp | `UNKNOWN` |
| account_aliases | `('TRADING_FLOAT', 'RESERVE_ACCOUNT', 'TAX_BUCKET', 'PROFIT_VAULT', 'OPERATING_ACCOUNT')` |

## Recommendation Output
- `HOLD`

## Cap Scenario
When trading float exceeds the maximum cap, the engine drafts a profit sweep preview capped by max withdrawal per event.

## Resupply Scenario
When trading float falls below the floor or resupply threshold, the engine drafts a resupply preview capped by max deposit per event.

## Compound Scenario
When profit vault reaches the compounding threshold and trading float is below target, the engine drafts a compound-in-place preview.

## Sweep Scenario
Profit sweep previews route from TRADING_FLOAT to PROFIT_VAULT by alias only.

## Risk Freeze Scenario
Emergency freeze or daily loss lockout produces FREEZE_CAPITAL_FLOW and blocks draft escalation.

## Maintenance-Window Scenario
Treasury actions outside a maintenance window are marked NEEDS_MAINTENANCE_WINDOW.

## Approval-Blocked Scenario
Missing human approval keeps recommendations in draft preview and blocks transfer execution.
