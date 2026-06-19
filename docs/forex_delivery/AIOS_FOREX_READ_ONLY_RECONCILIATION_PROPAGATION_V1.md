# AIOS Forex Read-Only Reconciliation Propagation V1

## Purpose

This pass fixes blocker propagation between sanitized read-only OANDA evidence, the live micro-trade arming gate, and the one-shot execution review.

## Propagation Rule

When sanitized read-only evidence reports `source_type: broker-live-read-only`, `source_label: OANDA_READ_ONLY_SANITIZED`, `stale_status: VALID`, broker account reachability, and open-position reconciliation, downstream readiness gates may remove only the corresponding account and position blockers.

## Removed When Proven

- `broker_account_not_reachable_in_read_only_evidence`
- `open_positions_not_reconciled_in_read_only_evidence`
- `open_live_position_state_not_reconciled`

## Still Blocked

- `daily_pl_not_available_in_read_only_evidence`
- `real_trading_history_unavailable_or_blocked`
- `real_trading_history_writeback_not_verified`
- `auto_exit_readiness_not_implemented_for_live_execution`
- `future_execution_human_phrase_not_provided`
- `execution_review_packet_is_not_an_execution_packet`

## Safety

This is propagation-only. It does not fake P/L, fake history, place trades, wire BUY/SELL/close, call broker write endpoints, read secrets, or output account/order/transaction identifiers. Live execution remains blocked.
