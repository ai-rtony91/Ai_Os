# AIOS Broker Demo Data Adapter V3

## Objective
- Add a protected, offline-default demo data adapter simulation layer.
- Normalize broker-demo-style account, instrument, and quote fixtures without live trading, credentials, network calls, or order execution.

## Files added
- `automation/forex_engine/broker_demo_data_adapter_v3.py`
- `tests/forex_engine/test_broker_demo_data_adapter_v3.py`
- `Reports/forex_delivery/AIOS_BROKER_DEMO_DATA_ADAPTER_V3.md`

## Capabilities
- Account snapshot normalization:
  - requires balance, equity, and margin_available
  - rejects negative financial fields
  - rejects account identifier presence
  - removes sensitive fields from output
- Instrument normalization:
  - accepts forex-like symbols such as `EUR_USD` and `EURUSD`
  - rejects live-route markers
  - validates unit and precision placeholders
- Quote normalization:
  - validates bid and ask
  - calculates spread
  - rejects stale timestamps
  - blocks excessive spread
- Risk-readiness mapping:
  - combines account, instrument, quote, and gate state
  - blocks kill switch, max-loss gate, and daily-stop failures
  - returns deterministic verdicts:
    - `BROKER_DEMO_DATA_READY`
    - `BROKER_DEMO_DATA_BLOCKED`
    - `BROKER_DEMO_DATA_INVALID`
    - `BROKER_DEMO_DATA_SANITIZED`

## Safety proof
- no live trading
- no order execution
- no broker credentials
- no `.env` reads
- no network calls
- no scheduler, daemon, webhook, or background execution
- no raw account IDs persisted
- no raw broker payload persisted
- output is sanitized

## Latency budget
- account normalization: 4 ms
- instrument normalization: 4 ms
- quote normalization: 5 ms
- spread calculation: 1 ms
- risk-readiness mapping: 3 ms
- network latency: excluded offline default

## Validation commands
- `python -m pytest tests/forex_engine/test_broker_demo_data_adapter_v3.py -q`
- `python -m pytest tests/forex_engine/test_broker_demo_effectiveness_v2.py tests/forex_engine/test_broker_integration_effectiveness_v1.py -q`
- `python -m pytest tests/forex_engine -q --tb=short --durations=50`
