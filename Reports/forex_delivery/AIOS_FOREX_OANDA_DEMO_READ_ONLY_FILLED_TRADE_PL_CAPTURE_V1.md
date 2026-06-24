# AIOS Forex OANDA Demo Read Only Filled Trade PL Capture V1

## 1. Prior Filled Trade Evidence

Prior sanitized owner-run evidence classified the live-quote-derived OANDA demo result as:

- RESULT_BUCKET: FILLED_PNL_UNKNOWN
- FILL_STATUS: FILLED
- PROFITABILITY_STATUS: PNL_NOT_CAPTURED
- ALLOCATION_DECISION: NO_NEXT_ALLOCATION_UNTIL_PNL_CAPTURE
- orderCreateTransaction id: 319
- orderFillTransaction id: 320
- relatedTransactionIDs: 319, 320, 321, 322
- cancel_reason: null

This is filled demo trade evidence, not profit proof.

## 2. Tooling Created

Created owner-run read-only P/L capture tooling:

- `automation/forex_engine/oanda_demo_read_only_filled_trade_pl_capture_v1.py`
- `scripts/forex_delivery/run_oanda_demo_read_only_filled_trade_pl_capture_v1.py`
- `tests/forex_engine/test_oanda_demo_read_only_filled_trade_pl_capture_v1.py`

The tooling defaults to a ready/template state and does not call OANDA, read Windows Vault, read environment variables, read `.env`, place orders, close trades, or mutate positions unless the owner explicitly runs the execute flag with confirmations.

## 3. Owner Runtime Boundary

Supported CLI modes:

```text
--print-template
--execute-read-only-filled-trade-pl-capture-from-vault
```

The execute mode is owner-runtime-only. It loads only these approved Windows Vault labels:

```text
AIOS_OANDA_DEMO_ACCESS_TOKEN
AIOS_OANDA_DEMO_ACCOUNT_ID
```

The CLI does not accept token or account ID values as command-line arguments.

## 4. Read-Only Endpoint Allowlist

The tooling allows only OANDA practice/demo GET endpoints:

```text
GET https://api-fxpractice.oanda.com/v3/accounts
GET https://api-fxpractice.oanda.com/v3/accounts/<runtime_account_id>
GET https://api-fxpractice.oanda.com/v3/accounts/<runtime_account_id>/summary
GET https://api-fxpractice.oanda.com/v3/accounts/<runtime_account_id>/openTrades
GET https://api-fxpractice.oanda.com/v3/accounts/<runtime_account_id>/openPositions
GET https://api-fxpractice.oanda.com/v3/accounts/<runtime_account_id>/transactions
```

POST, PUT, PATCH, DELETE, live endpoints, order placement, trade close, order mutation, trade mutation, and position mutation are blocked.

## 5. Evidence Capture Scope

Owner execute mode is designed to capture:

- account summary
- NAV and balance snapshot when returned by OANDA
- open trades
- open positions
- transaction evidence around 319 through 322
- filled trade P/L evidence when present in read-only responses
- sanitized account and credential redaction proof

## 6. P/L Classification Standard

The tooling classifies captured P/L evidence as one of:

- FILLED_TRADE_PL_POSITIVE
- FILLED_TRADE_PL_NEGATIVE
- FILLED_TRADE_PL_ZERO
- FILLED_TRADE_PL_OPEN_UNREALIZED
- FILLED_TRADE_PL_NOT_FOUND
- BLOCKED_BY_READ_ONLY_PL_CAPTURE_FAILURE

Positive, negative, or zero classifications require explicit captured P/L values. Open unrealized classification requires read-only open trade or open position evidence. Missing evidence remains not found and does not authorize allocation.

## 7. Secret Redaction Standard

All outputs are sanitized JSON. Runtime token and account ID values are redacted in nested payloads, URLs, vault adapter results, endpoint responses, and error boundaries.

The tooling records proof fields for:

- credential value printed: false
- account ID value printed: false
- `.env` read: false
- environment read: false
- live endpoint used: false
- credential persistence to repo: false

## 8. Codex Execution Boundary

Codex did not call OANDA, read Windows Vault, read credentials, read account IDs, read environment variables, read `.env`, place an order, close a trade, modify a position, create a scheduler, create a daemon, stage files, commit, or push.

## 9. Owner Command Template

```text
python scripts/forex_delivery/run_oanda_demo_read_only_filled_trade_pl_capture_v1.py --execute-read-only-filled-trade-pl-capture-from-vault --instrument EUR_USD --order-create-transaction-id 319 --order-fill-transaction-id 320 --related-transaction-ids 319 320 321 322 --client-order-id AIOS-DEMO-LIVEQUOTE-DERIVED-OWNER-RUNTIME-001 --i-confirm-demo-only --i-confirm-read-only-pl-capture --i-confirm-windows-vault-only --i-confirm-no-env-file --i-confirm-no-repo-persistence --i-confirm-no-live-endpoint --i-confirm-no-order --i-confirm-no-close-trade --i-confirm-no-mutation --i-confirm-no-second-order --i-confirm-no-profit-claim
```

## 10. Next Safe Action

The next safe action is owner review of the read-only P/L capture template. Codex must not run it. Any owner-run output should be captured in a separate sanitized result evidence packet before profit, loss, allocation, or next-step claims are made.

No next allocation is authorized until read-only P/L capture produces explicit evidence.
