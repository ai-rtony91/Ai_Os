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

## Why this is not autonomy
One controlled micro proof is a visibility check only. It is not profitable-autonomy evidence.
It does not prove repeatable profit across sessions.

## Next action
After this review, continue with supervised repeatability evidence loop and human-approved evidence
comparison before any broader execution readiness decision.
