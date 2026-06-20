# AIOS Forex Session Replay V1

## Purpose

`automation/forex_engine/session_replay.py` provides deterministic session summaries from
canonical evidence ledger events for paper-only trading sessions.

## Paper-only boundary

- Mode must be `PAPER_ONLY`.
- `paper_only=False` events are rejected.
- Live/demo/broker style events are rejected via replay validation.
- Evidence paths must be relative.

## Ledger input

Input is a ledger-like iterable of event dictionaries as produced by
`automation/forex_engine/evidence_ledger.py`.
Optional `session_id` filters to a single session.

## Output shape

`build_session_replay(...)` returns:

- `allowed`, `decision`, `blocked_reason`, `blocked_reasons`, `warnings`
- `session_id`, `event_count`, `counts_by_event_type`
- candidate summary: `total_candidates`, `accepted_candidates`, `rejected_candidates`
- preview summary: `previews_created`, `previews_rejected`
- risk summary: `risk_accepted`, `risk_rejected`
- trade summary: `trades_opened`, `trades_closed`, `open_trades`, `closed_trades`
- P/L summary: `wins`, `losses`, `breakeven`, `gross_profit`, `gross_loss`, `net_pnl`, `win_rate_pct`, `profit_factor`
- balance summary: `balance_start`, `balance_end`, `balance_change`
- drawdown summary: `max_drawdown`, `max_drawdown_pct`
- risk usage: `risk_usage`
- missing evidence: `rejection_reasons`, `missing_evidence_warnings`
- replay metadata: `source_event_ids`, `replay_summary`
- safety/tracing fields including `safety`, `evidence`, `evidence_path`, `next_safe_action`

## P/L, balance, and risk metrics

The module derives:

- wins/losses/breakeven from `paper_trade_closed` events using `payload.realized_pnl`.
- `gross_profit` and `gross_loss` from closed trade realized P/L.
- `net_pnl = gross_profit - gross_loss`.
- `profit_factor = gross_profit / abs(gross_loss)` when `gross_loss > 0`, else `None`.
- `balance_start` and `balance_end` from `balance_updated` payloads when present.
- `balance_change = balance_end - balance_start` when both available.
- `risk_usage` from risk event payload keys `dollar_risk` and `risk_dollars`.

## Missing evidence checks

Replay emits `missing_evidence_warnings` when:

- candidate exists but required candidate payloads are missing
- preview events appear without candidate context
- risk events appear without related preview context
- trade closes appear for unknown trade IDs

## Relationship to evidence ledger and spine

This report is produced from outputs of:
`evidence_ledger.replay_ledger` and `evidence_ledger.validate_ledger`
with events from existing paper engine modules.

## Why safe

- No trade execution
- No broker API calls
- No credentials/network use
- No filesystem writes in runtime module

## Next safe packet

Next safe packet: `FOREX-DASHBOARD-TRUTH-WIRING`.
