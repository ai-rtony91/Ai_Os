# AIOS Forex Live Multi-Trade Expansion Gate

## Purpose

`automation/forex_engine/live_multi_trade_expansion_gate.py` reviews whether AIOS evidence is complete enough to request human review for future live multi-trade expansion.

This is review/gate policy only. It does not submit live orders, call broker APIs, read credentials, store account identifiers, enable live trading, or create execution routes.

## Inputs

- First live micro-trade proof.
- Live readiness review.
- Paper-to-demo promotion.
- Demo multi-trade runner.
- Demo reconciliation.
- Session replay.
- Risk limits.
- Human approval record.

## Output

The gate returns:

- `allowed`
- `decision`
- `expansion_ready`
- `live_multi_trade_allowed: False`
- `broker_submit_allowed: False`
- `max_live_trades_requested`
- `max_live_trades_allowed_review_only`
- `risk_cap`
- `kill_switch_required: True`
- `rollback_required: True`
- `required_evidence`
- `missing_evidence`
- `blocked_reasons`
- `warnings`
- `safety`
- `next_safe_action`
- `metadata`

## Blockers

The gate blocks when:

- Human approval is missing.
- First live micro-trade proof is missing.
- Live readiness review is missing.
- Kill switch or rollback proof is missing.
- Reconciliation is unresolved.
- Drawdown is too high.
- Risk failures are unresolved.
- Requested live trade count exceeds review-only cap.
- Risk cap exceeds limit.
- Account identifier, credential, broker write, order submit, live trading, or network submit signals appear.

## Safety

Even when `expansion_ready` is true, `live_multi_trade_allowed` and `broker_submit_allowed` remain false. This gate only supports review packet readiness.
