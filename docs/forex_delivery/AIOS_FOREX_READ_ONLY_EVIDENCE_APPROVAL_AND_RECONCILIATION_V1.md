# AIOS Forex Read-Only Evidence Approval And Reconciliation V1

## Purpose

This layer evaluates sanitized read-only broker evidence and decides whether it can reduce future live-review blockers. It is not execution approval and it does not authorize a live trade.

## What Approval Means

Read-only evidence is approved for future live review only when it is sanitized broker read-only evidence, currently `broker-live-read-only` with an OANDA read-only sanitized label, valid freshness, reachable account state, reconciled open-position state, daily P/L availability, realized and unrealized P/L availability, margin/risk availability, read-only-only capabilities, and no secret/account/order/transaction identifier markers.

Trading history can be marked available or explicitly unavailable with a block reason while live execution remains blocked. Real trading-history writeback verification remains a separate blocker unless a sanitized history row/writeback is available.

## What Approval Does Not Mean

- It does not place a live trade.
- It does not authorize BUY, SELL, or close.
- It does not call a broker write endpoint.
- It does not read secrets.
- It does not print account, order, or transaction identifiers.
- It does not set `live_execution_allowed` true.
- It does not make `LIVE_ARMABLE` or `EXECUTION_REVIEW_READY` true by default.

## Blockers That Can Be Reduced

When sanitized evidence satisfies the specific field, downstream reviews may remove:

- `read_only_data_not_approved_for_future_live_execution`
- `broker_account_not_reachable_in_read_only_evidence`
- `open_positions_not_reconciled_in_read_only_evidence`
- `daily_pl_not_available_in_read_only_evidence`
- `open_live_position_state_not_reconciled`

## Blockers That Must Remain Unless Separately Solved

- `live_micro_trade_arming_gate_not_armable`
- `auto_exit_readiness_not_implemented_for_live_execution`
- `real_trading_history_writeback_not_verified`
- `future_execution_human_phrase_not_provided`
- `execution_review_packet_is_not_an_execution_packet`

## Run Order

```powershell
python scripts/forex_delivery/run_read_only_live_data_bridge.py
python scripts/forex_delivery/run_read_only_evidence_approval.py
python scripts/forex_delivery/run_live_micro_trade_arming_gate.py
python scripts/forex_delivery/run_one_shot_live_micro_trade_execution_review.py
```

## Next Target

The next target after this packet is auto-exit live readiness and real trading history writeback verification. Profitability is not guaranteed; any future execution must remain proof-based and risk-governed.
