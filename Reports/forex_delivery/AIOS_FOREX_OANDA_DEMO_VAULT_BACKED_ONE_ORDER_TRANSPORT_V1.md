# AIOS Forex OANDA Demo Vault Backed One Order Transport V1

## 1. Current Blocker

The owner-observed runtime blocker was:

- `script_status`: `TRANSPORT_BLOCKED_RUNTIME_CREDENTIALS_MISSING`
- `broker_network_call_performed`: false
- `order_placement_performed`: false
- `order_attempt_count`: 0
- `next_safe_action`: `owner_must_supply_runtime_env_credentials_outside_repo`

The existing transport was ready enough to build a redacted request preview, but it needed credentials supplied externally. This wrapper fixes that boundary by using the already approved Windows Vault labels at owner runtime.

## 2. Fix Implemented

Created a vault-backed owner-run wrapper that loads the OANDA demo/practice credential values at owner runtime, injects them only in memory into the existing one-order demo transport evaluator, and returns sanitized JSON only.

The wrapper does not accept token or account ID values through CLI arguments. It does not print or persist credential values. Codex must not run the wrapper.

## 3. Approved Vault Labels

Approved Windows Vault labels:

- `AIOS_OANDA_DEMO_ACCESS_TOKEN`
- `AIOS_OANDA_DEMO_ACCOUNT_ID`

No other Vault labels are approved by this wrapper.

## 4. Owner Runtime Boundary

The wrapper is owner-run only. Anthony may run it outside Codex only if he intends one OANDA demo/practice order attempt and has reviewed the full command.

Codex must not:

- run the wrapper.
- read Windows Vault values.
- read credentials.
- read account IDs.
- read `.env`.
- read environment variables.
- call OANDA.
- place an order.

## 5. Demo One-Order Boundary

The wrapper preserves the demo one-order boundary:

- OANDA demo/practice only.
- `EUR_USD` only.
- one order attempt maximum.
- no second order.
- stop loss required.
- take profit required.
- owner manual runtime confirmation required.
- kill switch confirmation required.
- post-trade evidence confirmation required.

## 6. Forbidden Live/Autonomous Paths

The wrapper forbids:

- live endpoint.
- live trading.
- autonomous order.
- scheduler.
- daemon.
- webhook.
- retry loop.
- unattended trading path.
- profit guarantee.
- `+120 percent` claim.

## 7. Exact Owner Template Command

Owner template command:

```powershell
python scripts/forex_delivery/run_oanda_demo_vault_backed_one_order_transport_v1.py --execute-vault-backed-demo-one-order --instrument EUR_USD --direction BUY --units 1 --stop-loss 1.07000 --take-profit 1.07100 --risk-amount 1.00 --client-order-id AIOS-DEMO-ONE-ORDER-OWNER-RUNTIME-001 --order-type MARKET --i-confirm-demo-only --i-confirm-vault-backed-runtime-only --i-confirm-one-order-only --i-confirm-owner-manual-runtime-only --i-confirm-stop-loss --i-confirm-take-profit --i-confirm-no-live-endpoint --i-confirm-no-autonomous-order --i-confirm-no-second-order --i-confirm-post-trade-evidence --i-confirm-kill-switch-ready --i-understand-loss-possible --i-understand-no-profit-guarantee
```

Anthony must review the stop loss, take profit, risk amount, direction, units, and order intent before any owner-side run.

## 8. Post-Trade Evidence Requirement

If Anthony manually runs the wrapper and one demo/practice order attempt is made, sanitized post-trade evidence capture is required immediately afterward.

The evidence packet must not include token values, account ID values, credentials, secrets, passwords, authorization headers, raw broker credential material, screenshots exposing private values, or a second-order authorization.

## 9. Next Required Packet After Owner Run

Exact next required packet after any owner-side vault-backed one-order demo runtime attempt:

```text
AIOS-FOREX-OANDA-DEMO-POST-TRADE-EVIDENCE-CAPTURE-V1
```

That packet must capture sanitized result evidence only and preserve demo-only scope, one-order-only enforcement, no second order, no credential persistence, no account ID persistence, no scheduler, no daemon, no webhook, no commit, and no push.
