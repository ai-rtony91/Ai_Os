# AIOS Forex OANDA Demo SLTP Validation Correction V1

## 1. Prior Failure

The prior owner-run vault-backed OANDA demo one-order attempt reached OANDA practice, created transaction evidence, and was canceled before fill.

Prior captured state:

- result bucket: `CANCELED_NOT_FILLED`
- cancel reason: `TAKE_PROFIT_ON_FILL_LOSS`
- direction: `BUY`
- instrument: `EUR_USD`
- stop loss: `1.07000`
- take profit: `1.07100`
- order attempt count: 1
- second order allowed: false

## 2. Root Cause

The prior order was canceled because the take-profit-on-fill value was invalid/loss-side for the order context at execution time.

This is broker-side validation/cancel evidence. It is not fill evidence, profit evidence, or `+120 percent` campaign evidence.

## 3. Correction Standard

AIOS now has a pure SL/TP validation correction gate. The gate requires an owner-supplied, non-secret reference price and validates stop loss and take profit side rules before any future corrected command package can exist.

The correction gate:

- accepts only non-secret numeric price inputs.
- requires `EUR_USD`.
- requires `BUY` or `SELL`.
- does not call OANDA.
- does not read broker prices.
- does not read live market data.
- does not read credentials, account IDs, Windows Vault, environment variables, or `.env`.
- returns sanitized JSON only.

## 4. BUY SL/TP Rule

For a `BUY` order:

- stop loss must be below the owner reference price.
- take profit must be above the owner reference price.

If the BUY stop loss is not below reference, the gate returns:

```text
BLOCKED_BY_BUY_STOP_LOSS_NOT_BELOW_REFERENCE
```

If the BUY take profit is not above reference, the gate returns:

```text
BLOCKED_BY_BUY_TAKE_PROFIT_NOT_ABOVE_REFERENCE
```

## 5. SELL SL/TP Rule

For a `SELL` order:

- stop loss must be above the owner reference price.
- take profit must be below the owner reference price.

If the SELL stop loss is not above reference, the gate returns:

```text
BLOCKED_BY_SELL_STOP_LOSS_NOT_ABOVE_REFERENCE
```

If the SELL take profit is not below reference, the gate returns:

```text
BLOCKED_BY_SELL_TAKE_PROFIT_NOT_BELOW_REFERENCE
```

## 6. No Broker Call Boundary

The correction gate is local validation only. It does not call OANDA, place an order, open a position, request broker pricing, read live market data, or create execution authority.

The script supports `--print-template` and `--validate-sltp` only.

## 7. No Second Order Boundary

The prior one-order cap remains consumed for the canceled attempt.

This correction does not authorize:

- a second order.
- a rerun.
- a retry loop.
- a scheduler.
- a daemon.
- a webhook.
- any unattended trading path.

Any future demo-order consideration requires a separate Human Owner-approved packet after corrected validation evidence exists.

## 8. Required Owner Reference Price

The owner must supply a non-secret reference price at validation time:

```text
--reference-price EXAMPLE_REFERENCE_PRICE
```

The reference price is not fetched by Codex or by the validation gate. If the reference price is missing, non-numeric, zero, negative, or a placeholder during validation, the gate blocks before any corrected command package can be considered.

## 9. Next Safe Packet

Next safe packet:

```text
AIOS-FOREX-OANDA-DEMO-CORRECTED-ORDER-COMMAND-PACKAGE-V1
```

That packet must consume validated SL/TP correction evidence only. It must not call OANDA, place another order, read credentials, read account IDs, read Windows Vault, read environment variables, read `.env`, create live authority, stage, commit, or push unless separately approved.
