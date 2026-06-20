# AIOS Forex Market Data Normalizer

## Purpose

`market_data_normalizer.py` is the canonical paper-only market data normalization layer for the Forex paper engine. It ensures every strategy/preview path receives deterministic, validated, and bounded market input before order preview or risk checks proceed.

## Paper-Only Boundary

- Output is always `PAPER_ONLY`.
- Non-paper inputs are blocked (live/demo/broker submission paths are rejected).
- The module performs no file writes, no broker calls, no credential access, no network access, and no live order execution.

## Raw Input Fields

Expected fields include:

- `pair` or `symbol` (e.g., `EURUSD`, `EUR_USD`, `EUR/USD`)
- `bid`
- `ask`
- `timestamp` or `data_timestamp`
- `source_mode` (`sample`, `paper`, `demo_readonly`, `live_blocked`, `live`, `broker`)
- optional `spread`
- optional `session_label`
- optional `candle` or `candles`

Pair normalization:

- Uppercases and removes separators (`_`, `/`, `-`), so `EUR_USD` becomes `EURUSD`.

## Output Shape

`normalize_market_snapshot` returns:

- `allowed`, `decision`
- `blocked_reason`, `blocked_reasons`
- `warnings`
- canonical fields: `paper_only`, `mode`, `pair`, `bid`, `ask`, `mid`, `spread`, `spread_pips`, `pip_size`, `timestamp`, `data_age_seconds`, `fresh`, `source_mode`, `session_label`, `candle`, `candles`
- `normalized_for_preview`
- `normalized_for_strategy`
- `evidence`, `evidence_path`
- `safety`
- `next_safe_action`
- `metadata`

`normalized_for_preview` contains:

- `pair`, `entry_price` (mid), `bid`, `ask`, `spread`, `spread_pips`, `data_timestamp`, `paper_only`

`normalized_for_strategy` contains:

- `pair`, `bid`, `ask`, `mid`, `spread_pips`, `candle/candles`, `timestamp`, `source_mode`, `session_label`, `paper_only`

## Rejection Rules

- missing/invalid pair
- unsupported pair
- missing/invalid bid/ask
- invalid spread (`ask < bid`, non-positive values)
- spread too high
- missing/invalid timestamp and stale timestamps (if `require_timestamp=True`, default)
- invalid or missing candle input when required
- invalid source mode
- unsupported live/broker mode

Defaults:

- supported pairs: `EURUSD`, `GBPUSD`, `USDJPY`
- `max_spread_pips`: `3.0`
- `max_data_age_seconds`: `300`
- `require_timestamp`: `True`
- `require_candle`: `False`

## Candle Validation

- Supports both single `candle` and list `candles`
- Requires OHLCV fields: `open`, `high`, `low`, `close`, `volume`, `timestamp`
- All OHLC values must be positive
- `high` must be >= `open`, `close`, and `low`
- `low` must be <= `open`, `close`, `high`
- `volume` must be non-negative

## Source Modes

- `sample`/`paper`/`demo_readonly`/`live_blocked` accepted
- `live` blocked as live trading mode
- `broker` blocked as non-paper mode
- other unknown values blocked as invalid source mode

## Integration and Boundaries

- Consumed by canonical preview risk stack before `order_preview.py` and `risk_governor.py`.
- This module does not fetch market data; it only normalizes already provided raw snapshots.
- Evidence is returned as metadata only.

## Next Safe Packet

- `FOREX-STRATEGY-CANDIDATES`
