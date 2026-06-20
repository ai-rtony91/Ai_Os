# AIOS Forex Trade Lifecycle Manager

## Purpose

`trade_lifecycle_manager.py` is the canonical Forex engine module for updating active paper trades against market or control events and producing deterministic close output. It closes trades by stop loss, take profit, manual close, expiry, or kill-switch events and returns paper-account ready evidence payloads for downstream accounting flows.

## Paper-Only Boundary

This module is paper-only by design:

- `paper_only` must be true on the input trade.
- `mode` must be paper-only (`PAPER_ONLY`).
- No broker adapter, no account credential usage, no network calls, and no live order paths are performed.
- Only deterministic in-memory dictionaries are produced.

## Inputs

`process_trade_update`:

- `trade`: dict or dataclass-like object from trade creation/fill flow.
- `price_update`: optional price dict with `bid`, `ask`, or `price`.
- `timestamp`: optional unix timestamp for expiry evaluation and lifecycle timestamps.
- `manual_close_price`: optional explicit close value for manual intervention.
- `expire_at`: optional expiry timestamp.
- `kill_switch`: optional bool that forces immediate close.
- `evidence_path`: optional relative metadata path string.
- `metadata`: free-form dict metadata payload.

Required minimum trade fields for processing:

- `trade_id`
- `pair`
- `direction` (`buy` / `sell`)
- `entry_price`
- `stop_loss`
- `take_profit`
- `units`
- `status` (`active` or `opened`)

Pair is normalized to upper-case.

## Close Rules

- Buy trade:
  - Stop loss: close when `bid/price <= stop_loss`
  - Take profit: close when `bid/price >= take_profit`
- Sell trade:
  - Stop loss: close when `ask/price >= stop_loss`
  - Take profit: close when `ask/price <= take_profit`
- Manual close:
  - immediate close when `manual_close_price` is valid
- Kill switch:
  - immediate close when enabled
  - uses current `bid/ask/price` if provided
  - may fallback to `manual_close_price` when available
- Expiry:
  - closes when `timestamp >= expire_at`

If no close trigger hits, status remains active and monitoring continues.

## P/L Formula

- `buy`: `realized_pnl = (exit_price - entry_price) * units`
- `sell`: `realized_pnl = (entry_price - exit_price) * units`

Result is deterministic and emitted as plain numeric value.

## Returned Payload

`process_trade_update` returns:

- `allowed` and `decision` (`allowed` / `blocked`)
- blocked details and list
- core trade outcome fields (`trade_id`, `pair`, `direction`, `status`, `closed`, `close_reason`, `realized_pnl`, etc.)
- `lifecycle_result` from transition processing
- inline `evidence` and `evidence_path` metadata
- `safety` boundary flags
- `next_safe_action`

`evidence` is returned data only; no file write occurs.

## Lifecycle Integration

- Uses canonical lifecycle helpers from `paper_trade_lifecycle.py`:
  - transitions to `closed`, `killed`, `expired`, or `error` where appropriate
  - preserves immutable fields and appends history events.

## Non-Execution Guarantee

- No broker/live/demo adapter calls.
- No file system writes.
- No network IO.
- No credentials/account access.
- No dashboard truth generation responsibility inside this module.

## Relationship

- Input `trade` may be produced by canonical `paper_fill_simulator.py`.
- Status/transition behavior aligns with canonical `paper_trade_lifecycle.py`.
- It is a deterministic paper control module used before account/projection updates.

## Next Safe Packet

- `FOREX-BALANCE-COMPOUNDING`
