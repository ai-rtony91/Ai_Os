# AIOS FOREX OANDA DEMO TRADE 320 READ ONLY PL REFRESH V1 REPORT

- packet_name: AIOS FOREX OANDA DEMO TRADE 320 READ ONLY PL REFRESH V1
- repo_branch: feature/forex-oanda-demo-trade-320-read-only-pl-refresh-v1
- pr_1072_anchor: Add OANDA demo open trade monitor
- pr_1074_anchor: Add OANDA demo PL result bucket repeat proof lane
- trade_320_anchor: EUR_USD long 1 entry 1.13596 TP 321 SL 322
- broker_read_mode_used: OFFLINE_FIXTURE_ONLY
- monitor_bucket: OPEN_UNREALIZED_NEGATIVE
- pl_result_bucket: NO_PROFIT_EVIDENCE_OPEN_NEGATIVE
- repeat_proof_lane_status: NOT_STARTED_NO_PROFIT_EVIDENCE
- repeat_proof_eligible: no
- profit_evidence: no
- realized_pl: 0.0000
- unrealized_pl: -0.0004
- next_action: KEEP_MONITORING_EXISTING_TRADE_NO_NEW_ORDER
- next_packet_name: AIOS FOREX OANDA DEMO OPEN TRADE MONITOR V2
- blockers: none

## Safety Statements

- no new order placed
- no live trade placed
- no broker state modified
- no secrets written

## Machine Result

- campaign_packet: 3
- trade_id: 320
- instrument: EUR_USD
- source: offline_fixture_owner_trade_320_anchor
- broker_evidence_status: OFFLINE_FIXTURE_CLASSIFIED
- is_open: true
- is_closed: false
- no_new_order_placed: true
- no_live_trade_placed: true
- no_broker_state_modified: true
- no_secrets_written: true
