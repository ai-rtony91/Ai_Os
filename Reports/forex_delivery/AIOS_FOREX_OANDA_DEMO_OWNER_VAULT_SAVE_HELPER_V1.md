# AIOS Forex OANDA Demo Owner Vault Save Helper V1

## Purpose

This lane created an owner-run Windows Vault save helper for the two approved OANDA demo/practice labels required by the existing vault-backed read-only preflight.

Approved labels:

```text
AIOS_OANDA_DEMO_ACCESS_TOKEN
AIOS_OANDA_DEMO_ACCOUNT_ID
```

## What Was Created

- `automation/forex_engine/oanda_demo_owner_vault_save_helper_v1.py`
- `scripts/forex_delivery/run_oanda_demo_owner_vault_save_helper_v1.py`
- `tests/forex_engine/test_oanda_demo_owner_vault_save_helper_v1.py`
- this report

## Safety Boundaries

- No OANDA call.
- No order placement.
- No existing Windows Vault read.
- No `.env` read.
- No environment variable read.
- No token or account value CLI argument support.
- No token or account value printing.
- No repo secret persistence.
- No scheduler, daemon, webhook, or background process.
- No commit.
- No push.

The helper prompts the owner interactively with hidden input, then writes the two runtime values to Windows Credential Manager through `CredWriteW` at owner runtime only.

## Owner Commands

Template:

```powershell
python scripts/forex_delivery/run_oanda_demo_owner_vault_save_helper_v1.py --print-template
```

Owner save:

```powershell
python scripts/forex_delivery/run_oanda_demo_owner_vault_save_helper_v1.py --owner-save-to-windows-vault --i-confirm-demo-only --i-confirm-windows-vault-only --i-confirm-no-env-file --i-confirm-no-repo-persistence --i-confirm-no-value-printing
```

Do not add token or account values to the command.

## Expected Helper Output

The helper returns sanitized JSON only.

Success means:

```text
script_status: OWNER_VAULT_SAVE_SAVED
labels_saved: true
```

Blocked output keeps `labels_saved: false` and does not include runtime values.

## Exact Read-Only Preflight Rerun Command

After `labels_saved: true`, the owner may run:

```powershell
python scripts/forex_delivery/run_oanda_demo_read_only_preflight_from_vault_v1.py --execute-read-only-preflight-from-vault --i-confirm-demo-only --i-confirm-read-only-preflight --i-confirm-windows-vault-only --i-confirm-no-env-file --i-confirm-no-repo-persistence --i-confirm-no-live-credentials --i-confirm-token-visible-account --i-confirm-no-order-endpoint --i-confirm-no-trade-mutation --i-confirm-no-second-order-attempt
```

## Validation Plan

Run:

```powershell
python -m py_compile automation/forex_engine/oanda_demo_owner_vault_save_helper_v1.py scripts/forex_delivery/run_oanda_demo_owner_vault_save_helper_v1.py tests/forex_engine/test_oanda_demo_owner_vault_save_helper_v1.py
python -m pytest tests/forex_engine/test_oanda_demo_owner_vault_save_helper_v1.py -q
git diff --check
git status --short --branch
```

## Stop Point

Codex must stop after creating the helper, wrapper, tests, report, and validator evidence. Codex must not run the owner-save command, stage, commit, or push.
