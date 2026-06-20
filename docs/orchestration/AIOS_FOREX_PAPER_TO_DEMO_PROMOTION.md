# AIOS Forex Paper-To-Demo Promotion

## Purpose

`automation/forex_engine/paper_to_demo_promotion.py` decides whether AIOS paper evidence is mature enough to proceed with demo-readonly, demo order mapping, and demo reconciliation workflows.

This gate does not submit demo orders, submit live orders, perform broker writes, read credentials, or call broker/network APIs.

## Inputs

- Session replay summary.
- Evidence ledger validation.
- Long-run supervisor summary.
- Self-improvement review result.
- Demo connector read-only result.
- Demo order mapping result.
- Demo reconciliation result.
- Limits.

## Output

The promotion decision includes:

- `allowed`
- `decision`
- `blocked_reason`
- `blocked_reasons`
- `warnings`
- `mode: PAPER_TO_DEMO_PROMOTION_ONLY`
- `paper_only: True`
- `demo_promotion_ready`
- `evidence_score`
- `minimum_trade_count_met`
- `minimum_session_count_met`
- `risk_compliance_met`
- `drawdown_within_limit`
- `reconciliation_ready`
- `readonly_ready`
- `mapping_ready`
- `missing_requirements`
- `safety`
- `next_safe_action`
- `metadata`

## Blockers

The gate blocks when:

- Trade count is below threshold.
- Session count is below threshold.
- Evidence ledger is missing or failed.
- Session replay is missing.
- Risk failures are unresolved.
- Drawdown exceeds limit.
- Demo read-only, mapping, or reconciliation readiness failed.
- Account identifier material is present.
- Credential-loaded flags are present.
- Live trading, broker write, order submit, network submit, or requested live/broker actions appear.

## Safety

The safety dict denies broker write, live trading, credentials, real orders, and network submit. Promotion only authorizes continuation into bounded demo-readonly/order-mapping/reconciliation workflows.
