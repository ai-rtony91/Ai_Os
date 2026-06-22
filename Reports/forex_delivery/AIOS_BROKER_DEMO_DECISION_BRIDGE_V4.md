# AIOS Broker Demo Decision Bridge V4A

## Objective
Implement a protected, offline-default decision bridge that combines broker integration
readiness evidence (V1), connector readiness evidence (V2), and normalized demo data
readiness (V3) into one deterministic verdict for demo review readiness.

## Scope
- No live trading.
- No order execution.
- No broker credentials.
- No `.env` reads.
- No network calls.
- No scheduler/daemon/webhook execution.
- In-memory fixtures only.
- No raw broker payload or account id persistence.

## Files Added
- `automation/forex_engine/broker_demo_decision_bridge_v4.py`
- `tests/forex_engine/test_broker_demo_decision_bridge_v4.py`
- `Reports/forex_delivery/AIOS_BROKER_DEMO_DECISION_BRIDGE_V4.md`

## API

`evaluate_broker_demo_decision(integration, connector_probe, demo_data, gates=None)`

Returns:
- `decision`: one of:
  - `BROKER_DEMO_DECISION_READY`
  - `BROKER_DEMO_DECISION_BLOCKED`
  - `BROKER_DEMO_DECISION_INVALID`
  - `BROKER_DEMO_DECISION_REVIEW_REQUIRED`
- `ready`: boolean
- `blockers`: tuple of blocker reasons
- `evidence_summary`: per-source state (`integration`, `connector`, `demo_data`, `gates`)
- `safety_summary`: unsafe-flag map and count
- `next_safe_action`: deterministic next step
- `latency_budget`: local processing buckets with `network_latency_ms` set to `excluded_offline_default`

## Deterministic blocking rules
- Integration evidence missing or not ready.
- Connector probe missing or not ready.
- Demo data missing or not ready.
- `kill_switch_enabled` true.
- `max_loss_gate_clear` false.
- `daily_stop_clear` false.
- Any unsafe flags true:
  - `live_trading`, `order_execution`, `credentials_read`, `env_read`,
    `network_calls`, `scheduler_daemon_webhook`,
    `raw_broker_payload_persisted`, `account_id_present`.

## Latency budget
- `integration_evidence_read_ms`
- `connector_probe_read_ms`
- `demo_data_read_ms`
- `safety_gate_eval_ms`
- `decision_mapping_ms`
- `network_latency_ms: "excluded_offline_default"`

## Validation runbook
```
python -m pytest tests/forex_engine/test_broker_demo_decision_bridge_v4.py -q
python -m pytest tests/forex_engine/test_broker_demo_data_adapter_v3.py tests/forex_engine/test_broker_demo_effectiveness_v2.py tests/forex_engine/test_broker_integration_effectiveness_v1.py -q
python -m pytest tests/forex_engine -q --tb=short --durations=50
```

## Safety statement
- no live trading
- no broker credentials
- no `.env` reads
- no network calls
- no order execution
- no scheduler/daemon/webhook
