# AIOS Forex Demo Reconciliation

## Purpose

`automation/forex_engine/demo_reconciliation.py` compares sanitized demo read-only snapshots against AIOS paper/demo intent records and returns reconciliation evidence.

This is reconciliation only. It does not submit, close, modify, route, connect, authenticate, or call broker APIs.

## Inputs

- Sanitized demo read-only snapshot.
- `demo_order_intent` from demo order mapping.
- Optional paper fill result.
- Optional lifecycle result.

## Output

The reconciliation report includes:

- `allowed`
- `decision`
- `blocked_reason`
- `blocked_reasons`
- `warnings`
- `mode: DEMO_RECONCILIATION_ONLY`
- `paper_only: True`
- `demo_readonly: True`
- `matched`
- `match_score`
- `pair_match`
- `side_match`
- `units_match`
- `price_within_tolerance`
- `stop_loss_match`
- `take_profit_match`
- `position_seen`
- `order_seen`
- `stale_data`
- `mismatches`
- `evidence`
- `safety`
- `next_safe_action`
- `metadata`

## Blockers

The reconciler blocks if:

- Account identifier material is present.
- Credential-loaded flags are present.
- Broker write, order submit, live trading, or network submit flags are enabled.
- Exact account identifier values are detected.
- Snapshot mode is unsupported.
- Snapshot data is stale.
- Intent is invalid.
- Intent pair, side, or units are missing.

## Safety

The safety dict always keeps:

- `paper_only: True`
- `demo_readonly: True`
- `broker_write: False`
- `live_trading: False`
- `credentials: False`
- `real_orders: False`
- `network_submit: False`

No execution, broker access, network access, file access, or runtime sensitive-material access is added.
