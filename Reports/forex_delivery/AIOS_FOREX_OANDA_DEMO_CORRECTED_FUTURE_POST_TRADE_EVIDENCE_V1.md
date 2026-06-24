# AIOS Forex OANDA Demo Corrected Future Post Trade Evidence V1

## 1. Corrected Future Owner Run Classification

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

The corrected future owner-run command reached the OANDA practice/demo orders endpoint and produced
broker transaction evidence. This proves the demo transport path reached OANDA practice for this
attempt, but it does not prove fill, profit, strategy edge, allocation progress, or campaign return.

## 3. Sanitized Transaction Evidence

Sanitized owner-provided order evidence:

- stop loss: `1.06950`
- take profit: `1.07150`
- client order ID: `AIOS-DEMO-CORRECTED-FUTURE-OWNER-RUNTIME-001`
- order create transaction ID: `315`
- order cancel transaction ID: `316`
- related transaction IDs: `315`, `316`

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

OANDA canceled the corrected future demo order again because the take-profit-on-fill value was
loss-side for the executable order context at broker evaluation time.

## 6. Why Static Reference Validation Failed

The corrected future packet validated the submitted `BUY` values against an owner-supplied static
reference price:

```text
stop_loss: 1.06950
reference_price: 1.07050
take_profit: 1.07150
```

That static relationship satisfied the local rule:

```text
stop_loss < reference_price < take_profit
```

The broker cancel result proves that this local static reference-price validation was insufficient.
For a market order, the actual executable context can differ from a stale or manually supplied
reference price because the spread and current bid/ask side matter immediately before order
construction and submission.

## 7. Required Bid/Ask Quote Validation Correction

Future order logic must validate stop loss and take profit against current bid/ask quote evidence
immediately before command construction.

Required correction:

- fetch or owner-supply current bid/ask quote evidence before building the command.
- validate `BUY` stop loss and take profit against the executable side of the spread.
- validate `SELL` stop loss and take profit against the executable side of the spread.
- reject stale, missing, placeholder, zero, negative, non-numeric, or side-incompatible quote inputs.
- preserve sanitized output only.
- preserve no credential, account ID, vault, env, `.env`, live endpoint, scheduler, daemon, webhook,
  or unattended execution boundary.

The next validation layer must prove that TP and SL are on the correct side of the current
executable market context, not just on the correct side of a static reference price.

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
AIOS-FOREX-OANDA-DEMO-BID-ASK-SLTP-VALIDATION-V1
```

That packet should create a broker-call-free validation layer for current bid/ask-based SL/TP side
checks. It must not place an order, call OANDA, read credentials, read account IDs, read Windows
Vault, read environment variables, read `.env`, create automation, stage, commit, or push unless a
separate explicit approval packet authorizes those actions.
