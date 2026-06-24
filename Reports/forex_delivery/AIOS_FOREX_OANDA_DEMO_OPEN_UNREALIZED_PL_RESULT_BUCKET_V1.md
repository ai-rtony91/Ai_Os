# AIOS Forex OANDA Demo Open Unrealized PL Result Bucket V1

## 1. P/L Capture Classification

RESULT_BUCKET: FILLED_OPEN_UNREALIZED_NEGATIVE

Required classification fields:

- FILL_STATUS: FILLED_OPEN
- REALIZED_PL_STATUS: ZERO_REALIZED_PL
- UNREALIZED_PL_STATUS: NEGATIVE_UNREALIZED_PL
- PROFITABILITY_STATUS: OPEN_TRADE_NOT_PROFIT_PROVEN
- ALLOCATION_DECISION: NO_NEXT_ALLOCATION_WHILE_TRADE_OPEN
- NEXT_SAFE_PACKET: AIOS-FOREX-OANDA-DEMO-OPEN-TRADE-MONITOR-READ-ONLY-V1

The owner-run read-only capture found the filled EUR_USD demo trade remains open. Realized P/L is zero and unrealized P/L is negative at capture time.

## 2. Open Trade Evidence

Sanitized owner-provided open trade evidence:

- trade_id: 320
- instrument: EUR_USD
- state: OPEN
- currentUnits: 1
- price: 1.13596
- realizedPL: 0.0000
- unrealizedPL: -0.0004
- trueUnrealizedPL: -0.0004
- order_placement_performed: false
- order_close_performed: false
- mutation_performed: false

This supports `FILLED_OPEN` status and negative unrealized P/L. It does not support realized profit.

## 3. Position Evidence

Sanitized owner-provided account and position evidence:

- account_details_status_code: 200
- account_summary_status_code: 200
- openTrades_status_code: 200
- openPositions_status_code: 200
- account_openTradeCount: 1
- account_openPositionCount: 1
- pendingOrderCount: 2
- live_endpoint_used: false

The read-only account, summary, open-trades, and open-positions responses returned enough evidence to classify the trade as open with current unrealized P/L.

## 4. Pending TP/SL Evidence

Pending protective order evidence:

- takeProfitOrderID: 321
- takeProfitOrder_state: PENDING
- stopLossOrderID: 322
- stopLossOrder_state: PENDING

The TP and SL orders remain pending while the trade is open. This means the next safe action is read-only monitoring until the trade closes or reaches a clearly classified state.

## 5. Transactions Window Blocker

Transactions window result:

- transactions_window_status_code: 416
- transactions_window_errorCode: INVALID_TIME_RANGE

The transactions-window read did not return usable transaction detail because OANDA returned `INVALID_TIME_RANGE`. This does not block the open/unrealized classification because account details, summary, openTrades, and openPositions returned sufficient read-only evidence.

## 6. Profitability Status

PROFITABILITY_STATUS: OPEN_TRADE_NOT_PROFIT_PROVEN

Profitability evidence:

- realizedPL: 0.0000
- unrealizedPL: -0.0004
- trueUnrealizedPL: -0.0004
- profit_claimed: false
- realized_profit_claimed: false
- 120_percent_claimed: false

This is not profit proof. The trade is still open and its unrealized P/L was negative at capture time.

## 7. Allocation Decision

ALLOCATION_DECISION: NO_NEXT_ALLOCATION_WHILE_TRADE_OPEN

No next allocation is authorized while this trade remains open. Allocation requires a separate closed-trade or otherwise clearly classified P/L evidence packet.

## 8. No Further Order Rule

No further order is authorized by this report.

Blocked actions:

- broker rerun
- second order
- close trade
- order modification
- position modification
- scheduler
- daemon
- webhook
- live endpoint use

Any future broker action requires a separate Human Owner-approved packet. This report is sanitized evidence classification only.

## 9. Next Safe Packet

NEXT_SAFE_PACKET: AIOS-FOREX-OANDA-DEMO-OPEN-TRADE-MONITOR-READ-ONLY-V1

The next safe packet should perform read-only monitoring of the open demo trade until it closes or reaches a clearly classified state. It must not place another order, close the trade, mutate orders or positions, read secrets during Codex validation, claim realized profit, or authorize allocation.
