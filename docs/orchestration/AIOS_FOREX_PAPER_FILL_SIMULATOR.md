# AIOS FOREX Paper Fill Simulator (V1)

## Purpose

`automation/forex_engine/paper_fill_simulator.py` is the canonical paper-only fill step after order preview approval. It consumes an approved order preview and materializes a paper trade with deterministic lifecycle transitions for downstream paper execution/queue flows.

## Paper-only boundary

- `PAPER_FILL_MODE = "PAPER_ONLY"`
- Never touches broker APIs, account credentials, or live order endpoints.
- No file writes; `evidence` is returned metadata only.
- No networking or filesystem operations.
- Output always includes:

```python
{
  "paper_only": True,
  "broker": False,
  "live_trading": False,
  "credentials": False,
  "real_orders": False,
  "network_access": False,
}
```

## Required input

`order_preview` must be an approved preview payload with:

- `allowed == True`
- `approval_state == "paper_preview_ready"`
- `paper_only` not `False`
- `mode` not `live|demo|broker`
- `pair`, `direction`, `entry_type`, `entry_price`, positive `units`

Optional:

- `market_state`:
  - `bid`, `ask` (used when present)
  - `spread` (optional, else derived from bid/ask)
- `fill_config`:
  - `slippage`
  - `max_spread`
  - `max_slippage`

`evidence_path` must be a relative metadata string when provided.

## Fill math

- For buy:
  - `fill_price = ask + slippage` when bid/ask present
- For sell:
  - `fill_price = bid - slippage` when bid/ask present
- Without market bid/ask:
  - `fill_price = entry_price` (fallback)
- `spread = bid/ask spread` when available
- Block when spread exceeds `max_spread` or slippage exceeds `max_slippage` (if caps > 0).

## Lifecycle integration

`simulate_paper_fill` creates a canonical paper trade using `build_paper_trade(...)`
from `automation.forex_engine.paper_trade_lifecycle` and applies deterministic transitions:

- `candidate -> previewed -> queued -> opened -> active`

Lifecycle data is returned in `lifecycle_result` and the final trade object in `trade`.

## Returned payload

- `allowed`, `decision`, `blocked_reason`, `blocked_reasons`, `warnings`
- `paper_only`, `mode`, `fill_id`, `preview_id`, `trade_id`, `pair`, `direction`, `entry_type`
- `requested_price`, `fill_price`, `filled_units`, `slippage`, `spread`, `opened_timestamp`, `status`
- `trade`, `lifecycle_result`, `evidence`, `evidence_path`, `safety`, `next_safe_action`, `metadata`

`fill_id` is deterministic, derived from `preview_id/pair/direction/fill_price/units/timestamp` with SHA-256.

## Integration context

- This module consumes canonical output from `order_preview.py`.
- It is canonical for Forex Engine paper fill simulation.
- Legacy `apps/trading_lab/trading_lab/forex_paper_execution_simulator.py` is not modified and remains historical/supported in parallel.
- Dashboard/orchestrator should consume this module output; no trade truth is created outside paper-state flow.

## Why this does not execute real trades

This is a simulation and transitions helper. It creates paper-trade structures only and never sends orders to brokers or live systems.

## Next packet

- `FOREX-TRADE-LIFECYCLE`

