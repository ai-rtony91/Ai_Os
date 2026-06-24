# AIOS Forex OANDA Demo Live Quote Derived Post Trade Evidence V1

## 1. Live Quote Derived Owner Run Classification

Owner-run classification captured:

- `script_status`: `LIVE_QUOTE_DERIVED_DEMO_ORDER_ATTEMPTED`
- `classification`: `LIVE_QUOTE_DERIVED_DEMO_ORDER_ATTEMPTED`
- pricing fetch performed: true
- broker network call performed: true
- order placement performed: true
- order attempt count: 1
- endpoint: OANDA practice/demo orders endpoint only

This report captures sanitized owner-provided post-trade evidence only. Codex did not call OANDA,
place another order, read credentials, read account IDs, read Windows Vault, read environment
variables, read `.env`, create automation, stage, commit, or push.

## 2. Pricing Snapshot Evidence

Sanitized owner-provided pricing snapshot:

- pricing status code: 200
- instrument: `EUR_USD`
- bid: `1.13539`
- ask: `1.13599`
- pricing time: `2026-06-24T21:47:33.713676094Z`
- endpoint type: OANDA practice/demo pricing endpoint only

This pricing snapshot was used by the owner-run live-quote-derived runtime path to compute SL/TP
from the current executable spread context before order construction.

## 3. Broker Network Result

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

The owner-run live-quote-derived command reached the OANDA practice/demo orders endpoint and
produced broker transaction evidence.

## 4. Sanitized Transaction Evidence

Sanitized owner-provided order evidence:

- derived stop loss: `1.13519`
- derived take profit: `1.13629`
- client order ID: `AIOS-DEMO-LIVEQUOTE-DERIVED-OWNER-RUNTIME-001`
- order create transaction ID: `319`
- order fill transaction ID: `320`
- order cancel transaction ID: null
- related transaction IDs: `319`, `320`, `321`, `322`

No token value, account ID value, credential value, authorization header, password, raw broker
payload, or private account identifier is included in this report.

## 5. Fill Status

Fill status captured:

- `orderFillTransaction` observed: true
- filled demo trade evidence captured: true
- order fill transaction ID: `320`
- no cancel transaction observed

This proves broker reachability, vault-backed owner runtime credentials, live quote fetch, SL/TP
derivation, order creation, and order fill for this OANDA practice/demo attempt.

## 6. Cancel Status

Cancel status captured:

- order cancel transaction ID: null
- cancel reason: null
- `TAKE_PROFIT_ON_FILL_LOSS` observed on this attempt: false

The prior repeated cancel pattern was not observed in this owner-provided result.

## 7. Profitability Status

Profitability status:

- profit claimed: false
- realized P/L evidence captured: false
- unrealized P/L evidence captured: false
- `120%` claim supported: false

This is filled demo trade evidence, not profit proof. Realized P/L has not been captured in this
packet, so no profit, strategy edge, allocation progress, campaign progress, or return claim is
made.

## 8. Secret Redaction Proof

Secret redaction proof:

- credential value printed: false
- account ID value printed: false
- token value included in report: false
- account ID value included in report: false
- credential persistence to repo: false
- account ID persistence to repo: false
- `.env` read by Codex: false
- environment variable read by Codex: false
- Windows Vault read by Codex: false

This report stores only sanitized owner-provided outcome fields.

## 9. No Second Order Rule

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

## 10. Next Safe Packet

Next safe packet:

```text
AIOS-FOREX-OANDA-DEMO-FILLED-TRADE-RESULT-BUCKET-V1
```

That packet should classify the filled demo trade result bucket and capture realized P/L evidence if
available, without calling OANDA, reading secrets, placing another order, creating automation,
staging, committing, or pushing unless separately approved.
