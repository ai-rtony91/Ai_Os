# AIOS Broker Demo Rehearsal Runner V6A

## Objective
Build a deterministic, offline-default rehearsal runner that consumes a V5 review packet and produces a protected rehearsal verdict.

## Scope
- No live trading.
- No order execution.
- No broker credentials.
- No `.env` reads.
- No network calls.
- No scheduler/daemon/webhook execution.
- In-memory fixture/demo data only.
- No raw broker payload persistence.
- No account id persistence.

## Files Added
- `automation/forex_engine/broker_demo_rehearsal_runner_v6.py`
- `tests/forex_engine/test_broker_demo_rehearsal_runner_v6.py`
- `Reports/forex_delivery/AIOS_BROKER_DEMO_REHEARSAL_RUNNER_V6.md`

## API

`run_broker_demo_rehearsal(review_packet, operator_ack=None)`

Returns a deterministic dictionary with:
- `rehearsal_schema`
- `rehearsal_status`
- `ready`
- `blockers`
- `packet_summary`
- `operator_ack_summary`
- `safety_summary`
- `next_safe_action`
- `latency_budget`

Supported statuses:
- `BROKER_DEMO_REHEARSAL_READY`
- `BROKER_DEMO_REHEARSAL_BLOCKED`
- `BROKER_DEMO_REHEARSAL_INVALID`
- `BROKER_DEMO_REHEARSAL_REVIEW_REQUIRED`

Next action mapping:
- ready -> `prepare_protected_demo_connection_preflight`
- blocked -> `resolve_rehearsal_blockers`
- invalid -> `repair_review_packet`
- review_required -> `complete_human_rehearsal_acknowledgement`

Blocking rules:
- invalid if review packet missing
- invalid if packet schema/status missing
- blocked if V5 packet is blocked
- review_required if approval required but missing or incomplete operator acknowledgement
- ready only when V5 packet ready is true and all required operator ack flags are true
- blocked if any unsafe flags are true:
  - `live_trading`
  - `order_execution`
  - `credentials_read`
  - `env_read`
  - `network_calls`
  - `scheduler_daemon_webhook`
  - `raw_broker_payload_persisted`
  - `account_id_present`

Latency budget:
- `packet_read_ms`
- `operator_ack_eval_ms`
- `safety_gate_eval_ms`
- `rehearsal_mapping_ms`
- `network_latency_ms: excluded_offline_default`

## Required operator acknowledgement fields
- `reviewed_by_human`
- `simulation_only_ack`
- `no_live_trading_ack`
- `no_order_execution_ack`
- `no_credentials_ack`
- `no_network_ack`

## Validation
- `python -m pytest tests/forex_engine/test_broker_demo_rehearsal_runner_v6.py -q`
- `python -m pytest tests/forex_engine/test_broker_demo_review_packet_v5.py tests/forex_engine/test_broker_demo_decision_bridge_v4.py tests/forex_engine/test_broker_demo_data_adapter_v3.py -q`
- `python -m pytest tests/forex_engine -q --tb=short --durations=50`
