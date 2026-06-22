# AIOS Broker Demo Review Packet V5A

## Objective
Build a deterministic, offline-default operator review packet from V4 decision output for protected broker-demo readiness review.

## Scope
- No live trading.
- No order execution.
- No broker credentials.
- No `.env` reads.
- No network calls.
- No scheduler/daemon/webhook execution.
- In-memory fixture/demo data only.
- No raw broker payload persistence.

## Files Added
- `automation/forex_engine/broker_demo_review_packet_v5.py`
- `tests/forex_engine/test_broker_demo_review_packet_v5.py`
- `Reports/forex_delivery/AIOS_BROKER_DEMO_REVIEW_PACKET_V5.md`

## API

`build_broker_demo_review_packet(decision, metadata=None)`

Returns a deterministic packet dictionary with:
- `packet_schema`
- `packet_status`
- `decision`
- `ready`
- `blockers`
- `evidence_summary`
- `safety_summary`
- `approval_required`
- `next_safe_action`
- `review_checklist`
- `sanitized_metadata`
- `latency_budget`

Supported statuses:
- `BROKER_DEMO_REVIEW_PACKET_READY`
- `BROKER_DEMO_REVIEW_PACKET_BLOCKED`
- `BROKER_DEMO_REVIEW_PACKET_INVALID`
- `BROKER_DEMO_REVIEW_PACKET_REVIEW_REQUIRED`

Review checklist fields:
- `integration_contract_present`
- `connector_probe_present`
- `demo_data_present`
- `safety_gates_clear`
- `no_live_trading`
- `no_order_execution`
- `no_credentials`
- `no_network_calls`
- `no_env_reads`
- `human_approval_required`

## Validation
- `python -m pytest tests/forex_engine/test_broker_demo_review_packet_v5.py -q`
- `python -m pytest tests/forex_engine/test_broker_demo_decision_bridge_v4.py tests/forex_engine/test_broker_demo_data_adapter_v3.py tests/forex_engine/test_broker_integration_effectiveness_v1.py -q`
- `python -m pytest tests/forex_engine -q --tb=short --durations=50`

## Safety statement
- no live trading
- no broker credentials
- no `.env` reads
- no network calls
- no order execution
- no scheduler/daemon/webhook

## Blocking and readiness rules
- Invalid if `decision` missing.
- Blocked if V4 decision is `BROKER_DEMO_DECISION_BLOCKED`.
- Ready only if V4 ready is `True` and unsafe flags are all `False`.
- Review required if V4 decision is `BROKER_DEMO_DECISION_REVIEW_REQUIRED`.
- Human approval is required prior to any protected demo progression.
- `network_latency_ms` is fixed to `excluded_offline_default`.
