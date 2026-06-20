# AIOS Forex Multi-Trade Queue V1 Report

- Packet: `FOREX-MULTI-TRADE-QUEUE-V1`
- Worktree: `C:\Dev\Ai.Os`
- Branch: `feature/forex-multi-trade-queue-v1`
- Files inspected: `automation/forex_engine/strategy_candidates.py`, `automation/forex_engine/order_preview.py`, `automation/forex_engine/risk_governor.py`, `automation/forex_engine/position_sizing.py`, `automation/forex_engine/market_data_normalizer.py`, `automation/forex_engine/paper_fill_simulator.py`, `automation/forex_engine/trade_lifecycle_manager.py`, `automation/forex_engine/balance_compounding.py`, `docs/orchestration/AIOS_FOREX_STRATEGY_CANDIDATES.md`, `docs/orchestration/AIOS_FOREX_ORDER_PREVIEW_HARDENING.md`, `docs/orchestration/AIOS_FOREX_RISK_GOVERNOR.md`
- Files changed:
  - `automation/forex_engine/multi_trade_queue.py`
  - `tests/forex_engine/test_multi_trade_queue.py`
  - `docs/orchestration/AIOS_FOREX_MULTI_TRADE_QUEUE.md`

## Queue behavior added

- Implemented deterministic ranking by score → pair → candidate ID.
- Added queue limits for score thresholding, max selected, max open, per-pair count/exposure,
  session cap, cooldown, duplicate setup prevention.
- Added optional `evaluate_risk_preview` and `build_order_preview` integration.
- Added deterministic rejection reasons and evidence summary metadata.

## Caps enforced

- `max_selected_trades`
- `max_open_trades` (existing open-like trades + selected)
- `max_candidates_per_pair`
- `max_pair_exposure` (using `dollar_risk` family)
- `session_trade_cap`
- `cooldown_after_loss_seconds`

## Risk integration

- Risk governor checks are enabled by default and append deterministic entries under
  `risk_evaluations`.
- Optional order-preview checks available when `require_order_preview=True`.

## Rejection reasons added

- `non_paper_mode`, `live_trading_blocked`, `missing_candidate_id`, `missing_pair`,
  `missing_direction`, `invalid_score`, `score_below_threshold`, `duplicate_setup`,
  `max_selected_trades_hit`, `max_open_trades_hit`, `max_pair_candidate_hit`,
  `max_pair_exposure_hit`, `session_trade_cap_hit`, `cooldown_active`,
  `risk_governor_blocked`, `order_preview_blocked`, `invalid_candidates`,
  `evidence_path_invalid`.

## Tests added

- Added `tests/forex_engine/test_multi_trade_queue.py` with ranking, cap, risk, preview, safety,
  evidence, and source-safety tests.

## Safety boundary

- Module stays paper-only.
- No broker/demo/live API calls.
- No credentials, no network I/O, no filesystem writes.

## Validators

- Not run by Codex (per packet constraints).

## Next human commands

- Run tests for `tests/forex_engine/test_multi_trade_queue.py`.
- Integrate `build_multi_trade_queue` output into the queue orchestration boundary.

## Next safe action

- `FOREX-EVIDENCE-LEDGER`
