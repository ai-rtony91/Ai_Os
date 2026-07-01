# Forex Owner Approved Demo One Order Profit Attempt Execution V1

## Scope

This packet defines the owner-approved OANDA DEMO one-order execution boundary for `AIOS_FOREX_OWNER_APPROVED_DEMO_ONE_ORDER_PROFIT_ATTEMPT_EXECUTION_V1`.

Anthony's approval scope is limited to:

- OANDA DEMO only.
- One order only.
- Protected execution only.
- No live trade.
- No money movement.
- No banking, withdrawal, transfer, card, ACH, wire, sweep, or fund rail work.

## Evaluator Boundary

`automation/forex_engine/forex_owner_approved_demo_one_order_profit_attempt_execution_v1.py` is a metadata/control-plane evaluator. It does not call OANDA, does not submit an order, does not read credentials, does not read environment variables, and does not store account identifiers.

The evaluator can return `DEMO_ONE_ORDER_EXECUTION_READY_FOR_RUNTIME` only when owner approval, protected demo attempt readiness, runtime credential-session metadata, existing runtime-interface metadata, sanitized order candidate metadata, risk limits, OANDA demo boundary metadata, and post-trade review gates all pass.

## Runtime Interface Requirement

Runtime execution still requires a separately approved repo runtime path. The inspected repo already contains the protected metadata gate:

`automation/forex_engine/oanda_demo_owner_approved_one_order_protected_runtime_execution_v1.py`

This packet only identifies that kind of existing interface by sanitized metadata. It does not modify runtime transport, broker adapter, strategy, or capital operating files.

## Hard Gates

- Exact Anthony owner approval for this packet.
- Protected demo daily profit attempt ready.
- Runtime credential session available for one OANDA DEMO order only.
- No credential values or account IDs in payloads.
- Existing runtime interface identified and demo-only.
- OANDA mode is `OANDA_DEMO`, `PRACTICE`, or `DEMO`.
- Stop loss and take profit are present.
- Stop-loss and take-profit value or distance metadata is present.
- Maximum risk per trade is `<= 0.01`.
- Maximum daily loss is `<= 0.03`.
- One order only, maximum order count `1`.
- Kill switch inactive.
- Daily loss stop inactive.
- Post-trade review, daily PnL record, sanitized receipt, owner review, and no-second-trade lock required.

## Next Step

If an external approved runtime later executes the OANDA DEMO order, the next step is sanitized runtime receipt capture and post-trade review only:

`AIOS_FOREX_OANDA_DEMO_RUNTIME_RECEIPT_AND_POST_TRADE_REVIEW_V1`

Live micro exception review remains future-only and requires demo evidence plus a separate owner-approved review packet.
