# AIOS Forex Owner-Review Capital Surface V1

## Purpose
Create a single deterministic, read-only owner-facing surface for:
- capital bucket status
- rail readiness
- withdrawal cadence
- withdrawal plan
- OANDA funding posture
- big-winner watchtower signals
- remaining-work sequencing

This surface intentionally only summarizes precomputed outputs and does not perform actions.

## Inputs
- `bucket_purge_controller` (sanitized bucket summary payload)
- `capital_rail_registry` (sanitized rail registry summary payload)
- `withdrawal_cadence_planner` (sanitized cadence payload)
- `capital_rail_withdrawal_plan` (sanitized plan payload)
- `oanda_funding_rail_readiness` (optional)
- `big_winner_watchtower` (optional)
- `as_of_date`
- `owner_name`

## Output
All required output fields are emitted by module:
- schema and mode
- read-only / owner-gated flags
- `owner_review_cards`
- `safe_manual_next_action`
- summaries for capital buckets, rails, cadence, plan, OANDA funding, and big-winner watchtower
- audit record
- safety block

## Owner review cards
`owner_review_cards` includes:
- `CAPITAL_BUCKETS`
- `RAILS`
- `WITHDRAWAL_CADENCE`
- `WITHDRAWAL_PLAN`
- `OANDA_FUNDING`
- `BIG_WINNER_WATCHTOWER`
- `REMAINING_WORK`

Each card has:
- `card_id`
- `title`
- `status`
- `priority`
- `owner_decision_required`
- `execution_allowed` (always `False`)
- `summary`
- `blockers`
- `safe_next_action`

## Capital bucket summary
Includes:
- `bucket_state`
- `stale_bucket_flags`
- `purge_actions_count`
- `rollover_actions_count`
- `sweep_actions_count`
- `withdrawal_bucket_status`
- protected reserve status
- `margin_or_open_risk_block`
- `daily_loss_stop_active`

## Rail readiness summary
Includes:
- eligible rail count
- blocked rail count
- lowest-cost rail id
- fastest rail id
- preferred withdrawal rail id
- same-name proof status
- sensitive data block indicator
- third-party payment block indicator

## Withdrawal cadence summary
Includes:
- `recommended_cadence`
- weekly / monthly / bimonthly eligibility
- no-withdrawal reasons
- risk blocks
- fee efficiency

## Withdrawal plan summary
Includes:
- `withdrawal_plan_status`
- `eligible_for_owner_review`
- `selected_review_rail`
- `owner_gate`
- `manual_execution_only`
- `safe_next_action`

## OANDA funding summary
Uses only supplied OANDA payload and reports:
- readiness status
- same-name bank requirement
- withdrawal hierarchy notes
- blockers

## Big-winner summary
Uses only supplied watchtower payload and reports:
- alert level
- top opportunity pair/direction if present
- big-winner candidate count
- safe next action

No trade execution recommendations are emitted.

## Surface statuses
The surface status supports:
- `READY_FOR_OWNER_REVIEW`
- `WATCHLIST_ONLY`
- `BLOCKED_BY_RISK`
- `BLOCKED_BY_RAIL`
- `BLOCKED_BY_RESERVE`
- `BLOCKED_BY_SENSITIVE_DATA`
- `INCOMPLETE_INPUTS`

## Safety boundary
- `read_only = True`
- `money_movement_allowed = False`
- `bank_access_allowed = False`
- `broker_api_allowed = False`
- `trade_execution_allowed = False`
- `credential_use_allowed = False`
- `manual_execution_only = True`
- `scheduler_allowed = False`
- `daemon_allowed = False`
- `webhook_allowed = False`
- `owner_gate_required = True`

## Manual owner review only
AIOS does not:
- move money
- access banks
- access brokers
- execute trades

All outputs are review-first and owner-authorized-only.
