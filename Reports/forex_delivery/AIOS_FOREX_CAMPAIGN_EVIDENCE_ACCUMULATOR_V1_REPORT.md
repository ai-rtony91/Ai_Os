# AIOS_FOREX_CAMPAIGN_EVIDENCE_ACCUMULATOR_V1_REPORT

## What changed
- Added `automation/forex_engine/campaign_evidence_accumulator.py` with `evaluate_campaign_evidence` and deterministic decision constants.
- Added `tests/forex_engine/test_campaign_evidence_accumulator.py` covering required positive, rejection, blocker, threshold, and safety paths.

## Files changed
- `automation/forex_engine/campaign_evidence_accumulator.py`
- `tests/forex_engine/test_campaign_evidence_accumulator.py`
- `Reports/forex_delivery/AIOS_FOREX_CAMPAIGN_EVIDENCE_ACCUMULATOR_V1_REPORT.md`

## Campaign evidence states
- `CAMPAIGN_EVIDENCE_READY`
- `CAMPAIGN_MORE_EVIDENCE_REQUIRED`
- `CAMPAIGN_EVIDENCE_BLOCKED`
- `CAMPAIGN_EVIDENCE_REJECTED`

## Aggregation rules
- Sum trade/session/win/loss counts across all input result mappings.
- Sum realized P/L across all inputs.
- Average expectancy, profit factor, and evidence score across values present in inputs.
- Max drawdown uses the maximum absolute drawdown observed.
- Missing lists are tolerated and treated as empty.
- Empty evidence returns `CAMPAIGN_MORE_EVIDENCE_REQUIRED`.
- Failed/blocked component statuses in profitability, walk-forward, promotion, or capital-allocation inputs map to rejected/blocked outcomes.
- Minimum threshold gates decide readiness (`>=20` trades, `>=3` sessions, expectancy `>=0.01`, profit factor `>=1.10`, drawdown `<=10.0`, evidence score `>=0.75`).
- Hard hard-fail metrics (negative expectancy, low profit factor, excessive drawdown) return `CAMPAIGN_EVIDENCE_REJECTED`.
- `campaign_demo_candidate` requires all components passing and no blockers.

## Promotion rules
- `campaign_demo_candidate` is `True` only when profitability, walk-forward, promotion, and capital-allocation inputs pass together with `CAMPAIGN_EVIDENCE_READY`.
- Any component blocker or failure clears the demo-candidate flag.

## Safety boundary
- `paper_only: True`
- `broker_connection_active: False`
- `network_access: False`
- `credentials_accessed: False`
- `order_execution_enabled: False`
- `demo_execution_active: False`
- `live_trading_authorized: False`
- `capital_allocated: False`
- `capital_allocation_modified: False`
- `operator_review_required: True`

## Validation commands
- `python -m py_compile automation/forex_engine/campaign_evidence_accumulator.py tests/forex_engine/test_campaign_evidence_accumulator.py`
- `python -m pytest tests/forex_engine/test_campaign_evidence_accumulator.py -q`

## Validation results
- `python -m pytest tests/forex_engine/test_campaign_evidence_accumulator.py -q`  
  => 15 passed in 0.07s
- `python -m py_compile automation/forex_engine/campaign_evidence_accumulator.py tests/forex_engine/test_campaign_evidence_accumulator.py`  
  => compile success

## Next safe action
- Re-run the same accumulator tests if inputs or thresholds change, then proceed to campaign supervisor integration.
