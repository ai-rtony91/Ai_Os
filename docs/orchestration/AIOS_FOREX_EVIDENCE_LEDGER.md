# AIOS Forex Evidence Ledger

## Purpose

The evidence ledger is the deterministic, paper-only event trail for the Forex engine spine.
It records market-data, strategy, preview, risk, fill, lifecycle, balance, kill-switch, and session summary events as immutable in-memory entries so behavior can be reconstructed.

## Paper-only boundary

- `mode` must be `PAPER_ONLY`.
- `paper_only=False` is rejected.
- Live/demo/broker style modes are rejected.
- Evidence path is metadata-only and must be a relative path.

## Event types

Supported event types:

- `market_data_accepted`
- `market_data_rejected`
- `strategy_candidate_created`
- `candidate_rejected`
- `preview_created`
- `preview_rejected`
- `risk_accepted`
- `risk_rejected`
- `paper_trade_opened`
- `paper_trade_closed`
- `balance_updated`
- `kill_switch_triggered`
- `session_summary_generated`

## Event shape

All events include:

- `event_id`
- `event_type`
- `session_id`
- `timestamp`
- `parent_event_id`
- `sequence`
- `payload`
- `paper_only`
- `mode`
- `evidence_path`
- `safety`
- `metadata`

`event_id` is deterministic when not provided using type/session/timestamp/payload hashing.

## Build behavior

`build_ledger_event(...)` validates:

- allowed event type
- session/timestamp presence
- payload shape
- evidence path validity

Invalid input returns `allowed=False` with structured `blocked_reason`/`blocked_reasons`.

## Append behavior

`append_ledger_event(ledger, event)`:

- never mutates input ledger
- assigns canonical sequence
- rejects duplicate `event_id`
- validates required fields
- returns updated ledger payload for deterministic consumption

## Validate behavior

`validate_ledger(ledger, session_id=None)` checks:

- required event fields
- duplicate ids
- deterministic sequencing
- parent references when provided
- non-paper/live flags

Returns structured validation result with `valid`, `errors`, and counts.

## Replay behavior

`replay_ledger(ledger, session_id=None)` reconstructs:

- `total_events`
- `counts_by_event_type`
- accepted/rejected market data counts
- strategy candidate counts
- preview counts
- risk counts
- trade open/close counts
- balance updates
- kill-switch events
- session summaries
- missing-parent and invalid-event signals

## Evidence-chain behavior

- `parent_event_id` creates deterministic event-order constraints.
- Missing parent IDs are detected and reported as `evidence_chain_broken` in validation/replay summaries.

## Evidence path behavior

- `evidence_path` is metadata only.
- Absolute paths (Unix/Windows style) are rejected.

## Why this is safe

- No filesystem writes in runtime path
- No broker APIs
- No live order actions
- No network calls
- No credentials, account IDs, or secrets

## Relationship to other modules

- This ledger records outputs from:
  - `strategy_candidates`
  - `multi_trade_queue`
  - `order_preview`
  - `risk_governor`
  - `paper_fill_simulator`
  - `trade_lifecycle_manager`
  - `balance_compounding`

It does not replace those modules and does not execute trading.

## Next packet

Next safe packet: `FOREX-SESSION-REPLAY`.
