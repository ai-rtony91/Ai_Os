# AIOS Forex OANDA Demo BidAsk Corrected Post Trade Evidence V1

## 1. Bid/Ask Corrected Owner Run Classification

Owner-run classification captured:

- `script_status`: `VAULT_BACKED_DEMO_ONE_ORDER_ATTEMPTED`
- `classification`: `VAULT_BACKED_DEMO_ONE_ORDER_ATTEMPTED`
- broker network call performed: true
- order placement performed: true
- order attempt count: 1
- endpoint: OANDA practice/demo orders endpoint only

This report captures sanitized owner-provided post-trade evidence only. Codex did not call OANDA,
place another order, read credentials, read account IDs, read Windows Vault, read environment
variables, read `.env`, create automation, stage, commit, or push.

## 2. Broker Network Result

Sanitized broker network result:

- HTTP status code: 201
- HTTP result: created
- instrument: `EUR_USD`
- direction: `BUY`
- units: 1
- order type: `MARKET`
- live endpoint used: false
- credential value printed: false
- account ID value printed: false

The bid/ask-corrected owner-run command reached the OANDA practice/demo orders endpoint and produced
broker transaction evidence. This proves the owner-run transport reached OANDA practice for this
attempt, but it does not prove fill, profit, strategy edge, allocation progress, or campaign return.

## 3. Sanitized Transaction Evidence

Sanitized owner-provided order evidence:

- stop loss: `1.07010`
- take profit: `1.07080`
- client order ID: `AIOS-DEMO-BIDASK-CORRECTED-OWNER-RUNTIME-001`
- order create transaction ID: `317`
- order cancel transaction ID: `318`
- related transaction IDs: `317`, `318`

No token value, account ID value, credential value, authorization header, password, raw broker
payload, or private account identifier is included in this report.

## 4. Fill Status

Fill status captured:

- no `orderFillTransaction` observed
- no fill evidence captured
- no open position claimed
- no realized profit claimed
- no unrealized profit claimed
- no `120%` claim supported

The available owner-provided evidence shows an order create transaction followed by an order cancel
transaction. It does not show a filled trade.

## 5. Cancel Reason

Cancel reason captured:

```text
TAKE_PROFIT_ON_FILL_LOSS
```

OANDA canceled the bid/ask-corrected demo order again because the take-profit-on-fill value was
loss-side for the executable order context at broker evaluation time.

## 6. Why Static Bid/Ask Failed

The bid/ask-corrected packet improved the prior static reference-price check by validating the
submitted SL/TP against owner-supplied bid/ask values:

```text
bid: 1.07040
ask: 1.07050
stop_loss: 1.07010
take_profit: 1.07080
```

That local relationship satisfied the bid/ask validation rule at packet construction time. The
broker cancel result proves that static owner-supplied bid/ask values can still become stale before
the order reaches broker evaluation. For a market order, the executable spread context at submit
time is the controlling context, not a previously copied quote.

## 7. Required Live Pricing Correction

Future order logic must fetch current OANDA demo pricing immediately before order construction,
compute SL/TP from the current executable side, and submit in one owner-approved runtime flow.

Required correction:

- fetch current OANDA practice/demo bid/ask pricing inside the owner-approved runtime packet.
- compute BUY stop loss below current bid and take profit above current ask using configured
  distance.
- compute SELL stop loss above current ask and take profit below current bid using configured
  distance.
- construct the order command only after the fresh quote is available.
- avoid accepting stale copied bid/ask values as final executable evidence.
- preserve sanitized output and post-trade evidence capture.
- preserve no live endpoint, no credential persistence, no account ID persistence, no scheduler, no
  daemon, no webhook, and no unattended execution boundary.

This report does not authorize Codex to perform that pricing call or place an order. It only records
the correction requirement for a separately approved owner-runtime packet.

## 8. No Second Order Rule

No second order is authorized by this evidence capture.

The captured state is:

- one order attempted: true
- order attempt count: 1
- second order allowed: false
- rerun authorized: false
- retry loop authorized: false
- scheduler authorized: false
- daemon authorized: false
- webhook authorized: false
- live endpoint authorized: false

Any new broker action requires a separate Human Owner-approved packet. This report is evidence only
and does not authorize another demo order, live order, allocation, compounding, or campaign claim.

## 9. Next Safe Packet

Next safe packet:

```text
AIOS-FOREX-OANDA-DEMO-LIVE-QUOTE-DERIVED-SLTP-RUNTIME-V1
```

That packet should define a tightly bounded owner-approved runtime flow that fetches current OANDA
practice/demo pricing immediately before order construction, derives SL/TP from that fresh quote,
and preserves one-order-only and sanitized post-trade evidence requirements. It must not create
general automation, live trading authority, schedulers, daemons, webhooks, credential persistence,
account ID persistence, commit, or push authority.
