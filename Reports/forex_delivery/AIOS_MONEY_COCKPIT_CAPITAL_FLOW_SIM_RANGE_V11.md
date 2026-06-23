# AIOS Money Cockpit Capital Flow Simulation Range V11

## Objective
Create a display-only Money Cockpit with capital-flow policy visibility, sanitized bank-style balances, request previews, protected gates, and a 0.99-to-100000 simulation ladder without moving money.

## Money Cockpit Doctrine
- Money-relevant fields stay visible by default.
- Technical detail stays collapsed unless it blocks money, risk, broker readiness, uptime, or maintenance readiness.
- The cockpit can feel like a semi-live trading HUD, but it remains policy and simulation only.

## Capital Flow Doctrine
- AIOS must not become a custodian of money.
- AIOS does not move money from this policy engine or dashboard.
- Account aliases only: TRADING_FLOAT, RESERVE_ACCOUNT, PROFIT_VAULT, TAX_BUCKET, OPERATING_ACCOUNT, WITHDRAWAL_TARGET, RESUPPLY_SOURCE, COMPOUND_BUCKET.
- Real transfers require future connector proof and human approval.
- Instant withdrawal/deposit depends on supported future broker/bank/payment rails.
- This panel is policy and simulation only.

## Money Relevance Rule
Technical detail stays hidden unless it blocks profit, loss, risk, capital flow, withdrawal, resupply, compounding, broker readiness, execution, uptime, or maintenance readiness.

## Classifications
| Field | Value |
|---|---|
| CAPITAL_FLOW_STATUS | `CAPITAL_FLOW_DISPLAY_ONLY` |
| WITHDRAWAL_STATUS | `WITHDRAWAL_BLOCKED_BY_APPROVAL` |
| RESUPPLY_STATUS | `RESUPPLY_NOT_NEEDED` |
| COMPOUND_STATUS | `COMPOUND_TARGET_NOT_REACHED` |
| SWEEP_STATUS | `PROFIT_SWEEP_NOT_NEEDED` |
| TREASURY_AUTOMATION_STATUS | `TREASURY_AUTOMATION_POLICY_ONLY` |
| MONEY_RELEVANCE_STATUS | `MONEY_RELEVANT_VISIBLE` |

## Policy Inputs
| Field | Value |
|---|---|
| trading_balance | `10000.0` |
| reserve_balance | `5000.0` |
| profit_vault_balance | `0.0` |
| tax_bucket_balance | `0.0` |
| operating_account_balance | `2500.0` |
| equity | `10000.0` |
| daily_pl | `0.0` |
| realized_pl | `0.0` |
| drawdown | `0.0` |
| daily_loss_limit | `250.0` |
| available_risk_budget | `100.0` |
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
| account_aliases | `('TRADING_FLOAT', 'RESERVE_ACCOUNT', 'PROFIT_VAULT', 'TAX_BUCKET', 'OPERATING_ACCOUNT', 'WITHDRAWAL_TARGET', 'RESUPPLY_SOURCE', 'COMPOUND_BUCKET')` |

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
Dashboard wiring is fixture-backed and display-only. It renders hot money facts, capital policy state, draft request previews, and collapsed ladder detail only.

## Visible By Default
- `trading_float`
- `available_risk_budget`
- `daily_pl`
- `realized_pl`
- `equity`
- `drawdown`
- `daily_loss_left`
- `capital_cap`
- `sweep_amount`
- `resupply_need`
- `compounding_progress`
- `withdrawal_request_status`
- `broker_proof_status`
- `connector_proof_status`
- `transfer_approval_status`
- `next_money_action`

## Collapsed By Default
- `raw_evidence_paths`
- `legal_governance_detail`
- `validator_logs`
- `repo_noise`
- `css_build_diagnostics`
- `stale_reports`
- `technical_detail`

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
