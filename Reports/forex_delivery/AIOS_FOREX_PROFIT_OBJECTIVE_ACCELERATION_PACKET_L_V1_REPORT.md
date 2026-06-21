# AIOS_FOREX_PROFIT_OBJECTIVE_ACCELERATION_PACKET_L_V1 Report

## Objective
Validate and rank forex strategy candidates for directional readiness and profitability gating using paper-only evidence only.

## Scope Implemented
- Added `automation/forex_engine/profit_objective_accelerator_l_v1.py` with:
  - direction support for `LONG` and `SHORT`
  - per-candidate evaluation for:
    - `strategy_id`
    - `candidate_id`
    - trade PnL list processing
    - `win_rate`
    - `expectancy`
    - `profit_factor`
    - `max_drawdown` (equity peak-to-trough, percentage)
    - `consecutive_wins`
    - `consecutive_losses`
    - `promotion_status`
  - default thresholds:
    - sample size >= 20
    - expectancy > 0
    - profit factor >= 1.25
    - max drawdown <= 10%
  - direction rejection and ranked candidate selection

## Promotion status values
- `PROFIT_OBJECTIVE_READY`
- `CONTINUE_PAPER_VALIDATION`
- `REJECT_NEGATIVE_EXPECTANCY`
- `REJECT_LOW_PROFIT_FACTOR`
- `REJECT_EXCESSIVE_DRAWDOWN`
- `REJECT_INSUFFICIENT_SAMPLE`
- `REJECT_DIRECTION_UNSUPPORTED`

## Tests added
- Added `tests/forex_engine/test_profit_objective_accelerator_l_v1.py`
- Coverage includes:
  - LONG candidate accepted
  - SHORT candidate accepted
  - unsupported direction rejected
  - negative expectancy rejection
  - low profit factor rejection
  - excessive drawdown rejection
  - insufficient sample rejection
  - profitable candidate reaches `PROFIT_OBJECTIVE_READY`
  - best-candidate ranking selects highest-quality candidate
  - consecutive win/loss profile calculations

## Safety
- Paper-only evaluator by design (`_safety()` indicates no network, no credentials, no broker or order execution).

## Validation
- `python -m pytest tests/forex_engine/test_profit_objective_accelerator_l_v1.py -q`
- `python -m py_compile automation/forex_engine/profit_objective_accelerator_l_v1.py tests/forex_engine/test_profit_objective_accelerator_l_v1.py`
