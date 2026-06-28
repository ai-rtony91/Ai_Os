# AIOS Forex C1 Demo Order Intent Owner Approval Gate V1 Report

## Campaign Scope

This report applies the P6 C1 demo-order intent owner-approval gate for `c1-eur-buy` only. It consumes the P5 supervised demo-trade readiness output and prepares a review-only owner decision card.

This report does not execute trades, access broker/API systems, access credentials, access accounts, calculate live or account-specific position size, place demo orders, place live orders, close orders, move money, activate schedulers, activate daemons, activate webhooks, activate production, approve autonomous trading, or approve any demo-order placement.

## Trader Meaning

AIOS is preparing a review-only demo-order intent card for the EUR/USD buy setup so the owner can inspect the proposed trade requirements before any demo order is allowed.

## Source Evidence

- `automation/forex_engine/c1_supervised_demo_trade_readiness_review_v1.py`: Provides the authoritative P5 supervised demo-readiness evaluator consumed by this P6 owner-approval gate.
- `Reports/forex_delivery/AIOS_FOREX_C1_SUPERVISED_DEMO_TRADE_READINESS_REVIEW_V1.json`: Records P5 review status, P6 readiness, score, failed requirements, and next lane.
- `Reports/forex_delivery/AIOS_FOREX_C1_SUPERVISED_DEMO_TRADE_READINESS_REVIEW_V1_REPORT.md`: Explains the source-backed P5 decision and preserves the no demo-order or live-trading boundary.
- `Reports/forex_delivery/AIOS_FOREX_C1_SUPERVISED_DEMO_TRADE_READINESS_REVIEW_NEXT_ACTION_QUEUE_V1.md`: Routes the source-cleared candidate into P6 demo-order intent owner-approval gate only.
- `RISK_POLICY.md`: Defines the root safety boundary for trading, credentials, broker access, order action, and fail-closed behavior.

## P5 Entry Condition

- p5_review_status: `P5_SUPERVISED_DEMO_READINESS_PASSED_FOR_P6_OWNER_APPROVAL`
- p5_p6_readiness: `P6_READY`
- input_score: `100`
- input_status: `P6_READY`
- p6_entry_passed: `True`

- p5_review_status: `True`
- p6_readiness: `True`
- post_p5_score: `True`
- next_required_lane: `True`
- failed_requirements_empty: `True`
- sanitized_snapshot_required: `True`
- owner_approval_required: `True`
- demo_order_placement_blocked: `True`
- broker_api_blocked: `True`
- credential_access_blocked: `True`
- live_trading_blocked: `True`

## Demo Order Intent Card

| field | value |
|---|---|
| `candidate_id` | `c1-eur-buy` |
| `candidate_name` | `paper_long_run_supervisor_v2 LONG EURUSD` |
| `intended_instrument` | `EUR_USD` |
| `intended_side` | `BUY` |
| `order_type_status` | `OWNER_SELECTION_REQUIRED` |
| `units_formula_only` | `True` |
| `units_formula` | `units = risk_amount / stop_loss_value_per_unit` |
| `max_risk_per_trade_percent` | `0.25` |
| `max_daily_loss_percent` | `1.0` |
| `max_weekly_loss_percent` | `2.0` |
| `max_open_positions` | `1` |
| `max_orders_per_signal` | `1` |
| `stop_loss_required` | `True` |
| `take_profit_required` | `True` |
| `minimum_reward_to_risk` | `1.2` |
| `stop_loss_formula_required` | `True` |
| `take_profit_formula_required` | `True` |
| `sanitized_snapshot_required` | `True` |
| `owner_approval_required` | `True` |
| `owner_approval_status` | `OWNER_ACTION_REQUIRED` |
| `demo_order_placement_authorized` | `False` |
| `live_trading_blocked` | `True` |
| `broker_api_access_blocked` | `True` |
| `credential_access_blocked` | `True` |
| `money_movement_blocked` | `True` |
| `one_order_rule_verification_required` | `True` |
| `daily_stop_verification_required` | `True` |
| `weekly_stop_verification_required` | `True` |
| `kill_switch_verification_required` | `True` |
| `audit_artifacts_required` | `['P6 owner report', 'P6 JSON evidence', 'P6 next action queue', 'owner-supplied sanitized broker/account snapshot', 'owner approval decision record']` |
| `no_autonomy_approval` | `True` |

## Sanitized Snapshot Requirement

- sanitized_broker_account_snapshot_required: `True`
- required_before_account_specific_units: `True`
- collected_in_this_packet: `False`
- requires_sanitized_broker_account_snapshot: `True`
- purpose: Provide enough demo-account state for owner review without exposing secrets, credentials, account identifiers, broker order identifiers, or private execution payloads.
- allowed_snapshot_fields:
- demo-account marker
- sanitized equity value or bracket
- current open position count
- current same-signal order count
- daily realized loss percent
- weekly realized loss percent
- kill-switch state
- forbidden_snapshot_fields:
- API keys
- tokens
- passwords
- broker credentials
- account identifiers
- broker order identifiers
- raw live account data
- private execution payloads
- status: `OWNER_SUPPLIED_SANITIZED_SNAPSHOT_REQUIRED`

