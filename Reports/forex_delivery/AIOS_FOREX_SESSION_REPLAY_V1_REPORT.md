# AIOS Forex Session Replay V1 Report

- Packet: `FOREX-SESSION-REPLAY-V1`
- Worktree: `C:\Dev\Ai.Os`
- Branch: `feature/forex-session-replay-v1`
- Files inspected:
  - `automation/forex_engine/evidence_ledger.py`
  - `automation/forex_engine/market_data_normalizer.py`
  - `automation/forex_engine/strategy_candidates.py`
  - `automation/forex_engine/multi_trade_queue.py`
  - `automation/forex_engine/order_preview.py`
  - `automation/forex_engine/risk_governor.py`
  - `automation/forex_engine/paper_fill_simulator.py`
  - `automation/forex_engine/trade_lifecycle_manager.py`
  - `automation/forex_engine/balance_compounding.py`
  - `docs/orchestration/AIOS_FOREX_EVIDENCE_LEDGER.md`
- Files changed:
  - `automation/forex_engine/session_replay.py`
  - `tests/forex_engine/test_session_replay.py`
  - `docs/orchestration/AIOS_FOREX_SESSION_REPLAY.md`

## Metrics added

- Candidate counts: total/accepted/rejected
- Preview counts: created/rejected
- Risk counts: accepted/rejected
- Trade counts: opened/closed plus trade lists
- P/L and outcome metrics: wins/losses/breakeven, gross profit, gross loss, net P/L, win rate, profit factor
- Balance metrics: start/end/change
- Drawdown metrics: max drawdown and percentage
- Risk usage sum from risk event payloads
- Replay metadata summary with source event ids and missing-evidence warnings

## Missing-evidence checks

- Close event without matching open
- Preview without corresponding candidate
- Risk without preview context
- Missing market data/candidate/risk/balance evidence warnings are surfaced via
  `missing_evidence_warnings` and validation-derived blocked reasons.

## Tests added

- Added `tests/forex_engine/test_session_replay.py` covering:
  - empty input handling
  - counts/aggregations
  - P/L and profit-factor determinism
  - balance reconstruction
  - missing evidence warnings
  - session filtering
  - paper/live/non-paper guards
  - invalid ledger/path handling
  - source-event determinism and safety source scan

## Safety boundary

- Paper-only session reconstruction only
- No live execution
- No broker/API calls
- No network or credentials
- In-memory event processing only

## Validators

- Not run by Codex (per packet constraints).

## Next human commands

- Run `pytest tests/forex_engine/test_session_replay.py`
- Wire replay output into dashboard truth layer as a read-only projection.

## Next safe action

- `FOREX-DASHBOARD-TRUTH-WIRING`
