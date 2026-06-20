# AIOS FOREX LONG RUN PAPER SUPERVISOR

## Purpose

The long-run paper supervisor is the canonical runtime coordinator for paper-only paper sessions.
It composes existing canonical modules in a deterministic order:

1. market data normalization
2. strategy candidate generation
3. multi-trade queue selection
4. order preview
5. paper fill simulation
6. lifecycle update
7. balance compounding
8. in-memory evidence recording
9. session replay summarization

## Paper-only boundary

- `paper_only` is required in all outputs.
- No broker/API/demo/live mode is executed.
- No credentials are read.
- No network calls are made.
- No files are written for runtime evidence.
- `safety` is a metadata block that explicitly reports:
  - `paper_only: True`
  - `broker: False`
  - `live_trading: False`
  - `credentials: False`
  - `real_orders: False`
  - `network_access: False`

## Inputs

- `market_batch`: iterable of raw market snapshots.
- `account_state`: optional paper account state.
- `open_trades` and `closed_trades`: optional in-memory lists.
- `session_state`: optional session metadata such as `session_id` and `cycle_number`.
- `limits`: optional policy limits (max cycles, max session trades, max session loss, stale cutoff, kill switch).
- `timestamp`: optional deterministic timestamp.
- `evidence_path`: metadata-only string path; absolute paths are rejected.

## Cycle flow

`run_paper_supervisor_cycle(...)` returns a structured dict with deterministic
counts and stop metadata:

- `normalized_market_count`
- `candidate_count`
- `selected_count`
- `rejected_count`
- `previews_created`
- `fills_created`
- `trades_opened`
- `trades_closed`
- `balance_updates`
- in-memory `ledger_events`
- `replay_summary`

It appends local evidence events when components produce output.

## Stop conditions

The cycle can stop with deterministic reasons:

- `stale_market_data` when market normalization is blocked as stale
- `risk_halt` when preview validation is blocked
- `kill_switch_active` when kill switch is set in limits
- `max_cycles_hit`
- `max_session_trades_hit`
- `max_session_loss_hit`
- `validation_failure`
- `invalid_market_batch`
- `non_paper_mode`
- `live_trading_blocked`
- `evidence_path_invalid`

Even when blocked, it returns a deterministic structured result and replay payload.

## Account and balance behavior

- Current paper account is copied into `account_state_before`.
- Closed-trade lifecycle updates may call balance compounding and update `account_state_after`.
- `balance_updates` counts successful balance applications.
- No runtime balances are persisted to disk.

## Relationships to prior modules

- Market data: `market_data_normalizer`
- Candidate generation: `strategy_candidates`
- Queueing: `multi_trade_queue`
- Preview gate: `order_preview`
- Fill engine: `paper_fill_simulator`
- Lifecycle updates: `trade_lifecycle_manager`
- Balance compounding: `balance_compounding`
- Evidence: `evidence_ledger` event shape
- Replay: `session_replay`

## Evidence and replay behavior

All cycle actions are expressed as event-like dictionaries and returned via
`ledger_events`.
The supervisor does not persist those events; consumers can pass the list to
`session_replay` for session-level reports.

## Why this is safe

- No broker endpoints.
- No order submission.
- No account credential usage.
- No daemon or scheduler loop.
- Deterministic and restartable with provided timestamp/evidence metadata.

## Next safe packet

- `AIOS-FOREX-SELF-IMPROVEMENT` if paper evidence shows recurring deterministic failure
  patterns, otherwise `FOREX-DEMO-CONNECTOR-READONLY` based on packet sequencing.
