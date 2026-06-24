# AIOS Forex OANDA Demo Result Bucket And Next Allocation After Cancel V1

## 1. Result Bucket

RESULT_BUCKET: `CANCELED_NOT_FILLED`

The owner-run vault-backed OANDA demo one-order attempt reached OANDA practice and produced transaction evidence, but the order was canceled by OANDA before any fill evidence was observed.

This bucket is a no-fill cancel classification. It is not a profit bucket, loss bucket, breakeven bucket, or open-position bucket.

## 2. Broker Result Summary

Sanitized broker result summary:

- `script_status`: `VAULT_BACKED_DEMO_ONE_ORDER_ATTEMPTED`
- HTTP status code: 201
- broker network call performed: true
- order placement performed: true
- order attempt count: 1
- order create transaction ID: `313`
- order cancel transaction ID: `314`
- cancel reason: `TAKE_PROFIT_ON_FILL_LOSS`
- live endpoint used: false
- credential value printed: false
- account ID value printed: false

The broker accepted the request far enough to create transaction evidence, then canceled the order because the take-profit-on-fill would have been invalid/loss-side for the order at execution time. This proves broker reachability and one-order transport execution, but it does not prove a filled trade, profit, or strategy edge.

## 3. Fill Status

Fill status: `NOT_FILLED`

No `orderFillTransaction` was observed. No filled trade is claimed. No open position is claimed. No realized profit or loss is claimed from a filled trade.

## 4. Cancel Reason

Cancel reason:

```text
TAKE_PROFIT_ON_FILL_LOSS
```

Operational meaning: the submitted take-profit-on-fill value was invalid for the order context at execution time. The correction path must validate stop loss and take profit side, distance, and broker acceptance rules before any new owner-reviewed demo order packet exists.

## 5. One-Order Cap Status

ORDER_CAP_STATUS: `CONSUMED_FOR_THIS_ATTEMPT`

The captured state is:

- one-order-only boundary: true
- order attempt count: 1
- second order allowed: false
- repeat order authorized: false
- retry loop authorized: false

The one-order cap for this attempt is consumed. This report does not authorize another order.

## 6. Profitability Status

PROFITABILITY_STATUS: `NO_PROFIT_EVIDENCE`

There is no fill evidence, no realized profit evidence, no strategy-edge evidence, and no `+120 percent` campaign progress evidence. The campaign target remains a non-guaranteed target only.

## 7. Allocation Decision

ALLOCATION_DECISION: `NO_NEXT_ALLOCATION`

No next allocation is authorized. No compounding, withdrawal, size increase, repeat order, or continuation trade is authorized from this result.

## 8. Blockers

Current blockers:

- order canceled before fill.
- cancel reason is `TAKE_PROFIT_ON_FILL_LOSS`.
- no `orderFillTransaction` observed.
- one-order cap consumed for this attempt.
- second order is blocked.
- next allocation is blocked.
- corrected SL/TP validation packet is required before any future demo-order consideration.

## 9. Required Correction Before Any New Demo Order

Before any new demo order can be considered, AIOS needs a corrected SL/TP validation packet that verifies the order-side relationship and broker-acceptance constraints without calling OANDA or placing an order.

Required correction scope:

- validate BUY and SELL stop loss side rules.
- validate BUY and SELL take profit side rules.
- validate that take profit cannot be loss-side at fill time.
- validate that stop loss and take profit are both present before owner runtime.
- preserve one-order-only governance until a separately approved future packet exists.
- preserve no-live, no-autonomy, no-secrets, no-scheduler, no-daemon, and no-webhook boundaries.

## 10. Next Safe Packet

NEXT_SAFE_PACKET: `AIOS-FOREX-OANDA-DEMO-SLTP-VALIDATION-CORRECTION-V1`

That packet must be a correction/validation packet only. It must not call OANDA, place another order, read credentials, read account IDs, read Windows Vault, read environment variables, read `.env`, authorize next allocation, stage, commit, or push unless separately approved.
