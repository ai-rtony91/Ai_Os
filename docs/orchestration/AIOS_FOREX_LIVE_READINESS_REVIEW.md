# AIOS Forex Live Readiness Review

## Purpose

`automation/forex_engine/live_readiness_review.py` evaluates whether AIOS has enough paper/demo evidence to request human review for a future live micro-trade exception.

This is review only. It does not enable live trading, submit orders, store credentials, call broker APIs, or mark live-ready automatically.

## Inputs

- Paper-to-demo promotion decision.
- Demo multi-trade runner plan.
- Demo reconciliation result.
- Session replay summary.
- Evidence ledger validation.
- Risk metrics.
- Kill-switch proof.
- Human approval flag.

## Output

The review returns:

- `allowed`
- `decision`
- `blocked_reason`
- `blocked_reasons`
- `warnings`
- `mode`
- `live_ready`
- `readiness_score`
- `paper_evidence_ok`
- `demo_evidence_ok`
- `reconciliation_ok`
- `risk_ok`
- `kill_switch_ok`
- `approval_required`
- `next_safe_action`
- `safety`
- `metadata`

## Review Rules

- By default, `allowed` is false and `live_ready` is false.
- Human approval is required.
- With human approval and all checks passing, the model can only indicate readiness to request human live micro-trade exception review.
- It does not grant broker, live, order, credential, or network capability.

## Blockers

The review blocks when:

- Human approval is missing.
- Paper or demo evidence is insufficient.
- Reconciliation is missing or mismatched.
- Drawdown exceeds limit.
- Risk failures are unresolved.
- Kill-switch proof is missing.
- Account identifier, credential, live trading, order submit, broker write, or network submit signals appear.

## Safety

The safety dict keeps:

- `paper_only: True`
- `review_only: True`
- `broker_write: False`
- `live_trading: False`
- `credentials: False`
- `real_orders: False`
- `network_submit: False`
