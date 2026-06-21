# AIOS_FOREX_STRATEGY_CAMPAIGN_SUPERVISOR_V1_REPORT

## What changed
- Added `automation/forex_engine/strategy_campaign_supervisor.py` as a deterministic campaign orchestration layer over:
  - campaign evidence
  - promotion workflow
  - capital allocation gate
- Added `tests/forex_engine/test_strategy_campaign_supervisor.py` for all required behavior paths.
- Added validation report capturing execution and decision outputs.

## Files changed
- `automation/forex_engine/strategy_campaign_supervisor.py`
- `tests/forex_engine/test_strategy_campaign_supervisor.py`
- `Reports/forex_delivery/AIOS_FOREX_STRATEGY_CAMPAIGN_SUPERVISOR_V1_REPORT.md`

## Supervisor states
- `CAMPAIGN_CONTINUE`
- `CAMPAIGN_MORE_EVIDENCE_REQUIRED`
- `CAMPAIGN_DEMO_CANDIDATE`
- `CAMPAIGN_BLOCKED`
- `CAMPAIGN_REJECTED`

## Decision rules
- `CAMPAIGN_BLOCKED` when capital allocation is explicitly blocked/fails required controls.
- `CAMPAIGN_REJECTED` when:
  - campaign evidence is rejected
  - expectancy is below minimum
  - profit factor is below minimum
  - drawdown exceeds maximum limit
  - promotion workflow rejects advancement
- `CAMPAIGN_MORE_EVIDENCE_REQUIRED` when campaign evidence is not yet ready and no hard rejection/block.
- `CAMPAIGN_DEMO_CANDIDATE` only when evidence is ready, promotion passes, capital allocation passes, no blockers remain, and positive profitability metrics are within thresholds.
- Otherwise `CAMPAIGN_CONTINUE` (fallback).

## Campaign metrics
- `trade_count`
- `session_count`
- `expectancy`
- `profit_factor`
- `drawdown`
- `evidence_score`
- `promotion_status`
- `capital_allocation_status`

## Safety boundary
- `paper_only = True`
- `broker_connection_active = False`
- `network_access = False`
- `credentials_accessed = False`
- `order_execution_enabled = False`
- `demo_execution_active = False`
- `live_trading_authorized = False`
- `capital_allocated = False`
- `capital_allocation_modified = False`
- `operator_review_required = True`

## Validation commands
- `python -m pytest tests/forex_engine/test_strategy_campaign_supervisor.py -q`
- `python -m py_compile automation/forex_engine/strategy_campaign_supervisor.py tests/forex_engine/test_strategy_campaign_supervisor.py`

## Validation results
- `python -m pytest tests/forex_engine/test_strategy_campaign_supervisor.py -q`  
  => 11 passed in 0.06s
- `python -m py_compile automation/forex_engine/strategy_campaign_supervisor.py tests/forex_engine/test_strategy_campaign_supervisor.py`  
  => compile success

## Next safe action
- Use `evaluate_campaign_supervisor(...)` results to feed higher-level campaign orchestration controls while retaining operator review gates.
