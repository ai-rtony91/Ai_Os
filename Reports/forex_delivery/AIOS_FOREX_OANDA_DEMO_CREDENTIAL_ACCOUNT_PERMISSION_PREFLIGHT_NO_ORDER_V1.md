# AIOS Forex OANDA Demo Credential Account Permission Preflight No Order V1

## Packet Context

Packet ID: AIOS-FOREX-OANDA-DEMO-CREDENTIAL-ACCOUNT-PERMISSION-PREFLIGHT-NO-ORDER-V1

Branch: feature/forex-oanda-demo-credential-account-permission-preflight-no-order-v1

Mission outcome: created the read-only OANDA demo credential/account permission preflight module, owner-run script, and tests for diagnosing the first attempt HTTP 403 without placing another order.

## Why This Is Read-Only

This lane only plans and supports GET requests against OANDA practice account metadata endpoints. It does not create, update, patch, cancel, or delete orders. It does not mutate trades, positions, accounts, or subscriptions.

Codex validation does not call OANDA. Tests use injected fake GET callables only.

## Why It Does Not Place Orders

The preflight evaluator and owner script reject mutation endpoints. The endpoint validator rejects any URL containing `/orders`, `/trades`, `/positions`, `/transactions`, or `api-fxtrade.oanda.com`.

There is no POST order payload and no order execution path in this lane.

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

## Runtime Env Var Rule

The owner-run script reads runtime values only from process environment variables:

- `OANDA_DEMO_ACCESS_TOKEN`
- `OANDA_DEMO_ACCOUNT_ID`

The script does not read `.env`, does not print runtime values, and does not persist credentials or account identifiers.

## No Credential Persistence Rule

Credentials remain runtime-only. Returned evidence redacts token, authorization, credential, secret, password, and API-key-looking fields.

## No Account ID Persistence Rule

The runtime account ID remains runtime-only. Returned evidence redacts account ID fields and any `id` value that equals the runtime account ID.

## Prior 403 Evidence Dependency

This lane depends on `AIOS_FOREX_OANDA_DEMO_FIRST_ORDER_ATTEMPT_403_EVIDENCE_CAPTURE_V1`, which captured that the first OANDA practice transport attempt reached the broker endpoint once, returned HTTP 403 forbidden, placed no order, observed no order create or fill transaction, and consumed the one-order attempt cap.

## Expected Root-Cause Outputs

The preflight returns:

- token validity status
- account visibility to token
- account details access
- account summary access
- instruments access
- EUR/USD availability
- practice account confirmation
- trading permission likelihood
- likely 403 root cause classification

Possible root-cause classifications include token expired, token/account mismatch, account not visible to token, practice/live mismatch, account permission restriction, order permission restriction, or unknown requiring owner broker review.

## Validation Results

Targeted validation after implementation:

- `python -m py_compile automation/forex_engine/oanda_demo_credential_account_permission_preflight_no_order_v1.py tests/forex_engine/test_oanda_demo_credential_account_permission_preflight_no_order_v1.py scripts/forex_delivery/run_oanda_demo_credential_account_permission_preflight_no_order_v1.py`: PASS
- `python -m pytest tests/forex_engine/test_oanda_demo_credential_account_permission_preflight_no_order_v1.py -q`: PASS, 37 passed
- `python -m compileall automation/forex_engine tests/forex_engine scripts/forex_delivery`: PASS
- `git diff --check`: PASS

## Next Safe Action After PR Lands

OWNER MANUAL ACTION ONLY: run the read-only preflight with runtime-only OANDA demo credentials only if the owner still wants broker permission diagnosis and understands no second order attempt is allowed.

## Next Milestone After Successful Read-Only Preflight

If the read-only preflight passes and owner review confirms the permission path, the next milestone is secure credential persistence design. That milestone must remain separate, approval-gated, and must not persist credentials until a dedicated secret-handling design is reviewed.
