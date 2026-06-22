# AIOS Live Runtime Executor V1

## Objective
Add the first governed live-runtime execution boundary for one single live micro-trade.

## Files
- `automation/forex_engine/live_runtime_executor_v1.py`
- `tests/forex_engine/test_live_runtime_executor_v1.py`
- `Reports/forex_delivery/AIOS_LIVE_RUNTIME_EXECUTOR_V1.md`

## Capabilities
- Builds a sanitized live runtime execution request.
- Validates command contract readiness.
- Validates protected live action authorization.
- Validates runtime context gates.
- Executes only through an injected connector when `execute_requested=True`.
- Enforces one-order-only behavior.
- Records sanitized live runtime ledger output.

## Safety
- no default live execution
- no `.env` reads
- no credential persistence
- no scheduler/daemon/webhook
- no loops
- no retries
- fake connector only in tests
- one live micro-order maximum per explicit call

## Validation
- `python -m pytest tests/forex_engine/test_live_runtime_executor_v1.py -q`
- `python -m pytest tests/forex_engine/test_live_execution_milestone_sprint.py tests/forex_engine/test_broker_threshold_sprint_v7_v9.py -q`
- `python -m pytest tests/forex_engine -q --tb=short --durations=50`
