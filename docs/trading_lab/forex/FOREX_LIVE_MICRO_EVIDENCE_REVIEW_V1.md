# AIOS Forex Live Micro Evidence Review V1

## Purpose
This packet is the post-live-proof evidence review for the controlled micro-live lane.

It does not place a trade. It only reads broker-side evidence to determine whether the prior
live micro execution is visible and whether the realized outcome is profitable.

## Runtime behavior
- Read-only only mode.
- No `POST`, `PUT`, `PATCH`, or `DELETE` requests.
- No `/orders` mutation paths.
- No order execution, money movement, scheduler, daemon, or webhook activity.

## Allowed probes
- `GET https://api-fxtrade.oanda.com/v3/accounts/{account_id}/summary`
- `GET https://api-fxtrade.oanda.com/v3/accounts/{account_id}/openTrades`
- `GET https://api-fxtrade.oanda.com/v3/accounts/{account_id}/openPositions`
- `GET https://api-fxtrade.oanda.com/v3/accounts/{account_id}/trades`
- `GET https://api-fxtrade.oanda.com/v3/accounts/{account_id}/transactions/sinceid?id=<safe id>`

## Evidence decisions
- If `EUR_USD` open trade or position is visible, classify visibility and optional profit class.
- If no open trade/position is visible after a prior controlled micro-live order, classify whether it is
  `ORDER_CREATED_NO_OPEN_TRADE_FOUND` or `CLOSED_OR_NOT_VISIBLE`.
- If no trade/position is visible and there is no live-order evidence, classify
  `READONLY_REVIEW_READY`.
- If broker credentials or endpoint contract are invalid, classify repair or credential stages.

## SL/TP evidence-depth repair behavior
- `prior_order_payload` and `prior_order_response` are now inspected for read-only SL/TP intent:
  - `stopLossOnFill`
  - `takeProfitOnFill`
  - `stopLossOrderID` / `takeProfitOrderID`
  - `stopLossOrder` / `takeProfitOrder` when present in prior payload objects
  - `trailingStopLossOrder` / `trailingStopLossOrderID` as stop-side evidence
- `openTrades` payload is now inspected for the matching EUR_USD trade:
  - `stopLossOrder`, `takeProfitOrder`, and `stopLossOrderID` / `takeProfitOrderID`
  - `trailingStopLossOrder`, `trailingStopLossOrderID`
- `trades` payload is a fallback only when `openTrades` trade details do not already expose SL/TP evidence.
- Evidence fields are fingerprinted (`sha256:first12`) and stored in summary fields to avoid exposing raw IDs.

### Position-source limitation
- `openPositions` proves exposure only (units / PL context). It is not used as SL/TP evidence by itself.
- A position match without matching SL/TP artifacts does not set `sl_observed`, `tp_observed`,
  or `sltp_evidence_complete`.

### `sltp_evidence_complete`
- `sltp_evidence_complete` is `True` only when both:
  - stop-side evidence exists (`sl_observed`), including fixed SL or trailing SL
  - TP evidence exists (`tp_observed`)
- This packet is still not proof of repeatable profitability; it only proves that SL/TP config is visible in broker read-only evidence.

## Why this is not autonomy
One controlled micro proof is a visibility check only. It is not profitable-autonomy evidence.
It does not prove repeatable profit across sessions.

## Next action
After this review, continue with supervised repeatability evidence loop and human-approved evidence
comparison before any broader execution readiness decision.
