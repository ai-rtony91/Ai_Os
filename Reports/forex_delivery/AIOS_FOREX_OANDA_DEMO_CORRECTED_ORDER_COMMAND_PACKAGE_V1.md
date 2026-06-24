# AIOS FOREX OANDA DEMO CORRECTED ORDER COMMAND PACKAGE V1

## 1. Prior Cancel Evidence

Prior sanitized owner-run evidence classified the OANDA demo attempt as `CANCELED_NOT_FILLED`.
The request reached OANDA practice, produced order create transaction `313`, then OANDA canceled
it with order cancel transaction `314` and reason `TAKE_PROFIT_ON_FILL_LOSS`.

No filled trade was observed. No profit evidence was created.

## 2. Correction Consumed

The corrected command package consumes the SL/TP validation correction gate before a transport
command template can be marked ready.

Required validation classification:

```text
SLTP_VALIDATION_READY
```

If the validation gate returns a side-placement blocker, this package returns:

```text
BLOCKED_BY_SLTP_VALIDATION
```

## 3. Required Reference Price

The owner must provide a non-secret reference price before building a corrected command package.
The reference price must come from owner-visible market context and must not be read from a broker,
credential store, vault, environment variable, `.env`, daemon, scheduler, webhook, or live data
fetch by Codex.

Missing reference price blocks with:

```text
BLOCKED_BY_MISSING_REFERENCE_PRICE
```

## 4. Corrected BUY Rule

For `BUY`:

```text
stop_loss < reference_price
take_profit > reference_price
```

This blocks the prior loss-side take-profit pattern before broker transport.

## 5. Corrected SELL Rule

For `SELL`:

```text
stop_loss > reference_price
take_profit < reference_price
```

This blocks loss-side take-profit and profit-side stop-loss placement before broker transport.

## 6. Prior One-Order Cap Warning

The prior owner-run attempt consumed the one-order cap for that attempt. This package does not
authorize another order. It only prepares a corrected command template path after validation.

Any future demo order attempt requires a separate owner approval gate.

## 7. Owner Manual Boundary

This package is owner-manual only. It creates no scheduler, daemon, webhook, retry engine, loop,
autonomous order path, or live endpoint authority.

Codex must not run the broker transport command and must not read credentials, account IDs,
Windows Vault, environment variables, or `.env`.

## 8. Corrected Command Template

Build the corrected command package with placeholders replaced by owner-selected, non-secret
numeric values:

```powershell
python scripts/forex_delivery/run_oanda_demo_corrected_order_command_package_v1.py --build-corrected-command-package --instrument EUR_USD --direction BUY --units 1 --reference-price EXAMPLE_REFERENCE_PRICE --stop-loss EXAMPLE_VALID_STOP_LOSS_PRICE --take-profit EXAMPLE_VALID_TAKE_PROFIT_PRICE --risk-amount 1.00 --client-order-id AIOS-DEMO-CORRECTED-ONE-ORDER-OWNER-RUNTIME-001 --order-type MARKET --i-confirm-demo-only --i-confirm-sltp-validation-passed --i-confirm-one-prior-order-cap-consumed --i-confirm-new-owner-approval-required-before-any-future-order --i-confirm-owner-manual-runtime-only --i-confirm-no-live-endpoint --i-confirm-no-autonomous-order --i-confirm-post-trade-evidence-required --i-confirm-no-profit-claim
```

The output is sanitized JSON only. A ready package emits a transport command template for owner
review, but that template remains blocked from runtime until the next approval packet exists.

## 9. Next Safe Packet

```text
AIOS-FOREX-OANDA-DEMO-FUTURE-ORDER-APPROVAL-GATE-V1
```

The next packet must decide whether a separately approved future demo order attempt is allowed
after SL/TP correction. Until then:

```text
NO_SECOND_ORDER_AUTHORIZED
NO_BROKER_CALL_AUTHORIZED
NO_PROFIT_CLAIM
```
