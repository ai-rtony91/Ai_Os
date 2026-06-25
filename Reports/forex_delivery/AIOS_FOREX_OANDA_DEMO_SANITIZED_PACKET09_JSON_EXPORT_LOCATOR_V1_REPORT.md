# AIOS FOREX OANDA DEMO SANITIZED PACKET 09 JSON EXPORT LOCATOR V1 REPORT

- packet_name: AIOS FOREX OANDA DEMO SANITIZED PACKET 09 JSON EXPORT LOCATOR V1
- packet_id: AIOS-FOREX-OANDA-DEMO-PACKET-12A-SANITIZED-PACKET09-JSON-EXPORT-LOCATOR-V1
- repo_branch: feature/forex-oanda-demo-sanitized-packet09-json-export-locator-v1
- export_status: SANITIZED_PACKET09_JSON_EXPORT_BLOCKED_MISSING_FIELDS
- json_written: no
- json_path: Reports/forex_delivery/oanda_demo_packet09_sanitized_owner_run_telemetry_evidence_v1.json
- sanitized_evidence_ready: no
- required_fields_present: no
- next_action: CAPTURE_REQUIRED_FIELDS_FROM_OWNER_READ_HELPER_WITHOUT_RAW_PAYLOAD

## Missing Required Fields

- realized_pl
- unrealized_pl
- open_trade_count
- open_position_count
- monitor_bucket
- result_bucket
- repeat_proof_lane_status
- broker_read_mode
- evidence_timestamp_utc
- evidence_source

## Rejected Forbidden Fields

- none

## Unsafe Audit Flags

- none

## Safety Statements

- no new order placed
- no live trade placed
- no broker state modified
- no secrets written
- raw broker payload persisted: false
- withdrawals, transfers, and money movement remain blocked

## Machine Result

- broker_read_performed: yes
- broker_network_call_performed: yes
- no_new_order_placed: true
- no_live_trade_placed: true
- no_broker_state_modified: true
- no_secrets_written: true
- raw_broker_payload_persisted: false
- withdrawal_allowed_now: false
- transfer_allowed_now: false
- money_movement_allowed_now: false
- profit_reserve_bucket_mode: INTERNAL_LEDGER_ONLY
