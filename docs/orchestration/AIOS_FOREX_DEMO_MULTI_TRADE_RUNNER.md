# AIOS Forex Demo Multi-Trade Runner

## Purpose

`automation/forex_engine/demo_multi_trade_runner.py` builds a plan-only demo multi-trade run from approved promotion, read-only, mapping, and reconciliation outputs.

This module produces `DEMO_RUN_PLAN` evidence only. It does not submit orders, close trades, call broker APIs, read credentials, use account identifiers, or perform network work.

## Inputs

- Paper-to-demo promotion decision.
- Mapped demo order intents.
- Sanitized demo read-only snapshot.
- Demo reconciliation result.
- Limits.

## Output

The runner returns:

- `allowed`
- `decision`
- `blocked_reason`
- `blocked_reasons`
- `warnings`
- `mode: DEMO_RUN_PLAN_ONLY`
- `paper_only: True`
- `demo_readonly: True`
- `submit_enabled: False`
- `broker_write_enabled: False`
- `live_trading: False`
- `selected_intents`
- `rejected_intents`
- `run_id`
- `idempotency_keys`
- `max_demo_orders`
- `safety`
- `next_safe_action`
- `metadata`

The nested `demo_run_plan` mirrors the selected/rejected intent evidence and keeps all execution flags false.

## Blockers

The runner blocks when:

- Promotion is not allowed.
- Read-only snapshot is not allowed.
- Reconciliation is not ready.
- Any intent enables submit, broker write, or live trading.
- Credential or account identifier material is present.
- Duplicate idempotency keys are present.
- Units are invalid.
- Pair, side, or order type is unsupported.
- Maximum demo order cap is exceeded.

## Safety

The safety dict denies submit, broker write, live trading, credentials, real orders, and network submit. This component is plan-only and does not perform broker or network actions.
