# AIOS Forex OANDA Demo Read-Only Preflight From Vault V1

## Packet Context

Packet ID: `AIOS-FOREX-OANDA-DEMO-READ-ONLY-PREFLIGHT-FROM-VAULT-V1`

Lane: `OANDA_DEMO_READ_ONLY_PREFLIGHT_FROM_VAULT`

Mode: local APPLY, no commit, no push.

## What Was Created

- `automation/forex_engine/oanda_demo_read_only_preflight_from_vault_v1.py`
- `scripts/forex_delivery/run_oanda_demo_read_only_preflight_from_vault_v1.py`
- `tests/forex_engine/test_oanda_demo_read_only_preflight_from_vault_v1.py`
- this report
- the separate campaign anchor report

## Why This Is The Next Milestone

The previous secure credential persistence milestone established the approved Windows vault labels:

- `AIOS_OANDA_DEMO_ACCESS_TOKEN`
- `AIOS_OANDA_DEMO_ACCOUNT_ID`

This milestone is the next step because it composes that vault boundary with the previously landed read-only OANDA demo account permission preflight. The credential values remain runtime-only and are redacted from returned evidence.

## What It Proves

This milestone only proves whether the vault-backed demo credential path can perform read-only OANDA practice account preflight.

It can prove whether the token-visible demo account can access OANDA practice account metadata endpoints through the read-only path.

## What It Does Not Prove

This milestone does not place an order.

This milestone does not prove profitability.

This milestone does not prove 120% return.

This milestone does not authorize live trading.

It does not authorize broker writes, order mutation, position mutation, scheduler execution, daemon execution, webhook execution, or autonomous trading.

## Exact Safety Boundaries

- DEMO only.
- Windows vault adapter boundary only.
- Runtime-only credential values.
- No `.env` read.
- No `.env` write.
- No plaintext credential file.
- No repo credential persistence.
- No account ID persistence in repo.
- No credential or account ID printing.
- No live endpoint.
- No `/orders`.
- No `/trades`.
- No `/positions`.
- No `/transactions`.
- No POST, PUT, PATCH, or DELETE broker request.
- No commit.
- No push.

## Allowed Endpoints

- `GET https://api-fxpractice.oanda.com/v3/accounts`
- `GET https://api-fxpractice.oanda.com/v3/accounts/<runtime_account_id>`
- `GET https://api-fxpractice.oanda.com/v3/accounts/<runtime_account_id>/summary`
- `GET https://api-fxpractice.oanda.com/v3/accounts/<runtime_account_id>/instruments`

## Forbidden Endpoints

- `/orders`
- `/trades`
- `/positions`
- `/transactions`
- `api-fxtrade.oanda.com`
- any non-practice OANDA base URL
- any broker mutation endpoint

## Credential Redaction Policy

The access token is loaded only through the approved vault adapter label and is treated as runtime-only. Returned evidence recursively replaces token values with `REDACTED_RUNTIME_ACCESS_TOKEN` or `REDACTED_RUNTIME_ONLY_REFERENCE`.

## Account ID Redaction Policy

The demo account ID is loaded only through the approved vault adapter label and is treated as runtime-only. Returned evidence recursively replaces account ID values with `REDACTED_RUNTIME_ACCOUNT_ID` or `REDACTED_RUNTIME_ONLY_REFERENCE`.

## Owner Manual Run Command Template

```powershell
python scripts/forex_delivery/run_oanda_demo_read_only_preflight_from_vault_v1.py --print-template
```

```powershell
python scripts/forex_delivery/run_oanda_demo_read_only_preflight_from_vault_v1.py --execute-read-only-preflight-from-vault --i-confirm-demo-only --i-confirm-read-only-preflight --i-confirm-windows-vault-only --i-confirm-no-env-file --i-confirm-no-repo-persistence --i-confirm-no-live-credentials --i-confirm-token-visible-account --i-confirm-no-order-endpoint --i-confirm-no-trade-mutation --i-confirm-no-second-order-attempt
```

No token value and no account ID value should be placed in the command.

## Validation Results

Local validation in this APPLY lane:

- `python -m py_compile automation/forex_engine/oanda_demo_read_only_preflight_from_vault_v1.py tests/forex_engine/test_oanda_demo_read_only_preflight_from_vault_v1.py scripts/forex_delivery/run_oanda_demo_read_only_preflight_from_vault_v1.py`: PASS
- `python -m pytest tests/forex_engine/test_oanda_demo_read_only_preflight_from_vault_v1.py -q`: PASS, 25 passed
- `python -m compileall automation/forex_engine tests/forex_engine scripts/forex_delivery`: BLOCKED by sandbox process-launch failure `CreateProcessAsUserW failed: 1312`
- `git diff --check`: PASS

## Exact Next Safe Action After PR Lands

Owner manual action only: run the print-template command, confirm the Windows vault labels exist locally, then run the read-only preflight command only if the owner wants metadata-only OANDA practice account verification. Do not place an order.
