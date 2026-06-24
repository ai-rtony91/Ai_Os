# AIOS Forex OANDA Demo Owner One Trade Command Package V1

## 1. Current State

The current readiness state is `READY_FOR_OWNER_DEMO_ONE_TRADE_COMMAND_PACKAGE`.

The owner-run vault-backed read-only OANDA practice preflight was captured as sanitized evidence. It reported favorable read-only metadata access, `EUR_USD` availability, no blocker list, no order placement, no orders endpoint call, no live endpoint use, and no credential or account value printing.

This command package is template-only evidence. It does not call OANDA, read credentials, read an account ID, read Windows Vault, read environment variables, read `.env`, place a demo order, or place a live order.

## 2. Required Prior Evidence

Required prior evidence before any owner manual trade attempt:

- read-only vault-backed OANDA practice preflight captured as sanitized evidence.
- one-trade readiness classified `READY_FOR_OWNER_DEMO_ONE_TRADE_COMMAND_PACKAGE`.
- allowed instrument is `EUR_USD`.
- Codex broker call performed: false.
- credential read performed by Codex: false.
- account ID read performed by Codex: false.
- order placement performed by Codex: false.
- orders endpoint called by Codex: false.
- live endpoint used: false.
- execution authority remains false.

## 3. Owner Manual Runtime Boundary

The owner manual runtime boundary means Anthony may review and run a demo/practice command outside Codex only if he intends one demo order attempt.

Codex must not run the owner trade command. Codex must not read runtime credential material. Token and account values must not appear in command text, repo files, reports, logs, tests, fixtures, telemetry, screenshots, or prompts.

The command package builder returns sanitized JSON only and accepts no token or account ID arguments.

## 4. Demo One-Trade Command Package Standard

The command package is ready only when all of these remain true:

- demo/practice only.
- exactly one owner manual order attempt.
- `EUR_USD` only.
- direction is `BUY` or `SELL` only.
- units are integer micro-size only.
- stop loss is present.
- take profit is present.
- no live endpoint.
- no autonomous order.
- no scheduler, daemon, webhook, loop, retry engine, or unattended path.
- post-trade evidence capture is required next.
- result bucket classification is required after evidence.
- no profit claim and no +120 percent guarantee.

## 5. Required Trade Intent Fields

Required trade intent fields:

- `--instrument EUR_USD`
- `--direction BUY` or `--direction SELL`
- `--units 1` or another integer micro-size value allowed by the package gate
- `--stop-loss-price EXAMPLE_STOP_LOSS_PRICE`
- `--take-profit-price EXAMPLE_TAKE_PROFIT_PRICE`

The report intentionally uses placeholder prices only.

## 6. Risk Fields Required

The command package requires stop loss and take profit to be present before the owner command template can classify ready.

The generated owner runtime command template includes `EXAMPLE_RISK_AMOUNT` as a placeholder. The owner must not treat placeholders as executable values without owner-side review.

## 7. Forbidden Execution Paths

Forbidden paths:

- Codex broker call.
- Codex demo order.
- any live order.
- live endpoint.
- credential or account ID read by Codex.
- token or account ID in CLI arguments.
- token or account ID printing.
- `.env` read.
- Windows Vault read by Codex.
- scheduler, daemon, webhook, loop, retry engine, or unattended trading path.
- profit guarantee or +120 percent achievement claim.

## 8. Post-Trade Evidence Requirement

After any owner manual demo trade attempt, the next required packet is post-trade evidence capture. The evidence must be sanitized and must not include token values, account ID values, credentials, secrets, passwords, authorization headers, raw broker credential material, or screenshots exposing private values.

No second order attempt is authorized by this package.

## 9. Result Bucket Requirement

After post-trade evidence capture, the result must feed the result bucket and next allocation evaluator before any continuation decision.

Result bucket output is accounting and decision support only. It does not create a broker command or execution authority.

## 10. Exact Owner Template Command

Run this package builder template first:

```powershell
python scripts/forex_delivery/run_oanda_demo_owner_one_trade_command_package_v1.py --print-template
```

Build the sanitized owner command package with placeholders only:

```powershell
python scripts/forex_delivery/run_oanda_demo_owner_one_trade_command_package_v1.py --build-owner-command-package --instrument EUR_USD --direction BUY --units 1 --stop-loss-price EXAMPLE_STOP_LOSS_PRICE --take-profit-price EXAMPLE_TAKE_PROFIT_PRICE --i-confirm-demo-only --i-confirm-one-order-only --i-confirm-owner-manual-runtime-only --i-confirm-stop-loss-present --i-confirm-take-profit-present --i-confirm-no-live-endpoint --i-confirm-no-autonomous-order --i-confirm-post-trade-evidence-required --i-confirm-result-bucket-required --i-confirm-no-profit-claim
```

The builder output is a template package only. It is not proof that an order should be run and it is not a broker call.

## 11. Next Safe Packet After Owner Trade Attempt

If the owner manually runs one demo/practice trade attempt outside Codex, the next safe packet is:

```text
AIOS-FOREX-OANDA-DEMO-POST-TRADE-EVIDENCE-CAPTURE-V1
```

That packet must capture sanitized result evidence only. It must preserve no-live-trading, one-order-only, no second order, no credential persistence, no account ID persistence, no scheduler, no daemon, no webhook, no commit, and no push.
