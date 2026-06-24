# AIOS Forex OANDA Demo Post Trade Evidence Capture Owner Run V1

## 1. Owner Run Classification

Owner-run classification captured:

- `script_status`: `VAULT_BACKED_DEMO_ONE_ORDER_ATTEMPTED`
- `classification`: `VAULT_BACKED_DEMO_ONE_ORDER_ATTEMPTED`
- transport status: `TRANSPORT_ATTEMPTED_OANDA_DEMO_ORDER_ONCE`
- next safe action: `capture_sanitized_post_trade_evidence_and_do_not_rerun`

This report is sanitized evidence only. Codex did not rerun the transport, call OANDA, read credentials, read account IDs, read Windows Vault, read environment variables, read `.env`, place another demo order, or place any live order.

## 2. Broker Network Result

Owner-provided broker network result:

- broker network call performed: true
- endpoint type: OANDA practice/demo orders endpoint only
- HTTP status code: 201
- HTTP result: created
- live endpoint used: false
- dotenv read: false
- credential value printed: false
- account ID value printed: false

The owner result indicates the demo transport reached OANDA practice and received a created response for the attempted order transaction sequence.

## 3. Order Attempt Count

Order attempt count captured:

- order attempt count: 1
- one order only: true
- second order allowed: false
- no second order attempted or authorized by this report

The one-order cap is now consumed for this lane. Any continuation must proceed through evidence review and a separate approved packet, not another order attempt.

## 4. Sanitized Transaction Evidence

Sanitized owner-provided transaction evidence:

- instrument: `EUR_USD`
- direction: `BUY`
- units: 1
- order type: `MARKET`
- stop loss: `1.07000`
- take profit: `1.07100`
- client order ID: `AIOS-DEMO-ONE-ORDER-OWNER-RUNTIME-001`
- order create transaction ID: `313`
- order cancel transaction ID: `314`
- related transaction IDs: `313`, `314`

No token value, account ID value, credential value, authorization header, password, or raw broker credential material is included in this report.

## 5. Fill Status

Fill status captured:

- order placement performed by owner-run transport: true
- no `orderFillTransaction` observed
- no successful fill is claimed
- no open position is claimed
- no profit is claimed

The demo order reached OANDA practice, but the available owner-provided evidence shows a create transaction followed by a cancel transaction, not a filled trade.

## 6. Cancel Reason

Cancel reason captured:

```text
TAKE_PROFIT_ON_FILL_LOSS
```

This indicates OANDA canceled the order because the take-profit-on-fill configuration was invalid for the submitted order context.

## 7. SL/TP Attachment Status

Stop loss and take profit were present in the owner-submitted command:

- stop loss submitted: `1.07000`
- take profit submitted: `1.07100`
- stop loss requirement present: true
- take profit requirement present: true

Because no `orderFillTransaction` was observed and OANDA canceled the order with `TAKE_PROFIT_ON_FILL_LOSS`, no active filled-position stop loss or take profit attachment is claimed.

## 8. Secret Redaction Proof

Secret redaction proof:

- Windows Credential Manager labels were loaded by the owner-run wrapper with values redacted.
- credential value printed: false
- account ID value printed: false
- token value included in report: false
- account ID value included in report: false
- credential persistence to repo: false
- `.env` read: false
- environment variable read by Codex: false
- Windows Vault read by Codex: false

This report stores only sanitized owner-provided outcome fields.

## 9. No Second Order Rule

No second order is allowed by this evidence capture.

The captured state is:

- one order only: true
- order attempt count: 1
- second order allowed: false
- no rerun authorized
- no retry loop authorized
- no scheduler, daemon, webhook, or unattended trading path authorized

Any new broker action would require a separate Human Owner-approved packet and must not be inferred from this report.

## 10. Operational Interpretation

The demo transport reached OANDA and created a market order transaction, but the order was canceled by OANDA with TAKE_PROFIT_ON_FILL_LOSS. This is broker-side order validation/cancel evidence, not profit evidence and not a filled trade.

Operationally, this means the vault-backed owner runtime path reached the OANDA practice order endpoint and produced useful broker-side rejection evidence. It does not prove profitability, does not prove execution quality, does not prove campaign progress, and does not support a `+120 percent` claim.

## 11. Next Safe Packet

Next safe packet:

```text
AIOS-FOREX-OANDA-DEMO-RESULT-BUCKET-AND-NEXT-ALLOCATION-AFTER-CANCEL-V1
```

That packet must classify the canceled demo attempt, preserve no-second-order status, and decide the next allocation or repair path without calling OANDA, reading secrets, creating automation, staging, committing, or pushing unless separately approved.
