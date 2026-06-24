# AIOS Forex OANDA Demo Final Owner Order Command Review V1

## 1. Current Gate Status

Current gate status: `OWNER_REVIEW_REQUIRED_BEFORE_ANY_OWNER_DEMO_RUNTIME_ATTEMPT`.

Prior evidence shows the owner one-trade command package reached `OWNER_DEMO_ONE_TRADE_COMMAND_PACKAGE_READY` as a template-only package. The prior readiness report identifies the preceding state as `READY_FOR_OWNER_DEMO_ONE_TRADE_COMMAND_PACKAGE`.

This final review report does not call OANDA, does not read credentials, does not read an account ID, does not read `.env`, does not read Windows Vault, does not place an order, and does not create execution authority for Codex.

## 2. Final Owner Command Template

Owner command template:

```powershell
python scripts/forex_delivery/run_oanda_demo_runtime_http_transport_one_order_owner_run_v1.py --execute-transport --instrument EUR_USD --direction BUY --units 1 --stop-loss EXAMPLE_STOP_LOSS_PRICE --take-profit EXAMPLE_TAKE_PROFIT_PRICE --risk-amount EXAMPLE_RISK_AMOUNT --client-order-id AIOS-DEMO-ONE-ORDER-OWNER-RUNTIME-001 --order-type MARKET --i-confirm-transport-reviewed --i-confirm-actual-demo-order-intent --i-understand-demo-only --i-understand-one-order-only --i-understand-loss-possible --i-understand-no-profit-guarantee --i-confirm-stop-loss --i-confirm-take-profit --i-confirm-no-second-order --i-confirm-post-trade-evidence --i-confirm-kill-switch-ready --i-confirm-runtime-credentials-external
```

Codex must not run this command. This command is for Anthony owner-side review and possible owner-side demo runtime use only.

## 3. Required Placeholder Replacements

Before any owner-side run, Anthony must replace all placeholders outside Codex:

- `EXAMPLE_STOP_LOSS_PRICE` must be replaced with an owner-reviewed demo stop loss price.
- `EXAMPLE_TAKE_PROFIT_PRICE` must be replaced with an owner-reviewed demo take profit price.
- `EXAMPLE_RISK_AMOUNT` must be replaced with an owner-reviewed demo risk amount.

The placeholders are not executable values. This report intentionally does not generate real stop loss, take profit, or risk amount values.

## 4. Demo-Only Boundary

This review is demo/practice only. It does not authorize live trading, live endpoints, live broker routing, live credentials, live account use, or real-money order placement.

The runtime command is scoped to the OANDA demo/practice transport path and requires owner-provided runtime credentials outside the repository.

## 5. One-Order-Only Boundary

This review preserves a one-order-only boundary:

- one owner-side demo order attempt maximum.
- no second order attempt authorized by this report.
- no retry loop, scheduler, daemon, webhook, or unattended execution path authorized.
- no autonomous continuation after the owner-side attempt.

After an owner-side attempt, the only next required action is sanitized post-trade evidence capture.

## 6. Stop Loss / Take Profit Required

Stop loss and take profit are required before any owner-side runtime attempt.

The owner command includes both:

- `--stop-loss EXAMPLE_STOP_LOSS_PRICE`
- `--take-profit EXAMPLE_TAKE_PROFIT_PRICE`

Both placeholders must be replaced by Anthony before any owner-side demo run. If either value is missing, unresolved, or not owner-reviewed, the owner-side run should stop.

## 7. No Profit Guarantee

This report makes no profit claim and no `+120 percent` claim.

The owner confirmations include `--i-understand-loss-possible` and `--i-understand-no-profit-guarantee` because the demo order can lose, reject, fail validation, or produce no useful result.

## 8. Post-Trade Evidence Required

If Anthony manually runs one demo/practice order attempt outside Codex, post-trade evidence capture is required immediately afterward.

The evidence packet must be sanitized and must not include:

- token values.
- account ID values.
- credentials.
- secrets.
- passwords.
- authorization headers.
- raw broker credential material.
- screenshots exposing private values.

The evidence must record the result without authorizing a second order.

## 9. Exact Next Packet After Owner Run

Exact next required packet after any owner-side one-order demo runtime attempt:

```text
AIOS-FOREX-OANDA-DEMO-POST-TRADE-EVIDENCE-CAPTURE-V1
```

That next packet must capture sanitized result evidence only. It must preserve demo-only scope, one-order-only enforcement, no second order, no credential persistence, no account ID persistence, no scheduler, no daemon, no webhook, no commit, and no push.
