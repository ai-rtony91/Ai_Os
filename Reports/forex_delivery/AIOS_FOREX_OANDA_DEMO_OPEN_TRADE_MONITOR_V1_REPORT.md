# AIOS FOREX OANDA DEMO OPEN TRADE MONITOR V1 REPORT

- packet_name: AIOS FOREX OANDA DEMO OPEN TRADE MONITOR V1
- repo_branch: feature/forex-oanda-demo-open-trade-monitor-v1
- prior_proof_chain_anchor: PR #1071 finalized OANDA demo proof chain
- known_owner_run_trade_anchor: trade 320 EUR/USD long 1 entry 1.13596 TP 321 SL 322
- current_bucket_result: OPEN_UNREALIZED_NEGATIVE
- profit_evidence: false
- trade_open: true
- trade_closed: false
- realized_pl: 0.0000
- unrealized_pl: -0.0004
- total_pl: -0.0004
- blockers: none
- next_packet_recommendation: AIOS FOREX OANDA DEMO P/L RESULT BUCKET AND REPEAT PROOF LANE V1

## Safety Statements

- no new order was placed
- no live trade was placed
- no secrets were written
- no broker state was modified by this monitor
- no close, replace, TP, SL, unit, leverage, or account change was performed

## Machine Result

- status_bucket: OPEN_UNREALIZED_NEGATIVE
- trade_id: 320
- instrument: EUR_USD
- side: long
- units: 1
- entry_price: 1.13596
- current_price: UNKNOWN
- take_profit_order_id: 321
- stop_loss_order_id: 322
- open_trade_count: 1
- open_position_count: 1
- evidence_timestamp_utc: UNKNOWN
- evidence_source: owner_packet_anchor_oanda_demo_trade_320
