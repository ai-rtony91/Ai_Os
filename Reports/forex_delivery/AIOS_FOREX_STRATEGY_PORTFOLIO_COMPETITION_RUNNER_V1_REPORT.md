# AIOS FOREX Strategy Portfolio Competition Runner V1

## Scope
- Lane: `feature/forex-strategy-portfolio-competition-runner-v1`
- Mission: Build canonical paper-only portfolio competition runner for strategy selection.

## What was implemented
- Added `automation/forex_engine/strategy_portfolio_competition_runner.py` with:
  - `run_strategy_portfolio_competition(strategy_competitors=None)` returning the required canonical output shape.
  - Deterministic competitor evaluation and ranking flow.
  - Evaluation inputs per strategy via:
    - `evaluate_strategy`
    - optional `validate_walkforward_strategy`
    - optional `evaluate_market_regimes`
  - Paper-only safety enforcement and rejection of unsafe or malformed entries.
  - Blocking logic for negative expectancy and unsafe/safety-failing candidates.
  - Winner selection from ranked list only when portfolio-ready conditions are met.

- Added `tests/forex_engine/test_strategy_portfolio_competition_runner.py` with coverage for:
  - breakout winner case
  - mean-reversion winner case
  - both rejected
  - unsafe strategy rejection
  - deterministic output
  - safety source scan (no broker/network/file/env credential access)

## Verification
- `python -m pytest tests/forex_engine/test_strategy_portfolio_competition_runner.py -q`
- `python -m py_compile automation/forex_engine/strategy_portfolio_competition_runner.py tests/forex_engine/test_strategy_portfolio_competition_runner.py`

## Notes
- No broker adapters, credentials, live execution toggles, demo activation, or capital-allocation changes are introduced.
