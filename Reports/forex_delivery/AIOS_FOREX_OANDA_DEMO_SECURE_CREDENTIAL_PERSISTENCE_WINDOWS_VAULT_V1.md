# AIOS Forex OANDA Demo Secure Credential Persistence Windows Vault V1

## Packet Context

Packet ID: `AIOS-FOREX-OANDA-DEMO-SECURE-CREDENTIAL-PERSISTENCE-WINDOWS-VAULT-V1`

Branch: `feature/forex-oanda-demo-secure-credential-persistence-windows-vault-v1`

Mission outcome: created a DEMO-only secure credential persistence boundary for OANDA demo credentials using a Windows OS-backed vault adapter design. The lane is safe by default, testable with fake vault callables, and does not persist real credentials during Codex validation.

## Why DEMO Persistence Is Now Allowed

The prior read-only credential/account preflight proved the demo token was valid and diagnosed the first attempt 403 as an account/token mismatch. Persistence is now scoped only to the OANDA demo token and the owner-confirmed token-visible demo account reference.

The real account value is intentionally not written in this report or committed source text. Repo evidence refers to it only as `REDACTED_TOKEN_VISIBLE_DEMO_ACCOUNT_ID`.

## Why Live Credential Persistence Remains Blocked

Live credential persistence remains blocked because this lane is not a live broker lane, not an order lane, and not a production execution lane. The evaluator blocks live credentials, live mode, broker calls, broker writes, order mutation, position mutation, schedulers, daemons, webhooks, and autonomous execution.

## Account Reference Rules

The token-visible demo account must be used because the prior read-only preflight showed it is visible to the valid demo token. This lane records that account only as `REDACTED_TOKEN_VISIBLE_DEMO_ACCOUNT_ID`.

The prior mismatched account is rejected for this token and is recorded only as `REDACTED_MISMATCHED_ACCOUNT_ID`.

## Windows Vault Rule

Credential persistence is limited to Windows OS-backed credential storage or an equivalent vault adapter boundary. This PR does not claim robust plain `cmdkey` load support because `cmdkey` can store and delete but is not a safe secret retrieval interface for the read-only preflight path.

The owner-run script exposes the workflow boundary and injectable adapter hooks. Tests use fake callables only. Real vault save/load/delete remains owner-run only and should be completed through a Windows vault or SecretManagement-backed adapter in the next lane.

## Blocked Persistence Targets

- no `.env` read or write
- no plaintext secret file
- no repo-stored token
- no repo-stored account identifier
- no committed vault file
- no report or log printing of token or account ID
- no command-line token argument

## Broker And Order Safety

- no OANDA call by Codex
- no broker call
- no `/orders` endpoint
- no order placement
- no trade mutation
- no position mutation
- no scheduler
- no daemon
- no webhook
- no autonomous trading

## Credential Names

The allowed Windows vault credential names are:

- `AIOS_OANDA_DEMO_ACCESS_TOKEN`
- `AIOS_OANDA_DEMO_ACCOUNT_ID`

These names are labels only. They are not secret values.

## Redaction Rules

Returned evidence recursively redacts:

- access token values
- runtime account ID values
- authorization fields
- password fields
- secret fields
- API-key fields
- credential-looking fields
- values matching runtime-only secrets

The evaluator returns redacted account references:

- accepted account: `REDACTED_TOKEN_VISIBLE_DEMO_ACCOUNT_ID`
- rejected account: `REDACTED_MISMATCHED_ACCOUNT_ID`

## Execution Authority

All execution authority fields remain false:

- `execution_allowed`
- `demo_order_allowed`
- `live_order_allowed`
- `broker_write_allowed`
- `broker_call_allowed`
- `autonomous_order_allowed`
- `scheduler_allowed`
- `daemon_allowed`
- `webhook_allowed`
- `order_mutation_allowed`
- `position_mutation_allowed`

## Validation Results

Targeted validation after implementation:

- `python -m py_compile automation/forex_engine/oanda_demo_secure_credential_persistence_windows_vault_v1.py tests/forex_engine/test_oanda_demo_secure_credential_persistence_windows_vault_v1.py scripts/forex_delivery/run_oanda_demo_secure_credential_persistence_windows_vault_v1.py`: PASS
- `python -m pytest tests/forex_engine/test_oanda_demo_secure_credential_persistence_windows_vault_v1.py -q`: PASS, 39 passed
- `python -m compileall automation/forex_engine tests/forex_engine scripts/forex_delivery`: PASS
- `git diff --check`: PASS

## Exact Next Safe Owner Action After PR Lands

Owner manual action only: review the redacted vault boundary and save DEMO credentials only through an OS-backed Windows vault adapter. Do not place an order, do not call OANDA, and do not use live credentials.

## Next Milestone

After successful vault save/load, the next milestone is:

```text
AIOS-FOREX-OANDA-DEMO-READ-ONLY-PREFLIGHT-FROM-VAULT-V1
```
