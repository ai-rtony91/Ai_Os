# AIOS Forex OANDA Demo Vault Missing Credential Recovery V1

## 1. Current Blocker

Current blocker:

```text
VAULT_PREFLIGHT_BLOCKED_MISSING_TOKEN / vault_demo_access_token_missing
```

Meaning: the existing read-only OANDA demo vault preflight could not find or load the approved demo access-token value from Windows Vault. This report does not verify the value, read the vault, call OANDA, read `.env`, or place an order.

## 2. Required Windows Vault Labels

Create or update exactly these Windows Generic Credential targets:

```text
AIOS_OANDA_DEMO_ACCESS_TOKEN
AIOS_OANDA_DEMO_ACCOUNT_ID
```

The labels are safe to document. The values are not safe to document.

## 3. Owner Secret Handling Rule

The owner must keep the OANDA demo/practice access token and account ID runtime-only.

Do not paste either value into Codex, ChatGPT, Claude, GitHub, a markdown report, `.env`, PowerShell command history, screenshots, telemetry, or any repo file.

## 4. Manual Save Step Placeholder

Use Windows Credential Manager manually. Do not use a command that places the token or account ID in shell history.

For `AIOS_OANDA_DEMO_ACCESS_TOKEN`:

1. Open Windows Credential Manager.
2. Open Windows Credentials.
3. Add or edit a Generic Credential.
4. Set the Internet or network address to `AIOS_OANDA_DEMO_ACCESS_TOKEN`.
5. Set the user name to `AIOS_OWNER_RUNTIME_ONLY`.
6. Paste the OANDA demo/practice access token into the password field.
7. Save.

For `AIOS_OANDA_DEMO_ACCOUNT_ID`:

1. Open Windows Credential Manager.
2. Open Windows Credentials.
3. Add or edit a Generic Credential.
4. Set the Internet or network address to `AIOS_OANDA_DEMO_ACCOUNT_ID`.
5. Set the user name to `AIOS_OWNER_RUNTIME_ONLY`.
6. Paste the token-visible OANDA demo/practice account ID into the password field.
7. Save.

Stop if Windows shows a field name or flow that makes the secret value visible outside Credential Manager.

## 5. Exact Rerun Command

After both vault labels are saved, the owner may rerun the existing read-only preflight manually:

```powershell
python scripts/forex_delivery/run_oanda_demo_read_only_preflight_from_vault_v1.py --execute-read-only-preflight-from-vault --i-confirm-demo-only --i-confirm-read-only-preflight --i-confirm-windows-vault-only --i-confirm-no-env-file --i-confirm-no-repo-persistence --i-confirm-no-live-credentials --i-confirm-token-visible-account --i-confirm-no-order-endpoint --i-confirm-no-trade-mutation --i-confirm-no-second-order-attempt
```

This command must not include token or account ID values.

## 6. PASS Next Packet

If the redacted result shows `VAULT_PREFLIGHT_READ_ONLY_ATTEMPTED` and the read-only permission evidence is favorable, the next safe packet is:

```text
AIOS-FOREX-OANDA-DEMO-VAULT-PREFLIGHT-PASS-EVIDENCE-CAPTURE-V1
```

That packet should create one sanitized PASS evidence report only. It must not call OANDA, read credentials, place orders, stage, commit, or push.

## 7. BLOCKED Next Packet

If the rerun still returns `VAULT_PREFLIGHT_BLOCKED_*`, HTTP `401`, HTTP `403`, HTTP `404`, missing account visibility, missing instrument access, or any unclear permission result, the next safe packet is:

```text
AIOS-FOREX-OANDA-DEMO-VAULT-PREFLIGHT_403_BLOCKED_EVIDENCE_CAPTURE_V1
```

That packet should create one sanitized blocked-evidence report only. It must preserve the no-second-order-attempt boundary and must not retry an order.
