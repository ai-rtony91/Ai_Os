# AIOS Capital Flow Treasury Control Panel V10

## Objective
Create display-only capital-flow policy visibility, request previews, protected gates, and future connector boundaries without moving money.

## Capital Flow Doctrine
- AIOS must not become a custodian of money.
- AIOS does not move money from this policy engine or dashboard.
- Account aliases only: TRADING_FLOAT, RESERVE_ACCOUNT, TAX_BUCKET, PROFIT_VAULT, OPERATING_ACCOUNT.
- Real transfers require future connector proof and human approval.
- Instant withdrawal/deposit depends on supported future broker/bank/payment rails.

## Classifications
| Field | Value |
|---|---|
| CAPITAL_FLOW_STATUS | `CAPITAL_FLOW_DISPLAY_ONLY` |
| WITHDRAWAL_STATUS | `WITHDRAWAL_BLOCKED_BY_APPROVAL` |
| RESUPPLY_STATUS | `RESUPPLY_NOT_NEEDED` |
| COMPOUND_STATUS | `COMPOUND_TARGET_NOT_REACHED` |
| SWEEP_STATUS | `PROFIT_SWEEP_NOT_NEEDED` |
| TREASURY_AUTOMATION_STATUS | `TREASURY_AUTOMATION_POLICY_ONLY` |

## Policy Inputs
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

## Recommendations
- `HOLD`

## Protected Gates
| Field | Value |
|---|---|
| human_approval_status | `MISSING` |
| broker_proof_status | `MISSING` |
| bank_proof_status | `MISSING` |
| payment_rail_proof_status | `MISSING` |
| maintenance_window | `False` |
| emergency_freeze | `False` |
| daily_loss_lockout | `False` |
| sensitive_input_detected | `False` |
| real_money_movement_allowed | `False` |

## Dashboard Wiring
Dashboard wiring is fixture-backed and display-only. It renders capital policy state and draft request previews only.

## Display-Only Scope
- sanitized balances
- account aliases
- policy thresholds
- request previews
- protected-gate statuses

## Future Connector Proof Required
- broker proof
- bank proof
- payment rail proof
- transfer status proof

## Human Approval Required
Every future transfer must require explicit Human Owner approval before leaving draft preview.

## Safety Status
- broker status: not called
- bank status: not called
- payment processor status: not called
- credential status: not read
- account ID status: not read
- transfer status: no transfer executed
