# AIOS FOREX Position Sizing (V1)

## Purpose

`automation/forex_engine/position_sizing.py` is the canonical paper-only size engine for forex preview flow. It computes how many units can be risked from account risk inputs and trade-stop geometry before a preview is sent to execution simulation.

## Scope and Safety Boundary

- Paper-only mode only.
- No broker SDK usage.
- No account credentials.
- No network calls.
- No file I/O.

The engine returns safety metadata in every result:

```python
{
    "paper_only": True,
    "broker": False,
    "live_trading": False,
    "credentials": False,
    "real_orders": False,
    "network_access": False
}
```

## Inputs

Preview fields expected:

- `pair` (required, uppercase-normalized)
- `direction` (`buy`/`sell` when provided)
- `entry_price` (positive)
- `stop_loss` (positive)
- `risk_percent` optional, fallback to `limits.default_risk_percent`
- `risk_dollars` optional override
- `paper_only` must not be `False`
- `mode` must not be `live`, `demo`, or `broker`

Account state fields (ordered risk preference):

- `equity`
- `current_balance`
- `cash_balance`
- `starting_balance`

When `risk_dollars` is absent, one of the account fields must be present and positive.

## Limits / Defaults

- `default_risk_percent`: `1.0`
- `max_risk_percent`: `1.0`
- `min_units`: `1.0`
- `max_units`: `0.0` (disabled)
- `rounding_increment`: `1.0`
- `max_risk_dollars`: `0.0` (disabled)
- `allow_fractional_units`: `False`
- `supported_pairs`: `["EURUSD", "GBPUSD", "USDJPY"]`
- `max_stop_distance` optional

Pair configuration:

- `pair_config` can include per-pair dicts keyed by pair symbol.
- `pip_value_per_unit` defaults to `1.0` when no explicit config is provided.

## Formula

1. `stop_distance = abs(entry_price - stop_loss)`
2. `risk_dollars = explicit risk_dollars if provided else risk_base * risk_percent / 100`
3. `raw_units = risk_dollars / (stop_distance * pip_value_per_unit)`
4. `units = round/down(raw_units, increment)` by configured policy
5. `estimated_loss_at_stop = units * stop_distance * pip_value_per_unit`

## Rejection reason taxonomy

- `invalid_preview`
- `non_paper_mode`
- `invalid_account_state`
- `invalid_balance`
- `missing_balance`
- `missing_entry_price`
- `invalid_entry_price`
- `missing_stop_loss`
- `invalid_stop_loss`
- `invalid_stop_distance`
- `invalid_risk_percent`
- `invalid_risk_dollars`
- `risk_exceeds_cap`
- `min_units_not_met`
- `max_units_exceeded`
- `insufficient_balance`
- `unsupported_pair`
- `invalid_pip_value`
- `invalid_rounding`

## Result shape

`calculate_position_size(preview, account_state, limits, pair_config)` returns a dict containing:

- `allowed`, `decision`, `blocked_reason`, `blocked_reasons`, `warnings`
- `paper_only`, `mode`, `pair`, `direction`
- `entry_price`, `stop_loss`, `stop_distance`
- `risk_base`, `risk_percent`, `risk_dollars`
- `pip_value`, `raw_units`, `units`, `min_units`, `max_units`, `rounding_increment`, `estimated_loss_at_stop`
- `safety`, `next_safe_action`, `metadata`

## Relationship to other modules

- `risk_governor.py` handles mandatory risk gate checks (daily loss, open risk, duplicate setup, spread/debounce policies).
- `paper_trade_lifecycle.py` tracks canonical trade state transitions after risk and sizing pass.
- `risk.py` remains the legacy/simulation-grade scaffold; this new module is the canonical sizing engine for upcoming order preview hardening and paper fill.

## Why this does not execute trades

This module computes units only. It performs no order submission, broker routing, or simulation fill execution.

## Next packet

- `FOREX-ORDER-PREVIEW-HARDENING`

