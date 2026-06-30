# Forex OANDA Live Account Binding Repair V1

## Purpose

This packet repairs the account-binding mismatch condition where:
- The OANDA live API token is valid and can list accounts (`200` from
  `https://api-fxtrade.oanda.com/v3/accounts`).
- The configured Bitwarden account id is not visible to that token.

## Scope

- `--owner-approved-readonly-account-binding-inspect`:
  - requires `BW_SESSION`
  - reads Bitwarden item `AIOS / OANDA / Live / Broker Runtime`
  - uses only `GET https://api-fxtrade.oanda.com/v3/accounts`
  - compares visible account ids to configured `broker_account_id`
  - reports fingerprinted visibility state
- `--owner-approved-update-bitwarden-account-binding`:
  - requires the same runtime checks as inspect
  - accepts `--select-visible-account-index` (1-based)
  - updates **only** `broker_account_id` in Bitwarden item

## Safety and boundaries

- No `POST` requests.
- No `/orders` endpoint calls.
- No live order execution.
- No money movement.
- No scheduler/daemon/webhook startup.
- No `.env` read.
- No raw `BW_SESSION`, raw token, raw account IDs, or raw Bitwarden JSON in stdout/state/report.

## Validators

- `python -m py_compile scripts/forex_delivery/run_forex_oanda_live_account_binding_repair_v1.py`
- `python -m pytest tests/forex_engine/test_forex_oanda_live_account_binding_repair_v1.py -q`
- `python scripts/forex_delivery/run_forex_oanda_live_account_binding_repair_v1.py`
- `git diff --check`

## Statuses

- `ACCOUNT_BINDING_REPAIR_OWNER_RUNTIME_REQUIRED`
- `ACCOUNT_BINDING_REPAIR_CREDENTIAL_ACCESS_REQUIRED`
- `ACCOUNT_BINDING_REPAIR_INSPECT_READY`
- `ACCOUNT_BINDING_REPAIR_CONFIGURED_ACCOUNT_VISIBLE`
- `ACCOUNT_BINDING_REPAIR_CONFIGURED_ACCOUNT_NOT_VISIBLE`
- `ACCOUNT_BINDING_REPAIR_UPDATE_READY`
- `ACCOUNT_BINDING_REPAIR_UPDATE_APPLIED`
- `ACCOUNT_BINDING_REPAIR_UPDATE_FAILED`
- `ACCOUNT_BINDING_REPAIR_INDEX_INVALID`
- `ACCOUNT_BINDING_REPAIR_BROKER_UNAVAILABLE`

## Safe next action

- If inspect shows configured account not visible:
  `run the read-only classifier again with owner runtime flag to confirm status progression.`
- If update succeeds:
  `rerun read-only 403 classifier with --owner-approved-readonly-account-binding-inspect.`
