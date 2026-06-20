# AIOS Forex Multi-Trade Queue (Paper-Only)

## Purpose

`automation/forex_engine/multi_trade_queue.py` provides a deterministic, paper-only
queue for selecting strategy candidates before preview and fill. It ranks candidates,
applies session and risk-cap constraints, blocks unsafe duplicates, and emits selected
and rejected output for deterministic downstream processing.

## Paper-only boundary

- Queue mode must be `PAPER_ONLY`.
- `paper_only=False` candidates are blocked with `non_paper_mode`.
- `live`, `demo`, and `broker` style modes are blocked with `live_trading_blocked`.

## Candidate input

Input may be:

- a dict from `strategy_candidates` that contains `candidates`, or
- an iterable of candidate mappings.

Each candidate is normalized and required to include:

- `candidate_id`
- `pair`
- `direction` (`buy` or `sell`)
- `score` (0 to 100)

Optional risk value keys accepted for exposure checks:
`dollar_risk`, `risk_dollars`, `risk_amount`, `risk_amount_usd`.

## Ranking

Candidates are ranked deterministically:

1. highest `score` first
2. alphabetic `pair`
3. alphabetic `candidate_id`

## Blocking and caps

The queue rejects candidates with deterministic reasons:

- `score_below_threshold` (default threshold: `min_score = 50`)
- `duplicate_setup` for same `pair + direction` already queued/active/opened
- `max_selected_trades_hit`
- `max_open_trades_hit`
- `max_pair_candidate_hit`
- `max_pair_exposure_hit`
- `session_trade_cap_hit`
- `cooldown_active`
- `risk_governor_blocked`
- `order_preview_blocked`
- plus validation blockers (`missing_candidate_id`, `missing_pair`, `missing_direction`,
  `invalid_score`, etc.)

Default limits:

- `min_score`: `50`
- `max_selected_trades`: `3`
- `max_open_trades`: `3`
- `max_candidates_per_pair`: `1`
- `max_pair_exposure`: `0` (disabled)
- `session_trade_cap`: `0` (disabled)
- `cooldown_after_loss_seconds`: `0` (disabled)
- `duplicate_setup_block`: `True`
- `require_risk_governor`: `True`
- `require_order_preview`: `False`

## Risk governor and optional order preview integration

- If `require_risk_governor` is true, each candidate is checked with
  `evaluate_risk_preview` before selection.
- If `require_order_preview` is true, each candidate is checked with
  `build_order_preview`.
- Only candidates with approvals from enabled gates can be selected.

## Output

The result dict contains:

- `allowed`, `decision`, `blocked_reason`, `blocked_reasons`
- `selected_candidates`, `rejected_candidates`, `ranked_candidates`
- `risk_evaluations`, `preview_evaluations` (when enabled)
- `limits`, `evidence`, `evidence_path`, `safety`, `next_safe_action`

## Evidence behavior

- Evidence is returned as in-memory result metadata only.
- Evidence paths are metadata-only strings and must remain relative.
- The module does not write files, call brokers, hit network, or submit live orders.

## Next packet

Next safe packet: `FOREX-EVIDENCE-LEDGER`.
