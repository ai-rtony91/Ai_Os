# AIOS Forex C1 Risk Position Sizing Review V1 Report

## Campaign Scope

This report applies the P4 C1 risk and position-sizing review lane for `c1-eur-buy` only. It consumes the P3 walk-forward/OOS proof output and defines conservative review-only risk rules for a later P5 supervised demo-trade readiness review.

This report does not execute trades, access broker/API systems, access credentials, access accounts, calculate real order size from live data, place orders, close orders, move money, activate schedulers, activate daemons, activate webhooks, activate production, or approve autonomous trading.

## Trader Meaning

AIOS is defining how much the proven EUR/USD buy setup is allowed to risk, how position size must be calculated, and which stop rules must protect the account before any supervised demo-trade readiness review.

## Source Evidence

- `automation/forex_engine/c1_walk_forward_oos_proof_v1.py`: Provides the authoritative P3 proof evaluator consumed by this P4 risk review.
- `Reports/forex_delivery/AIOS_FOREX_C1_WALK_FORWARD_OOS_PROOF_V1.json`: Records P3 proof status, P4 readiness, score, failed requirements, and next lane.
- `Reports/forex_delivery/AIOS_FOREX_C1_WALK_FORWARD_OOS_PROOF_V1_REPORT.md`: Explains the source-backed P3 decision and preserves the no demo or live trading boundary.
- `Reports/forex_delivery/AIOS_FOREX_C1_WALK_FORWARD_OOS_PROOF_NEXT_ACTION_QUEUE_V1.md`: Routes the source-cleared candidate into P4 risk and position-sizing review only.

## P3 Entry Condition

- p3_proof_status: `P3_PROOF_PASSED_FOR_P4_REVIEW`
- p3_p4_readiness: `P4_READY`
- input_score: `100`
- input_status: `P4_READY`
- p4_entry_passed: `True`

## P4 Risk Policy

| rule | value |
|---|---|
| `max_risk_per_trade_percent` | `0.25` |
| `max_daily_loss_percent` | `1.0` |
| `max_weekly_loss_percent` | `2.0` |
| `max_consecutive_losses` | `3` |
| `max_open_positions` | `1` |
| `max_orders_per_signal` | `1` |
| `stop_loss_required` | `True` |
| `take_profit_required` | `True` |
| `minimum_reward_to_risk` | `1.2` |
| `max_strategy_drawdown_percent` | `5.0` |
| `one_order_rule` | `True` |
| `daily_stop_rule` | `True` |
| `weekly_stop_rule` | `True` |

## Position-Sizing Formula

- formula_only: `True`
- risk_amount: `risk_amount = account_equity * (max_risk_per_trade_percent / 100)`
- position_size: `position_size = risk_amount / stop_loss_value_per_unit`
- required_inputs: `['account_equity', 'max_risk_per_trade_percent', 'stop_loss_value_per_unit']`
- blocked_inputs: `['real account equity in this P4 review', 'broker balances', 'broker credentials', 'live prices', 'account identifiers']`
- real_sizing_block: `Real sizing is blocked until a later supervised demo-readiness review supplies a sanitized broker/account snapshot.`

## Max Loss Rules

- max_risk_per_trade_percent: `0.25`
- max_daily_loss_percent: `1.0`
- max_weekly_loss_percent: `2.0`
- max_consecutive_losses: `3`
- max_strategy_drawdown_percent: `5.0`
- rule: Loss exposure must stay inside the per-trade, daily, weekly, consecutive-loss, and strategy-drawdown gates before P5 can review supervised demo-trade readiness.

## Daily Stop Rules

- daily_stop_rule: `True`
- max_daily_loss_percent: `1.0`
- trigger: Stop new orders for the review day if realized loss plus open risk reaches 1.00 percent of account equity.
- reset_condition: Owner-reviewed next-session reset is required.
- calculation_dependency: Requires a sanitized broker/account snapshot in P5 before account-specific calculation.

## One-Order Rules

- one_order_rule: `True`
- max_open_positions: `1`
- max_orders_per_signal: `1`
- no_retry_loop: `True`
- rule: The C1 signal may have no more than one open position and no more than one order per signal during later supervised review.

## TP/SL Guardrails

- stop_loss_required: `True`
- take_profit_required: `True`
- minimum_reward_to_risk: `1.2`
- rule: Every later supervised demo-trade review candidate must include a stop loss, take profit, and at least 1.20 reward-to-risk before any order approval can be considered.

## Kill Switch Rules

- kill_switch_required: `True`
- triggers:
- missing stop loss
- missing take profit
- risk per trade above 0.25 percent
- daily loss at or above 1.00 percent
- weekly loss at or above 2.00 percent
- three consecutive losses
- more than one open position
- more than one order for the same signal
- strategy drawdown above 5.00 percent
- broker/account dependency requested before sanitized P5 snapshot
- credential, account, broker/API, order, scheduler, daemon, webhook, production, or autonomy path detected
- rule: Any trigger blocks progression until the issue is reviewed and the P4 or P5 evidence is rerun.

## Broker Account Dependency Block

- blocked: `True`
- reason: This P4 review defines formulas and guardrails only; it must not read credentials, balances, account identifiers, broker data, or live prices.
- p5_requirement: A later supervised demo-readiness review must supply a sanitized broker/account snapshot before any real position size can be calculated.

## P5 Readiness Decision

- p4_review_status: `P4_RISK_POSITION_SIZING_PASSED_FOR_P5_REVIEW`
- p5_readiness: `P5_READY`
- post_p4_score: `100`
- post_p4_status: `P5_READY`
- passed_requirements: `['p3_entry_condition', 'required_risk_rules_present', 'conservative_defaults', 'formula_only_position_sizing', 'broker_account_dependency_block', 'no_demo_live_approval']`
- failed_requirements: `[]`

## Next Required Lane

`P5_SUPERVISED_DEMO_TRADE_READINESS_REVIEW`

## What This Completes

- completes P4 risk and position-sizing review for `c1-eur-buy`
- defines the conservative risk policy, max loss gates, daily stop, one-order rule, TP/SL guardrails, position-sizing formula, broker/account dependency block, and kill-switch triggers
- decides whether the candidate can move to P5 supervised demo-trade readiness review only

## What This Does Not Approve

- broker/API access
- credentials
- account access
- demo trading without later evidence gate
- live trading
- order placement
- order closure
- money movement
- scheduler activation
- daemon activation
- webhook activation
- production activation
- autonomous trading
- claiming 22/6 autonomy readiness
- claiming vacation/luxury mode as active
- claiming 100-120 percent return as verified

## Final Owner Sentence

AIOS Forex P4 C1 risk and position-sizing review is complete: c1-eur-buy is source-cleared for P5 supervised demo-trade readiness review only, while demo trading, live trading, broker/API, credentials, money movement, 22/6 autonomy, vacation/luxury mode, and 100-120 percent return claims remain blocked until separately proven and approved.
