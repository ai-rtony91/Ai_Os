# AIOS Forex Risk Governor (V1)

## Purpose

This packet introduces the canonical paper-only risk governor for Forex preview trades.

It evaluates preview-level signal payloads before any paper fill path and returns an
explicit allow/block decision so Trading Lab can enforce risk checks before
opening new paper trades.

## Paper-only boundary

Governor decisions are always paper-only:

```python
{
    "paper_only": True,
    "safety": {
        "paper_only": True,
        "broker": False,
        "live_trading": False,
        "credentials": False,
        "real_orders": False,
        "network_access": False,
    },
}
```

No broker, no credentials, no network, no order submission, and no scheduler/daemon/daemonization behaviors.

## Module

`automation/forex_engine/risk_governor.py`

Exports:

- `RISK_GOVERNOR_MODE = "PAPER_ONLY"`
- `RISK_DECISION_ALLOWED = "allowed"`
- `RISK_DECISION_BLOCKED = "blocked"`
- `RiskGovernorLimits`
- `RiskGovernorDecision`
- `evaluate_risk_preview(...)`

## Required preview fields

At minimum, a preview is evaluated as dict-like and should include:

- `pair` (uppercase normalized)
- `entry_price`
- `stop_loss`
- `take_profit`
- `units`
- `dollar_risk`
- `percent_risk`

Optional fields used by the governor:

- `paper_only`
- `mode`
- `spread`
- `data_timestamp`
- `status`
- `direction` (buy/sell)

`paper_only=False`, missing required pricing/risk values, and non-`PAPER_ONLY` mode are rejected.

## Account-state inputs

`account_state` may include:

- `current_balance`
- `cash_balance`
- `equity`
- `open_risk`
- `daily_loss_used`
- `max_daily_loss`
- `kill_switch_active`

Negative balances or risk fields are invalid account state.

## Limits

Limit defaults:

- `max_risk_per_trade_pct=1.0`
- `max_daily_loss=0.0` (disabled unless provided in limits/account)
- `max_open_risk=0.0` (disabled when `0.0`)
- `max_open_trades=1`
- `max_pair_exposure=0.0` (disabled when `0.0`)
- `max_spread=0.0` (disabled when `0.0`)
- `max_data_age_seconds=300`
- `cooldown_after_loss_seconds=0.0` (disabled when `0.0`)
- `duplicate_setup_block=True`

## Rejection reason taxonomy

- `none`
- `invalid_preview`
- `invalid_account_state`
- `non_paper_mode`
- `live_trading_blocked`
- `missing_stop_loss`
- `missing_take_profit`
- `invalid_stop_distance`
- `invalid_units`
- `invalid_risk_amount`
- `excessive_risk_per_trade`
- `max_daily_loss_hit`
- `max_open_risk_hit`
- `max_open_trades_hit`
- `max_pair_exposure_hit`
- `spread_too_high`
- `stale_market_data`
- `cooldown_after_loss`
- `duplicate_setup`
- `kill_switch_active`

`evaluate_risk_preview` returns all reasons discovered (deterministic order) in
`blocked_reasons`, and sets `blocked_reason` to the first deterministic primary
reason.

## Result shape

`evaluate_risk_preview(...)` returns:

```json
{
  "allowed": bool,
  "decision": "allowed" | "blocked",
  "blocked_reason": "none" | string,
  "blocked_reasons": ["..."],
  "warnings": ["..."],
  "paper_only": true,
  "mode": "PAPER_ONLY",
  "pair": "...",
  "dollar_risk": 0.0,
  "percent_risk": 0.0,
  "open_risk_after": 0.0,
  "daily_loss_after": 0.0,
  "open_trade_count_after": 0,
  "pair_exposure_after": 0.0,
  "max_risk_per_trade": 0.0,
  "max_daily_loss": 0.0,
  "max_open_risk": 0.0,
  "max_open_trades": 0,
  "max_pair_exposure": 0.0,
  "max_spread": 0.0,
  "data_age_seconds": 0,
  "safety": { "paper_only": true, ... },
  "next_safe_action": "...",
  "metadata": {}
}
```

## Relationship to existing modules

This packet does not replace `automation/forex_engine/risk.py`.

- `risk.py` remains the current sprint risk scaffold.
- `paper_trade_lifecycle.py` remains the canonical lifecycle state machine for paper trades.
- `risk_governor.py` is the mandatory preview gate used before paper fills/multi-trade expansion.

## Why this packet is not execution

The governor only computes deterministic risk decisions.
It does **not** execute broker calls, write files, open connections, or submit orders.
It is required to decide approval before paper fill or portfolio transition.

## Next safe packet

- `FOREX-POSITION-SIZING` or `FOREX-ORDER-PREVIEW-HARDENING` depending on repository state.
