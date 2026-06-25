# AIOS Forex Operator Next Trade Review Composer V1 Report

## Packet

- packet_id: AIOS-FOREX-OPERATOR-NEXT-TRADE-REVIEW-COMPOSER-LOCAL-APPLY-V1
- mode: LOCAL_APPLY
- lane: forex-operator-next-trade-review-composer

## Files Created Or Changed

- `automation/forex_engine/operator_next_trade_review_composer_v1.py`
- `tests/forex_engine/test_operator_next_trade_review_composer_v1.py`
- `Reports/forex_delivery/AIOS_FOREX_OPERATOR_NEXT_TRADE_REVIEW_COMPOSER_V1_REPORT.md`

## What This Does For Anthony Up Front

This composer gives Anthony one plain review/not-review answer instead of forcing him to read several technical reports. It reduces guessing, protects attention and capital, and keeps broker action blocked until a separate explicit owner approval exists.

## Operator Decisions

- `REVIEW_READY_FOR_OWNER_APPROVAL`
- `BLOCK_REVIEW_MISSING_PROOF`
- `BLOCK_REVIEW_WEAK_TRADE_EVIDENCE`
- `BLOCK_REVIEW_LATENCY_UNKNOWN`
- `BLOCK_REVIEW_RISK_OR_SAFETY_NOT_CLEAR`
- `BLOCK_REVIEW_INVALID_EVIDENCE`

Example front-end answers:

- `Blocked: AIOS does not have enough proof for you to review this trade.`
- `Blocked: timing is not clear enough for you to review this trade.`
- `Review-ready: evidence is complete enough for Anthony to review, but no broker action is authorized.`

## Required Input Sections

1. `loss_review_metrics_gate`
2. `trade_latency_baseline`
3. `operator_context`

`loss_review_metrics_gate` may be either raw evidence for the loss-review metrics gate or a precomputed result from that gate.

`trade_latency_baseline` may be either raw evidence for the trade latency baseline reporter or a precomputed result from that reporter.

Required `operator_context` fields:

- `operator_name`
- `instrument`
- `direction`
- `strategy_name`
- `candidate_id`
- `last_trade_id`
- `last_trade_result`
- `wants_next_demo_review`

## Safety Boundary

- local-only: yes
- broker calls: blocked
- credential access: blocked
- `.env` access: blocked
- order placement: blocked
- order close/cancel/replace: blocked
- live endpoint: blocked
- network use: blocked
- owner approval: still required
- commit, push, PR, merge: blocked

## Validator Commands

```powershell
python -m pytest tests/forex_engine/test_operator_next_trade_review_composer_v1.py -q
python -m py_compile automation/forex_engine/operator_next_trade_review_composer_v1.py tests/forex_engine/test_operator_next_trade_review_composer_v1.py
```

## Stop Point

Stop after local files are created or changed and validators are attempted. Do not stage, commit, push, create a PR, merge, call brokers, use credentials, or place trades.

## Next Safe Action

Review the local composer output with sample evidence, then use a separate protected-action packet if Anthony wants these files staged or committed.
