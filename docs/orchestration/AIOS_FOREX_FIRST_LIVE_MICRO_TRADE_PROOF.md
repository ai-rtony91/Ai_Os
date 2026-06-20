# AIOS Forex First Live Micro Trade Proof

## Purpose

`automation/forex_engine/first_live_micro_trade_proof.py` builds a protected proof/checklist packet for future human review of a first live micro-trade exception.

This model is proof only. It does not submit orders, connect to broker APIs, read credentials, store account identifiers, enable live trading, or create an execution route.

## Inputs

- Live readiness review.
- Paper-to-demo promotion decision.
- Demo multi-trade runner plan.
- Demo reconciliation result.
- Risk limits.
- Human approval record.

## Output

The proof packet includes:

- `allowed: False`
- `decision`
- `proof_complete`
- `live_trade_allowed: False`
- `broker_submit_allowed: False`
- `required_evidence`
- `missing_evidence`
- `risk_limits`
- `micro_trade_size_cap`
- `kill_switch_required: True`
- `rollback_required: True`
- `approval_required: True`
- `safety`
- `next_safe_action`

## Proof Rules

- `proof_complete` may be true only when all required evidence and human approval records are present.
- Even when `proof_complete` is true, live trading and broker submit remain false.
- This packet only supports human review of a future exception request.

## Blockers

The proof blocks on:

- Missing human approval.
- Missing kill switch proof.
- Missing rollback plan.
- Missing reconciliation evidence.
- Excessive risk limits.
- Missing required evidence.
- Account identifier material.
- Credential material.
- Broker write, order submit, live trading, or network submit signals.

## Safety

The safety dict keeps:

- `paper_only: True`
- `proof_only: True`
- `broker_write: False`
- `live_trading: False`
- `credentials: False`
- `real_orders: False`
- `network_submit: False`
