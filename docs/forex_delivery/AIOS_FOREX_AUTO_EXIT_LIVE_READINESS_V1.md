# AIOS Forex Auto-Exit Live Readiness V1

## Purpose

This model records whether the exit policy evidence required before a future live micro-trade is present. It does not implement live close, broker write calls, order placement, or any live execution action.

## Model Rules

- `AUTO_EXIT_LIVE_READY` remains false by default.
- `live_execution_allowed` remains false.
- `stop_loss_required` is true.
- manual broker UI fallback is required.
- broker write calls, auto-exit write calls, and close trade actions remain false.
- readiness can only become policy-aware until a future dedicated live-safe exit packet exists.

## Remaining Blocker

`auto_exit_readiness_not_implemented_for_live_execution` must remain until a separately approved live-safe exit implementation exists.

## Run

```powershell
python scripts/forex_delivery/run_auto_exit_live_readiness.py
```

The script is local dry-run only and requires no secrets, broker calls, or network access.
