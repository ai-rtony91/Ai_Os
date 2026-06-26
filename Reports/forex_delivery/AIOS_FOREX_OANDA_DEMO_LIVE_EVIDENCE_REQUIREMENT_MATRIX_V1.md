# AIOS Forex OANDA Demo Live Evidence Requirement Matrix V1

## Purpose

Build a deterministic, local-only live evidence requirement matrix that maps repeated OANDA demo expectancy proof into the remaining live evidence bundle checklist.

This is a preview matrix only. It does not approve live trading, does not call a broker, and does not place a trade.

No trade placed by this packet.

No broker call was made by this packet.

## Requirement IDs And Categories

| Requirement ID | Category | Evidence status |
| --- | --- | --- |
| `human_owner_live_exception_approval` | owner_approval | OWNER_ACTION_REQUIRED |
| `live_account_boundary_verified` | account_boundary | OWNER_ACTION_REQUIRED |
| `demo_account_boundary_verified` | account_boundary | OWNER_ACTION_REQUIRED |
| `credential_boundary_verified` | credential_boundary | OWNER_ACTION_REQUIRED |
| `secret_redaction_verified` | data_safety | OWNER_ACTION_REQUIRED |
| `account_id_redaction_verified` | data_safety | OWNER_ACTION_REQUIRED |
| `live_endpoint_denial_or_boundary_proof` | endpoint_boundary | OWNER_ACTION_REQUIRED |
| `broker_permissions_verified` | permission_boundary | OWNER_ACTION_REQUIRED |
| `max_loss_policy_verified` | risk_policy | OWNER_ACTION_REQUIRED |
| `position_size_policy_verified` | risk_policy | OWNER_ACTION_REQUIRED |
| `daily_loss_limit_verified` | risk_policy | OWNER_ACTION_REQUIRED |
| `kill_switch_verified` | abort_control | OWNER_ACTION_REQUIRED |
| `timeout_abort_verified` | abort_control | OWNER_ACTION_REQUIRED |
| `rollback_plan_verified` | recovery | OWNER_ACTION_REQUIRED |
| `final_disarm_plan_verified` | recovery | OWNER_ACTION_REQUIRED |
| `monitoring_plan_verified` | monitoring | OWNER_ACTION_REQUIRED |
| `audit_log_plan_verified` | audit | OWNER_ACTION_REQUIRED |
| `order_ticket_review_verified` | order_review | OWNER_ACTION_REQUIRED |
| `spread_market_hours_review_verified` | market_review | OWNER_ACTION_REQUIRED |
| `duplicate_order_guard_verified` | order_safety | OWNER_ACTION_REQUIRED |
| `read_only_reconciliation_verified` | reconciliation | OWNER_ACTION_REQUIRED |
| `post_trade_journal_plan_verified` | journal | OWNER_ACTION_REQUIRED |
| `reconciliation_plan_verified` | reconciliation | OWNER_ACTION_REQUIRED |
| `one_shot_only_scope_verified` | scope_control | OWNER_ACTION_REQUIRED |
| `no_compounding_scope_verified` | scope_control | OWNER_ACTION_REQUIRED |
| `no_bank_movement_scope_verified` | scope_control | OWNER_ACTION_REQUIRED |
| `no_autonomous_loop_scope_verified` | scope_control | OWNER_ACTION_REQUIRED |
| `evidence_bundle_owner_review_verified` | owner_review | OWNER_ACTION_REQUIRED |

## Evidence Statuses

- PRESENT
- MISSING
- BLOCKED
- OWNER_ACTION_REQUIRED

Unknown evidence statuses are normalized to BLOCKED by the gap mapper.

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
- live_micro_trade_exception_allowed: false
- live_evidence_bundle_approved: false

## Owner Warning

Do not execute unless Anthony explicitly approves.

## Live Gap Warning

Live evidence gap review only. Codex is not authorized to execute, call a broker, access credentials, place orders, or approve live trading.

## Next Safe Action

Use the matrix to classify which live evidence bundle items are PRESENT, MISSING, BLOCKED, or OWNER_ACTION_REQUIRED before any owner exception review.
