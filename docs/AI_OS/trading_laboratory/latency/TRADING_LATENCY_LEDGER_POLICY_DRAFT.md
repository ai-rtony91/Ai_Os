# Trading Latency Ledger Policy Draft

Status: paper-only / simulation-only

## Purpose

Track signal timing delay before any live trading connection exists.

## Required Timing Fields

- signal_source
- alert_created_time
- alert_received_time
- ai_os_validation_start
- ai_os_validation_end
- traderspost_route_preview_time
- simulated_order_time
- total_delay_seconds
- latency_status
- blocked_reason

## Safety Rules

- Latency tracking is paper-only.
- `simulated_order_time` is not a real order.
- `latency_status` cannot unlock live trading.
- Live execution remains BLOCKED.
- No broker connection is allowed.
- No OANDA connection is allowed.
- No API keys are allowed.
- No real webhook execution is allowed.
- No real orders are allowed.
- No automatic route execution is allowed.

## Draft Status Values

- acceptable
- delayed
- stale

Thresholds are draft placeholders until enough paper-only timing samples exist.

## Next Safe Action

Record one paper-only mock alert timing path and keep all execution blocked.
