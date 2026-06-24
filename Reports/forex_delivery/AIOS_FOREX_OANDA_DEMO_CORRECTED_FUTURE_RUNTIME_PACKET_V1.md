# AIOS Forex OANDA Demo Corrected Future Runtime Packet V1

## 1. Current Main State

Preflight observed:

- path: `C:\Dev\Ai.Os`
- branch: `main`
- status: clean against `origin/main`
- latest proof-chain merge: `dbdc885a feat(forex): finalize OANDA demo proof chain (#1071)`

## 2. Prior Cancel Evidence

Prior owner-run evidence remains:

- result bucket: `CANCELED_NOT_FILLED`
- cancel reason: `TAKE_PROFIT_ON_FILL_LOSS`
- order create transaction: `313`
- order cancel transaction: `314`
- no `orderFillTransaction` observed
- no fill claimed
- no profit claimed

This runtime packet does not reinterpret the prior cancel as success or profit proof.

## 3. Corrected SL/TP Evidence

The corrected future template uses owner-supplied non-secret numeric values:

```text
reference_price: 1.07050
stop_loss: 1.06950
take_profit: 1.07150
```

For the provided `BUY` template, the corrected rule is satisfied:

```text
stop_loss < reference_price < take_profit
```

For `SELL`, the rule remains:

```text
take_profit < reference_price < stop_loss
```

## 4. Approval Gate Evidence

The future-order approval gate evidence required before this packet:

- corrected order command package ready
- SL/TP validation ready
- prior cancel evidence captured
- prior order cap consumption acknowledged
- owner manual decision boundary preserved

Ready gate classification remains:

```text
OWNER_APPROVAL_GATE_READY_FOR_MANUAL_DECISION
```

That classification does not authorize Codex to execute a broker command.

## 5. Owner Runtime Boundary

This packet is owner-run only. Codex must not run the command, call OANDA, place a demo order,
place a live order, read credentials, read account IDs, read Windows Vault, read environment
variables, or read `.env`.

The command template targets the existing vault-backed demo transport wrapper only.

## 6. Corrected Future Command Template

```powershell
python scripts/forex_delivery/run_oanda_demo_vault_backed_one_order_transport_v1.py --execute-vault-backed-demo-one-order --instrument EUR_USD --direction BUY --units 1 --stop-loss 1.06950 --take-profit 1.07150 --risk-amount 1.00 --client-order-id AIOS-DEMO-CORRECTED-FUTURE-OWNER-RUNTIME-001 --order-type MARKET --i-confirm-demo-only --i-confirm-vault-backed-runtime-only --i-confirm-one-order-only --i-confirm-owner-manual-runtime-only --i-confirm-stop-loss --i-confirm-take-profit --i-confirm-no-live-endpoint --i-confirm-no-autonomous-order --i-confirm-no-second-order --i-confirm-post-trade-evidence --i-confirm-kill-switch-ready --i-understand-loss-possible --i-understand-no-profit-guarantee
```

Codex did not run this command.

## 7. No Profit Claim

This packet does not claim profit, fill, strategy edge, campaign progress, or `120%` return. The
prior owner run was canceled-not-filled. Any future owner run must be treated as a new demo outcome
that requires its own sanitized evidence packet.

## 8. Required Post-Trade Evidence

If the owner manually runs the command, the next evidence packet must capture:

- sanitized script status
- broker network call status
- order attempt count
- fill or cancel status
- transaction IDs if present
- stop loss and take profit status
- proof that credential and account values were not printed or persisted
- no second-order status
- no profit claim unless supported by actual broker evidence

## 9. Next Safe Owner Action

Owner may review the corrected future runtime command template. Codex must stop here and must not
run broker transport.

Next required packet after any owner run:

```text
AIOS-FOREX-OANDA-DEMO-CORRECTED-FUTURE-POST-TRADE-EVIDENCE-V1
```
