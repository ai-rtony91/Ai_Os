# AIOS FOREX OANDA DEMO P/L RESULT BUCKET AND REPEAT PROOF LANE V1 REPORT

- packet_name: AIOS FOREX OANDA DEMO P/L RESULT BUCKET AND REPEAT PROOF LANE V1
- repo_branch: feature/forex-oanda-demo-pl-result-bucket-repeat-proof-v1
- pr_1072_anchor: Add OANDA demo open trade monitor
- pr_1073_anchor: Preserve OANDA demo proof chain leftovers
- current_trade_anchor: trade 320 EUR_USD long 1 entry 1.13596 TP 321 SL 322
- source_monitor_bucket: OPEN_UNREALIZED_NEGATIVE
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

- campaign_packet: 2
- trade_id: 320
- instrument: EUR_USD
- is_open: true
- is_closed: false
- no_new_order_required: true
- no_broker_state_change_required: true