## Owner Approval Requirement

- owner_approval_required: `True`
- owner_approval_status: `OWNER_ACTION_REQUIRED`
- approved_by_this_packet: `False`
- approval_granted: `False`
- required_before_any_demo_order: `True`
- demo_order_placement_authorized: `False`
- approval_scope: P6 demo-order intent owner-approval gate only
- required_decision_fields:
- explicit owner approval decision
- intended instrument confirmation
- intended side confirmation
- order type selection
- units formula review
- stop loss review
- take profit review
- reward-to-risk review
- one-order rule verification
- daily-stop verification
- weekly-stop verification
- kill-switch verification

## Pre-Order Safety Checks

- status: `OWNER_ACTION_REQUIRED`
- demo_order_placement_authorized: `False`
- broker_api_access_blocked: `True`
- credential_access_blocked: `True`
- live_trading_blocked: `True`
- money_movement_blocked: `True`
- no_autonomy_approval: `True`
- checks_required_before_any_later_demo_order:
- sanitized broker/account snapshot supplied by owner
- explicit owner approval decision recorded
- order type selected by owner
- units formula reviewed without account-specific sizing in this packet
- stop loss formula reviewed
- take profit formula reviewed
- reward-to-risk at or above minimum
- one-order rule verified
- daily-stop state verified
- weekly-stop state verified
- kill-switch state verified

## One-Order Verification

- one_order_rule_verification_required: `True`
- max_open_positions: `1`
- max_orders_per_signal: `1`
- no_retry_loop: `True`
- owner_snapshot_required: `True`
- rule: Owner-supplied sanitized evidence must show no more than one open position and no more than one order for the same signal before any later demo-order authority can be considered.

## TP/SL Verification

- stop_loss_required: `True`
- take_profit_required: `True`
- minimum_reward_to_risk: `1.2`
- stop_loss_formula_required: `True`
- take_profit_formula_required: `True`
- verification_required: `True`
- rule: Owner review must confirm stop loss, take profit, and at least 1.20 reward-to-risk before any later demo-order authority can be considered.

## Stop Rule Verification

- daily_stop_verification_required: `True`
- weekly_stop_verification_required: `True`
- max_daily_loss_percent: `1.0`
- max_weekly_loss_percent: `2.0`
- owner_snapshot_required: `True`
- rule: Owner-supplied sanitized evidence must show daily and weekly loss state remains inside the defined limits before any later demo-order authority can be considered.

## Kill Switch Verification

- kill_switch_verification_required: `True`
- required_state: active and untriggered before owner approval can continue
- owner_snapshot_required: `True`
- triggers:
- missing sanitized broker/account snapshot
- missing owner approval
- missing order type selection
- missing stop loss
- missing take profit
- reward-to-risk below 1.20
- risk per trade above 0.25 percent
- daily loss at or above 1.00 percent
- weekly loss at or above 2.00 percent
- more than one open position
- more than one order for the same signal
- credential, account, broker/API, order, scheduler, daemon, webhook, production, or autonomy path detected
- rule: Any trigger keeps the owner gate from advancing until repair evidence is generated and the relevant review lane is rerun.

## Audit Requirements

- audit_report_required: `True`
- manual_owner_review_required: `True`
- required_artifacts:
- P5 supervised demo-trade readiness JSON
- P5 supervised demo-trade readiness owner report
- P5 next action queue
- P6 owner report
- P6 JSON evidence
- P6 next action queue
- owner-supplied sanitized broker/account snapshot
- owner approval decision record
- must_exclude:
- secrets
- credentials
- account identifiers
- broker order identifiers
- private execution payloads

## Owner Action Status

`OWNER_ACTION_REQUIRED`

## Next Required Lane

`P6A_OWNER_SUPPLY_SANITIZED_SNAPSHOT_AND_APPROVAL_DECISION`

## What This Completes

- creates the P6 review-only demo-order intent card for `c1-eur-buy`
- defines the sanitized snapshot requirement and owner approval requirement
- preserves the one-order, TP/SL, stop-rule, kill-switch, audit, broker/API, credential, live-trading, money-movement, and autonomy blocks

## What This Does Not Approve

- demo-order placement
- live trading
- broker/API access
- credential access
- account access
- order placement
- order closure
- money movement
- scheduler activation
- daemon activation
- webhook activation
- production activation
- autonomous trading
- claiming owner approval has been granted
- claiming demo-order placement authority
- claiming live trading authority
- claiming 22/6 autonomy readiness
- claiming vacation/luxury mode as active
- claiming 100-120 percent return as verified

## Final Owner Sentence

AIOS Forex P6 C1 demo-order intent owner-approval gate is complete: c1-eur-buy has a review-only demo-order intent card prepared for owner decision, while demo-order placement, live trading, broker/API, credentials, money movement, 22/6 autonomy, vacation/luxury mode, and 100-120 percent return claims remain blocked until separately proven and approved.
