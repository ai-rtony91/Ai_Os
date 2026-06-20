# AIOS Forex Balance and Compounding Engine

## Purpose

`balance_compounding.py` is the canonical paper-only engine that updates paper account state from closed-trade output and computes a deterministic risk base for subsequent sizing under fixed compounding rules.

## Paper-Only Boundary

- Paper-only mode is mandatory (`PAPER_ONLY`).
- `paper_only=False` is rejected.
- Any live/demo/broker mode is rejected.
- No broker calls, account credentials, network traffic, filesystem writes, or scheduler/daemon automation are performed.
- Output is deterministic metadata intended for downstream paper modules only.

## Inputs

### `apply_closed_trade_to_balance(account_state, closed_trade_result, limits=None, evidence_path=None, metadata=None)`

- `account_state` may include:
  - `starting_balance`
  - `current_balance` / `cash_balance` / `equity`
  - `realized_pnl`
  - `daily_loss_used`
  - `open_risk`
  - `trade_count`
  - `session_count`
  - `peak_balance`
  - `drawdown_percent`
  - `compounding_enabled`
- `closed_trade_result` may include:
  - `realized_pnl`
  - `closed`
  - `paper_only`
  - `mode`
  - `trade_id`, `pair`, `direction`, `close_reason`
- `limits` may include:
  - `compounding_enabled`
  - `compounding_cap_percent`
  - `profit_lock_percent`
  - `drawdown_reduce_threshold_percent`
  - `recovery_risk_multiplier`
  - `max_recovery_multiplier_after_loss`
- `evidence_path` must be a plain relative metadata path.

## Balance Update Formula

- `current_balance_after = current_balance_before + realized_pnl`
- `realized_pnl_total = realized_pnl_total_before + realized_pnl`
- `daily_loss_used` increases by `abs(realized_pnl)` when `realized_pnl < 0`
- `trade_count` increments for each valid closed trade
- `peak_balance = max(previous_peak, current_balance_after)`
- `drawdown = max(0, peak - current_balance_after)`
- `drawdown_percent = drawdown / peak * 100` when `peak > 0`

## Risk Base Formula

- Base balance for sizing is:
  - `current_balance_after` if compounding is enabled
  - `starting_balance` if compounding is disabled
- Compounding cap applies: `risk_base <= starting_balance * (1 + compounding_cap_percent / 100)`
- Recommended risk multiplier is reduced deterministically when drawdown threshold is exceeded.
- No martingale/recovery up-sizing after a loss.

## Compounding Controls

- `compounding_cap_percent` limits upward risk base expansion when compounding is enabled.
- `profit_lock_percent` designates locked profit that should not be used for compounding:
  - `protected_profit = max(0, (current_balance_after - starting_balance) * profit_lock_percent / 100)`
  - `available_compound_profit = max(0, current_balance_after - starting_balance - protected_profit)`
- If drawdown is high, risk multiplier is reduced.
- After a losing trade, risk multiplier requests above allowed recovery limits are blocked.

## Drawdown Risk Reduction

- High drawdown percentage decreases risk multiplier below 1.0 in a deterministic, bounded way.

## Martingale / Recovery Policy

- The engine blocks any recovery multiplier request greater than the allowed recovery cap after a loss.
- This prevents doubling-up/martingale-like behavior in paper-only sizing.

## Evidence Behavior

- Returns inline structured `evidence` data.
- Does not write files.

## Integration

- Consumes closed-trade output from `trade_lifecycle_manager.py`.
- Produces `risk_base` for `position_sizing.py`.
- Compatible with current paper-only pipeline and forecasted forecast compounding updates.

## Next Safe Packet

- `FOREX-MARKET-DATA-NORMALIZER` or `FOREX-MULTI-TRADE-QUEUE`
