# AIOS Forex OANDA Practice Closed-Trade Receipt Intake V1

## Purpose

Convert one owner-reviewed, sanitized, broker-reported closed OANDA practice trade into an append-only `REAL_DEMO_DAY` ledger record that the 30/100/300/500 evidence campaign can count.

## Accepted Evidence

The receipt must contain:

- OANDA practice/demo scope;
- a closed trade only;
- sanitized trade reference;
- pair, side, units, entry and exit timestamps/prices;
- net realized P&L;
- pre/post balance reconciliation with no deposit or withdrawal adjustment;
- spread, absolute slippage, trade drawdown, strategy, timeframe, session, and walk-forward window;
- stop-loss and take-profit attachment status;
- explicit proof that no raw broker payload, credentials, account identifier, live money, or intake-created order is present.

## Rejections

The intake fails closed for:

- open or pending trades;
- missing or invalid metrics;
- inconsistent P&L/balance math;
- duplicate receipt fingerprint or trade reference;
- credentials, tokens, account identifiers, authorization values, or raw broker payload keys;
- missing owner confirmations;
- concurrent ledger intake lock;
- live-money or order-creation claims.

## Owner Command

Dry-run:

```powershell
pwsh -NoProfile -File scripts/forex_delivery/Invoke-AiOsOandaPracticeReceiptIntake.ps1 -ReceiptJson C:\PATH\receipt.json -OwnerConfirmed
```

Apply after reviewing the dry-run result:

```powershell
pwsh -NoProfile -File scripts/forex_delivery/Invoke-AiOsOandaPracticeReceiptIntake.ps1 -ReceiptJson C:\PATH\receipt.json -OwnerConfirmed -Apply
```

Apply requires `main`, a clean worktree, and passing targeted intake tests. After append, the wrapper runs the extended evidence verdict automatically.

## Safety Boundary

- No broker call.
- No credential or `.env` read.
- No order placement, modification, or closure.
- No automatic receipt discovery.
- No automatic evidence fabrication.
- No money movement.
- No live or autonomous trading authority.
- No profitability guarantee.

## Files

- `automation/forex_engine/oanda_practice_closed_trade_receipt_intake_v1.py`
- `scripts/forex_delivery/run_oanda_practice_closed_trade_receipt_intake_v1.py`
- `scripts/forex_delivery/Invoke-AiOsOandaPracticeReceiptIntake.ps1`
- `tests/forex_engine/test_oanda_practice_closed_trade_receipt_intake_v1.py`
- `control/forex/oanda_practice_closed_trade_receipt_template_v1.json`

## Finish-Line Meaning

This closes the software bridge between a real closed OANDA practice receipt and the trust ladder. It does not generate trades or prove profit. Real campaign progress begins only when owner-reviewed broker receipts are appended.
