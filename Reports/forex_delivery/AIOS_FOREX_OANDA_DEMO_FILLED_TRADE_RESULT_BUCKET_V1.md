# AIOS FOREX OANDA DEMO FILLED TRADE RESULT BUCKET V1

## 1. Filled Trade Classification

RESULT_BUCKET: FILLED_PNL_UNKNOWN

The owner-run live-quote-derived OANDA demo order reached OANDA practice and produced filled-trade transaction evidence. This classifies the result as a filled demo trade with P/L not yet captured.

This is not profit proof. No realized or unrealized P/L evidence has been captured in this packet.

## 2. Pricing Snapshot Summary

- pricing_fetch_performed: true
- pricing_status_code: 200
- instrument: EUR_USD
- bid: 1.13539
- ask: 1.13599
- pricing_time: 2026-06-24T21:47:33.713676094Z

The order used live OANDA practice pricing evidence to derive stop loss and take profit immediately before the owner-run order flow.

## 3. Broker Result Summary

- script_status: LIVE_QUOTE_DERIVED_DEMO_ORDER_ATTEMPTED
- classification: LIVE_QUOTE_DERIVED_DEMO_ORDER_ATTEMPTED
- broker_network_call_performed: true
- order_placement_performed: true
- order_attempt_count: 1
- endpoint: OANDA practice/demo orders endpoint only
- live_endpoint_used: false
- HTTP_status_code: 201

The result proves broker reachability, vault-backed runtime credential use by the owner-run packet, OANDA practice pricing fetch, live quote-derived SL/TP construction, order creation, and order fill.

## 4. Transaction Evidence

- instrument: EUR_USD
- direction: BUY
- units: 1
- order_type: MARKET
- derived_stop_loss: 1.13519
- derived_take_profit: 1.13629
- client_order_id: AIOS-DEMO-LIVEQUOTE-DERIVED-OWNER-RUNTIME-001
- orderCreateTransaction_id: 319
- orderFillTransaction_id: 320
- orderCancelTransaction_id: null
- relatedTransactionIDs: 319, 320, 321, 322

## 5. Fill Status

FILL_STATUS: FILLED

An orderFillTransaction was observed with transaction id 320.

## 6. Cancel Status

- orderCancelTransaction_id: null
- cancel_reason: null

No cancel transaction or cancel reason was reported for this owner-run evidence.

## 7. Profitability Status

PROFITABILITY_STATUS: PNL_NOT_CAPTURED

No realized P/L, unrealized P/L, account balance delta, position close result, or profit evidence is captured here. This packet must not be interpreted as a profit claim.

## 8. Allocation Decision

ALLOCATION_DECISION: NO_NEXT_ALLOCATION_UNTIL_PNL_CAPTURE

No next allocation is authorized from this result bucket. Any allocation decision requires a separate read-only P/L evidence packet.

## 9. Required P/L Evidence

The next packet must capture read-only filled-trade P/L evidence without placing any order. Required evidence should include the filled trade or position state, realized or unrealized P/L if available, and sanitized proof that no credential value, account ID value, or live endpoint was printed.

## 10. No Further Order Rule

No second order is authorized by this report. No broker rerun, retry, scheduler, daemon, webhook, or autonomous order loop is authorized.

## 11. Next Safe Packet

NEXT_SAFE_PACKET: AIOS-FOREX-OANDA-DEMO-READ-ONLY-FILLED-TRADE-PL-CAPTURE-V1

The next safe action is a read-only P/L capture packet for the filled demo trade. It must not place another order and must not claim profit unless explicit P/L evidence is captured.
