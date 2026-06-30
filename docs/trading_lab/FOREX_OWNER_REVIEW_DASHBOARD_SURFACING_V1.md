# AI_OS Forex Owner-Review Dashboard Surfacing V1

## Purpose

This packet builds a **read-only dashboard projection** from already-sanitized upstream inputs:

- `owner_review_capital_surface`
- `remaining_work_closure_index`

It does not start runtime services, daemons, schedulers, webhooks, broker calls, bank access, or any money movement.

## Inputs

- `owner_review_capital_surface`
- `remaining_work_closure_index`
- `as_of_date`
- `owner_name`
- `dashboard_context`
- `display_preferences`

## Dashboard Cards

The projection always emits these card IDs:

- `OWNER_REVIEW_STATUS`
- `CAPITAL_BUCKETS`
- `RAILS`
- `WITHDRAWAL_CADENCE`
- `WITHDRAWAL_PLAN`
- `OANDA_FUNDING`
- `BIG_WINNER_WATCHTOWER`
- `REMAINING_WORK`
- `NEXT_PACKET`
- `SAFETY_BOUNDARY`

Each card includes:

- `card_id`
- `title`
- `status`
- `priority`
- `owner_decision_required`
- `execution_allowed`
- `summary`
- `blockers`
- `safe_next_action`
- `display_group`
- `sort_order`

## Dashboard Summary

Output `dashboard_summary` includes:

- `headline_status`
- `owner_name`
- `ready_card_count`
- `blocked_card_count`
- `watchlist_card_count`
- `incomplete_card_count`
- `top_blockers`
- `next_best_packet`
- `safe_manual_next_action`
- `last_updated_source`

## Owner Action Queue

The owner action queue is a deterministic list of manual actions with these fields:

- `action_id`
- `title`
- `priority`
- `source_card_id`
- `owner_decision_required`
- `execution_allowed`
- `safe_action`
- `blocked_by`

Examples included in this projection:

- `REVIEW_CAPITAL_WITHDRAWAL_PACKET`
- `REVIEW_RAIL_PROOF`
- `REVIEW_RISK_BLOCKERS`
- `REVIEW_REMAINING_WORK_NEXT_PACKET`
- `REVIEW_BIG_WINNER_WATCHLIST`

## Blocker Summary

`blocker_summary` separates:

- `risk_blockers`
- `rail_blockers`
- `reserve_blockers`
- `sensitive_data_blockers`
- `incomplete_input_blockers`
- `remaining_work_blockers`
- `all_blockers`

## Remaining Work Summary

`remaining_work_summary` includes:

- `closure_index_status`
- `remaining_lane_count`
- `next_best_packet`
- `blocked_lanes`
- `deferred_lanes`
- `top_remaining_lanes`
- `completion_policy_statuses`

## Display Contract

This packet is projection-only:

- `display_only: true`
- `mutates_repo: false`
- `creates_dashboard_runtime: false`
- `source_of_truth: "owner_review_capital_surface + remaining_work_closure_index"`
- `cards_are_projection_only: true`
- `owner_action_required_for_real_world_steps: true`

## Safety Boundary

Every output is:

- `read_only: true`
- `dashboard_runtime_created: false`
- `scheduler_created: false`
- `daemon_created: false`
- `webhook_created: false`
- `money_movement_allowed: false`
- `bank_access_allowed: false`
- `broker_api_allowed: false`
- `trade_execution_allowed: false`
- `credential_use_allowed: false`
- `owner_gate_required: true`
- `manual_execution_only: true`

## No Money Movement

No money movement is authorized in projection output.

## No Bank/Broker Access

No bank access and no broker API usage are authorized in projection output.

## No Trade Execution

No trade execution is authorized in projection output.

## No Scheduler/Daemon/Webhook

No scheduler, daemon, or webhook is started by this packet.

## Manual Owner Review Only

Every `safe_action`, `safe_manual_next_action`, and `owner_action_queue` entry is designed for manual owner review and rerun behavior only.

## Feeds Next Remaining-Work Packet

The projection feeds next closure-lane execution by including:

- `next_best_packet`
- `NEXT_PACKET` card
- `REMAINING_WORK` card
- `owner_action_queue` item `REVIEW_REMAINING_WORK_NEXT_PACKET`

