# Forex OANDA Live 403 Read-Only Classifier V1

## Purpose

This packet classifies a prior OANDA live `403` response from a controlled attempt
without issuing another order.

## Classifier behavior

- Runs in dry-run/read-only mode by default.
- Requires explicit owner flag:
  `--owner-approved-readonly-live-403-classifier`.
- Uses an existing `Env:BW_SESSION` and then loads:
  `AIOS / OANDA / Live / Broker Runtime` from Bitwarden.
- Probes only:
  - `GET https://api-fxtrade.oanda.com/v3/accounts`
  - `GET https://api-fxtrade.oanda.com/v3/accounts/{account_id}/summary`
- Never submits orders, never calls `/orders`, never writes/mutates state.
- Returns a full classifier result and safe_next_action for owner review.

## What the classifier distinguishes

- `ACCOUNT_NOT_VISIBLE_TO_TOKEN`
  - OANDA account list returns account IDs, but configured account is missing.
- `ACCOUNT_LIST_FORBIDDEN`
  - Token lacks account list permission (`401`/`403` on `/accounts`).
- `ACCOUNT_SUMMARY_FORBIDDEN`
  - Accounts are visible, but summary endpoint is forbidden (`401`/`403`).
- `ACCOUNT_VISIBLE_SUMMARY_OK_ORDER_FORBIDDEN`
  - Accounts and summary are visible (`200`), consistent with token not permitting order operations.
- `BROKER_UNAVAILABLE`
  - Network/5xx issue before a definitive permission decision can be made.
- `REPAIR_REQUIRED`
  - Unexpected payloads or protocol mismatch.

## Owner session requirement

Owner must provide `BW_SESSION` in the PowerShell shell and use the Bitwarden
session helper pattern. This classifier does not read `.env`.

## Redaction

- Outputs are redacted:
  - token -> `REDACTED_TOKEN`
  - account id -> `REDACTED_ACCOUNT_ID`
  - BW session -> `REDACTED_SESSION`
- No raw `Authorization` headers or `Bearer` credentials are written in stdout,
  state file, or report.

