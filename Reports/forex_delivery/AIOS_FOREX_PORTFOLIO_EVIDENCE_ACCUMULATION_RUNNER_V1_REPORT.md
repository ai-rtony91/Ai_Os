# AIOS Forex Portfolio Evidence Accumulation Runner V1

## Scope
- Branch: `feature/forex-portfolio-evidence-accumulation-runner-v1`
- Mission: finalize the portfolio evidence accumulation runner with multi-batch competition support.

## What was implemented
- Added `automation/forex_engine/portfolio_evidence_accumulation_runner.py` with required output shape:
  - `accumulation_completed`
  - `batches_evaluated`
  - `competition_results`
  - `stable_winner`
  - `winner_consistency_rate`
  - `portfolio_ready`
  - `blocked_reasons`
  - `next_safe_action`
  - `safety`
- Implemented deterministic multi-batch workflow:
  - Runs `run_strategy_portfolio_competition` for each evidence batch.
  - Tracks per-batch winners and aggregates winner frequency.
  - Computes winner consistency rate.
  - Selects a stable winner only when repeatable and above threshold.
- Added safety enforcement for each winner and blocked unsafe candidates from final readiness.
- Added blocking logic for:
  - insufficient batches
  - no stable winner
  - winner consistency below threshold
  - no safe strategies remaining
  - all batches effectively failed

## Tests
- `python -m pytest tests/forex_engine/test_portfolio_evidence_accumulation_runner.py -q`
- `python -m py_compile automation/forex_engine/portfolio_evidence_accumulation_runner.py tests/forex_engine/test_portfolio_evidence_accumulation_runner.py`

## Test cases covered
- stable winner across batches
- unstable winners blocked
- all batches rejected
- unsafe strategy blocked
- insufficient batches
- deterministic output
- safety source scan

## Safety posture
- Paper-only execution only.
- No broker access, credentials, network, live trading, demo execution, or capital-allocation changes.
