# AIOS OANDA Live Runtime Connector V2

## Objective
Add the OANDA live runtime connector contract compatible with Live Runtime Executor V1.

## Files
- `automation/forex_engine/oanda_live_runtime_connector_v2.py`
- `tests/forex_engine/test_oanda_live_runtime_connector_v2.py`
- `Reports/forex_delivery/AIOS_OANDA_LIVE_RUNTIME_CONNECTOR_V2.md`

## Capabilities
- Validates live connector runtime config.
- Provides `OandaLiveRuntimeConnectorV2`.
- Exposes attributes required by `live_runtime_executor_v1`.
- Uses injected transport only.
- Allows exactly one live micro-order call.
- Blocks second order.
- Sanitizes broker responses.

## Safety
- no default live execution
- no `.env` reads
- no credential persistence
- no account ID persistence
- no scheduler/daemon/webhook
- no loops
- no retries
- tests use fake transport only

## Validation
- `python -m pytest tests/forex_engine/test_oanda_live_runtime_connector_v2.py -q`
- `python -m pytest tests/forex_engine/test_live_runtime_executor_v1.py tests/forex_engine/test_live_execution_milestone_sprint.py -q`
- `python -m pytest tests/forex_engine -q --tb=short --durations=50`
