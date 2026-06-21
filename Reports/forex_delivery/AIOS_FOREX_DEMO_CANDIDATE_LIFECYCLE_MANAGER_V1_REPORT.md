# AIOS_FOREX_DEMO_CANDIDATE_LIFECYCLE_MANAGER_V1_REPORT

## What changed
- Added `automation/forex_engine/demo_candidate_lifecycle_manager.py` with deterministic lifecycle orchestration for demo-candidate records.
- Added `tests/forex_engine/test_demo_candidate_lifecycle_manager.py` with required positive/negative and safety transition coverage.

## Files changed
- `automation/forex_engine/demo_candidate_lifecycle_manager.py`
- `tests/forex_engine/test_demo_candidate_lifecycle_manager.py`
- `Reports/forex_delivery/AIOS_FOREX_DEMO_CANDIDATE_LIFECYCLE_MANAGER_V1_REPORT.md`

## Lifecycle states
- `DEMO_CANDIDATE_CREATED`
- `DEMO_CANDIDATE_ACTIVE`
- `DEMO_CANDIDATE_PAUSED`
- `DEMO_CANDIDATE_REVOKED`
- `DEMO_CANDIDATE_APPROVED_FOR_DEMO_VALIDATION`

## Transition rules
- If `campaign_status == CAMPAIGN_DEMO_CANDIDATE`, a new candidate is created deterministically as `DEMO_CANDIDATE_CREATED`.
- With previous lifecycle state:
  - `CREATED -> ACTIVE`
  - `ACTIVE -> APPROVED_FOR_DEMO_VALIDATION`
  - `ACTIVE -> PAUSED`
  - `ACTIVE -> REVOKED`
  - `REVOKED ->` no automatic transitions
- Any invalid transition records blocker `invalid_transition` and keeps state unchanged.

## History model
- History entries include:
  - `timestamp` (deterministic sha hash)
  - `previous_state`
  - `new_state`
  - `reason`
  - `campaign_status`
- Initial creation always records an initial history entry when no prior history exists.

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
- `python -m pytest tests/forex_engine/test_demo_candidate_lifecycle_manager.py -q`
- `python -m py_compile automation/forex_engine/demo_candidate_lifecycle_manager.py tests/forex_engine/test_demo_candidate_lifecycle_manager.py`

## Validation results
- `python -m pytest tests/forex_engine/test_demo_candidate_lifecycle_manager.py -q`  
  => 11 passed in 0.09s
- `python -m py_compile automation/forex_engine/demo_candidate_lifecycle_manager.py tests/forex_engine/test_demo_candidate_lifecycle_manager.py`  
  => compile success

## Next safe action
- Feed campaign supervisor outputs into `evaluate_demo_candidate_lifecycle` and audit transition outputs before any downstream demo workflow step.
