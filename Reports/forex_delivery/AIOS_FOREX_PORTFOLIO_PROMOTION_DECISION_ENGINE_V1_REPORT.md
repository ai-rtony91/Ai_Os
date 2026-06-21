# AIOS Forex Portfolio Promotion Decision Engine V1

## Scope
- Branch: `feature/forex-portfolio-promotion-decision-engine-v1`
- Mission: convert portfolio evidence accumulation results into governed promotion decisions.

## What was implemented
- Added `automation/forex_engine/portfolio_promotion_decision_engine.py` with decision output:
  - `decision_completed`
  - `portfolio_promotion_status`
  - `demo_review_candidate`
  - `stable_winner`
  - `winner_consistency_rate`
  - `blocked_reasons`
  - `promotion_reasons`
  - `next_safe_action`
  - `safety`
- Decision logic enforces:
  - `Demo review` only when:
    - a stable winner exists
    - winner consistency is sufficient
    - accumulation is portfolio-ready
    - no blocked/unsafe/negative evidence flags
  - `More evidence` when batches are insufficient or winner consistency is below threshold.
  - `Reject` when no safe winner exists or winner evidence is unsafe/blocked.
- Paper-only safety posture is enforced in module and output.

## Tests
- `python -m pytest tests/forex_engine/test_portfolio_promotion_decision_engine.py -q`
- `python -m py_compile automation/forex_engine/portfolio_promotion_decision_engine.py tests/forex_engine/test_portfolio_promotion_decision_engine.py`

## Test coverage
- demo review candidate
- more evidence required
- rejected no safe winner
- rejected unsafe evidence
- unstable winner blocked
- deterministic output
- safety source scan
