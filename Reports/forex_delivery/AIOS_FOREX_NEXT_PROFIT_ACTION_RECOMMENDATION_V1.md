# AIOS_FOREX_NEXT_PROFIT_ACTION_RECOMMENDATION_V1

## Recommendation: evidence expansion required
Generate a larger paper-only candidate sample set from local fixtures/strategies and re-score immediately.

## Next-step execution plan (paper-only only)
1. Build multi-fixture candidate stream and convert to deterministic trade outcome rows:
   - Use local candidates from:
     - `strategy_candidates.py`
     - `strategies/day_trading_breakout_v1.py`
     - `strategies/mean_reversion_v1.py`
     - `paper_forward_runner.py`
     - `paper_session_sample_generator.py`
2. Feed candidate outcomes into `profit_objective_accelerator_l_v1.evaluate_candidate_pool(...)`.
3. Require each candidate to maintain:
   - `sample_size >= 20`
   - `expectancy > 0.0`
   - `profit_factor >= 1.25`
   - `max_drawdown <= 10.0`
4. Re-run validation and syntax checks.

## Concrete commands once Python execution is available
```bash
python -m pytest tests/forex_engine/test_profit_objective_accelerator_l_v1.py -q
python -m py_compile automation/forex_engine/profit_objective_accelerator_l_v1.py tests/forex_engine/test_profit_objective_accelerator_l_v1.py
```

## Immediate safe action
- Expand local sample depth before any promotion claim: minimum 20 closed-paper trades per candidate direction/strategy path, using only local fixtures and simulator paths.

## Success condition for this packet family
- Any candidate with `promotion_status == PROFIT_OBJECTIVE_READY` and no `blocked_reasons`.
