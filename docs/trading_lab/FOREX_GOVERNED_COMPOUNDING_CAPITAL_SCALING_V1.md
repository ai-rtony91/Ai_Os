# Forex Governed Compounding Capital Scaling V1

## Purpose

This packet is a metadata-only evaluator for controlled capital-scaling decisions in Forex.

It converts balance/equity and proof state into one controlled decision:

- `HOLD`
- `SCALE_UP`
- `SCALE_DOWN`
- `PROTECT_PROFIT`
- `STOP_COMPOUNDING`
- `OWNER_REVIEW_REQUIRED`

No trade order, broker call, broker credential read, money movement, banking, withdrawal, or routing is executed by this packet.

## Governing Rule Set

Compounding means:

- only verified realized profit may increase future risk budget,
- increase is bound by policy caps,
- every action remains metadata-only.

Compounding does not authorize:

- all-in sizing,
- unlimited scaling,
- revenge trading,
- scaling without sanitized receipts and verified proof,
- scaling during drawdown breach,
- scaling after daily-loss-stop,
- scaling while kill switch is active,
- scaling when banking, withdrawal, routing, transfer, or money movement focus is active,
- profit promises,
- live/demo execution.

## Required Metadata Inputs

- `balance_observer_result`
  - `status`
  - `ready`
  - `realized_profit_from_baseline`
  - `equity_drift`
  - `target_return_reached`
  - `target_balance_reached`
  - `withdrawal_deferred`
  - `bank_routing_deferred`
  - `money_moved`
- `compounding_scale_policy`
  - `compounding_enabled`
  - `owner_review_required`
  - `scale_up_allowed`
  - `scale_down_on_drawdown`
  - `stop_at_target`
  - `current_risk_budget_pct`
  - `max_scale_step_pct`
  - `max_risk_per_trade_pct`
  - `max_total_burst_risk_pct`
  - `profit_lock_pct`
  - `reinvest_profit_pct`
  - `minimum_verified_profit_to_scale`
  - `consecutive_scale_ups_since_review`
  - `max_consecutive_scale_ups_before_review`
  - `withdrawal_allowed`
  - `bank_routing_allowed`
  - `money_movement_allowed`
- `proof_state`
  - `receipts_sanitized`
  - `realized_pnl_verified`
  - `repeatability_score`
  - `proof_ready_for_scaling`
  - `fake_pnl_blocked`
- `risk_state`
  - `kill_switch_active`
  - `daily_loss_stop_active`
  - `drawdown_within_limit`
  - `current_drawdown_pct`
  - `max_drawdown_pct`
  - `current_daily_loss_pct`
  - `max_daily_loss_pct`
- `claims`
  - `guaranteed_profit_claimed`
  - `fixed_return_promised`
  - `daily_profit_guaranteed`
  - `weekly_profit_guaranteed`
  - `monthly_profit_guaranteed`
  - `yearly_profit_guaranteed`

## Verified Proof Requirement

`receipts_sanitized`, `realized_pnl_verified`, `proof_ready_for_scaling`, and
`fake_pnl_blocked` must be true to enable scale-up.

`repeatability_score` below 70 blocks scaling and routes to hold.

Claims and guarantees block and return `BLOCKED_BY_PROFIT_CLAIM`.

## Risk-Gated Scaling

- `kill_switch_active=True` returns `BLOCKED_BY_RISK_STATE`.
- `daily_loss_stop_active=True` returns `BLOCKED_BY_RISK_STATE`.
- `drawdown_within_limit=False` returns `SCALE_DOWN`.
- target hit or policy constraints are also handled deterministically before scale-up.

## Scale-Up Cap

`proposed_next_risk_budget_pct` is computed as:

```
min(current_risk_budget_pct + max_scale_step_pct, max_risk_per_trade_pct)
```

`max_scale_step_pct` and `max_risk_per_trade_pct` are bounded by policy constraints.

## Hold State

`HOLD` is returned when:

- compounding is disabled,
- verified profit has not reached minimum threshold,
- repeatability is below 70,
- owner review is pending,
- owner review policy or sequence limits require review.

## Scale-Down State

`SCALE_DOWN` returns when drawdown is breached (`drawdown_within_limit=False`).

## Target Protection

If `target_return_reached=True` or `target_balance_reached=True`, result is:

- `PROTECT_PROFIT`
- next packet: `AIOS_FOREX_PROFIT_PROTECTION_AND_WITHDRAWAL_REVIEW_FUTURE_V1`.

## Profit Lock and Reinvest

- `profit_lock_amount = realized_profit_from_baseline * profit_lock_pct`
- `reinvest_amount = realized_profit_from_baseline * reinvest_profit_pct`
- `protected_profit_amount = profit_lock_amount`

Negative realized values resolve to 0 lock/reinvest metadata by numeric conversion.

## Owner Review

Owner review is required when policy disables scale-up or scale-up history reached its review threshold.

`next_best_packet` for owner review is `AIOS_FOREX_VACATION_MODE_OWNER_TOGGLE_AND_OPERATION_STATE_V1`.

## No Trade, No Broker, No Credentials

Output hard-false guarantees include:

- `live_trade_executed_by_this_module = False`
- `demo_trade_executed_by_this_module = False`
- `broker_api_called_by_this_module = False`
- `credential_read = False`
- `money_moved = False`
- `banking_work_built = False`
- `withdrawal_work_built = False`
- `transfer_work_built = False`
- `bank_routing_built = False`
- `withdrawal_allowed_by_this_module = False`

The packet also sets `read_only=True`, `metadata_only=True`, `withdrawal_deferred=True`,
`bank_routing_deferred=True`, and zero broker/runtime flags.

## No Banking

Banking, withdrawal, routing, and money movement focus is blocked if active.
Explicit false safety flags for:

- `withdrawal_allowed=False`
- `bank_routing_allowed=False`
- `money_movement_allowed=False`

are accepted and do not block.

## Next Safe Packets

- scale up: `AIOS_FOREX_RUNTIME_ACTIVE_SUPERVISION_STATUS_V1`
- hold: `AIOS_FOREX_PROFIT_REPEATABILITY_EVIDENCE_V1`
- owner review: `AIOS_FOREX_VACATION_MODE_OWNER_TOGGLE_AND_OPERATION_STATE_V1`
- scale down: `AIOS_FOREX_RISK_SCALE_DOWN_REVIEW_V1`
- protect profit: `AIOS_FOREX_PROFIT_PROTECTION_AND_WITHDRAWAL_REVIEW_FUTURE_V1`
