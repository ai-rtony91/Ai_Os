# AIOS Forex OANDA Demo Bid Ask Corrected Runtime Packet V1

## 1. Prior Cancel Evidence

Prior sanitized owner-run evidence shows that OANDA practice was reached, but the orders canceled
before fill:

- first owner run: order create transaction `313`, order cancel transaction `314`
- corrected future owner run: HTTP 201, order create transaction `315`, order cancel transaction
  `316`
- cancel reason: `TAKE_PROFIT_ON_FILL_LOSS`
- no `orderFillTransaction` observed
- no fill evidence captured
- no profit evidence captured
- no `120%` claim supported

This packet does not reinterpret either canceled order as success, fill, profit, strategy edge, or
allocation progress.

## 2. Bid/Ask Correction Consumed

This packet consumes the local bid/ask SLTP validation standard:

```text
BID_ASK_SLTP_VALIDATION_READY
```

The runtime packet builder re-runs the local bid/ask validator against the supplied non-secret
numeric values before emitting an owner-only command template. Static reference-price validation is
not sufficient for future runtime packets.

Created local packet components:

- `automation/forex_engine/oanda_demo_bid_ask_corrected_runtime_packet_v1.py`
- `scripts/forex_delivery/run_oanda_demo_bid_ask_corrected_runtime_packet_v1.py`
- `tests/forex_engine/test_oanda_demo_bid_ask_corrected_runtime_packet_v1.py`

## 3. BUY Runtime Rule

For BUY runtime packet readiness:

- executable entry side is `ask`
- stop loss must be below `bid` by at least the configured minimum distance
- take profit must be above `ask` by at least the configured minimum distance
- bid/ask SLTP validation must return `BID_ASK_SLTP_VALIDATION_READY`

The example BUY packet values are:

```text
bid: 1.07040
ask: 1.07050
stop_loss: 1.07010
take_profit: 1.07080
min_distance_pips: 2
pip_size: 0.0001
```

## 4. SELL Runtime Rule

For SELL runtime packet readiness:

- executable entry side is `bid`
- stop loss must be above `ask` by at least the configured minimum distance
- take profit must be below `bid` by at least the configured minimum distance
- bid/ask SLTP validation must return `BID_ASK_SLTP_VALIDATION_READY`

SELL packets use the same local validation path and do not call a broker or fetch market data.

## 5. Owner Runtime Boundary

This packet is owner-run only. Codex must not execute the generated command.

Boundary preserved:

- no broker call by Codex
- no demo order by Codex
- no live order by Codex
- no credential read
- no account ID read
- no Windows Vault read
- no environment variable read
- no `.env` read
- no token or account ID CLI arguments
- no scheduler, daemon, webhook, or unattended execution path

The output is sanitized JSON only.

## 6. Corrected Bid/Ask Command Template

Owner command template produced by the packet builder when all gates pass:

```powershell
python scripts/forex_delivery/run_oanda_demo_vault_backed_one_order_transport_v1.py --execute-vault-backed-demo-one-order --instrument EUR_USD --direction BUY --units 1 --stop-loss 1.07010 --take-profit 1.07080 --risk-amount 1.00 --client-order-id AIOS-DEMO-BIDASK-CORRECTED-OWNER-RUNTIME-001 --order-type MARKET --i-confirm-demo-only --i-confirm-vault-backed-runtime-only --i-confirm-one-order-only --i-confirm-owner-manual-runtime-only --i-confirm-stop-loss --i-confirm-take-profit --i-confirm-no-live-endpoint --i-confirm-no-autonomous-order --i-confirm-no-second-order --i-confirm-post-trade-evidence --i-confirm-kill-switch-ready --i-understand-loss-possible --i-understand-no-profit-guarantee
```

Codex did not run this command. This report stores the template only.

## 7. No Profit Claim

This packet does not claim:

- fill
- realized profit
- unrealized profit
- strategy edge
- allocation progress
- campaign progress
- `120%` return

Any future owner run must produce its own sanitized post-trade evidence before any result
classification is made.

## 8. Required Post-Trade Evidence

If the owner manually runs the generated vault-backed transport command, the next evidence packet
must capture:

- sanitized script status
- broker network call status
- order placement status
- order attempt count
- fill or cancel status
- transaction IDs if present
- stop loss and take profit status
- proof that credential and account values were not printed or persisted
- no second-order status
- no profit claim unless supported by actual broker evidence

## 9. Next Safe Owner Action

Owner may review the bid/ask-corrected runtime packet output and command template. Codex must stop
here and must not run broker transport.

Next required packet after any owner run:

```text
AIOS-FOREX-OANDA-DEMO-BID-ASK-CORRECTED-POST-TRADE-EVIDENCE-V1
```
