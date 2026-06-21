# AIOS Forex Runtime Executed Top Candidate V1

## Top Candidate
- Strategy: `paper_long_run_supervisor_v2`
- Candidate: `c1-eur-buy`
- Direction: `LONG`
- Candidate count in deterministic set: `9`
- Sample size: `1`
- Expectancy: `200.00`
- Profit factor: `999.00`
- Max drawdown: `0.00`
- Win rate: `1.0000`
- Promotion status: `REJECT_INSUFFICIENT_SAMPLE`

## Execution Command Log
- `python -m pytest tests/forex_engine/test_profit_objective_accelerator_l_v1.py -q`
- `python -m py_compile automation/forex_engine/profit_objective_accelerator_l_v1.py tests/forex_engine/test_profit_objective_accelerator_l_v1.py`
- Runtime candidate execution attempt (blocked):  
  - `python -c "from automation.forex_engine import paper_long_run_supervisor, profit_objective_accelerator_l_v1, strategy_evaluation_harness, walkforward_validation_harness, paper_profitability_evaluator, portfolio_promotion_decision_engine"`
  - Failure: `windows sandbox: runner error: CreateProcessAsUserW failed: 1312`

## Blocker
- `runtime_execution_blocked_by_sandbox_launcher`
