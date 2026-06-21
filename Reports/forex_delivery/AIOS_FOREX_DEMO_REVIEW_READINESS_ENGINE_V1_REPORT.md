# AIOS Forex Demo Review Readiness Engine V1

## Scope
- Branch: `feature/forex-demo-review-readiness-engine-v1`
- Mission: determine governed readiness of portfolio promotion candidates for demo review.

## What was implemented
- Added `automation/forex_engine/demo_review_readiness_engine.py` with required output:
  - `readiness_completed`
  - `demo_review_ready`
  - `portfolio_promotion_status`
  - `stable_winner`
  - `readiness_reasons`
  - `blocked_reasons`
  - `next_safe_action`
  - `safety`
- Readiness rules implemented:
  - Must originate from `PORTFOLIO_DEMO_REVIEW_CANDIDATE`.
  - Requires stable winner present.
  - Requires winner consistency >= threshold.
  - Rejects when blocked reasons exist.
  - Rejects unsafe or negative-evidence winners.
  - Preserves paper-only safety constraints.
- Supports direct `promotion_result` input and auto-fallback execution from evidence batches through the portfolio promotion/evidence pipeline.

## Validation
- `python -m pytest tests/forex_engine/test_demo_review_readiness_engine.py -q`
- `python -m py_compile automation/forex_engine/demo_review_readiness_engine.py tests/forex_engine/test_demo_review_readiness_engine.py`

## Test cases covered
- demo review ready
- more evidence required
- portfolio rejected
- unstable winner blocked
- unsafe evidence blocked
- missing stable winner blocked
- deterministic output
- safety source scan

## Safety posture
- Paper-only execution only.
- No brokers, credentials, network, live trading, demo execution activation, or capital-allocation changes.
