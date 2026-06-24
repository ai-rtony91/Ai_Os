# AIOS Forex OANDA Demo Read-Only Preflight Result Capture V1

## Purpose

This report captures the owner-run OANDA demo vault-backed read-only preflight result as sanitized repo evidence.

Codex did not call OANDA, did not read Windows Vault, did not read credentials, did not read an account ID, did not read `.env`, and did not place an order while creating this report.

## Sanitized Owner Result

- status: `VAULT_PREFLIGHT_READ_ONLY_ATTEMPTED`
- broker network call performed by owner-run preflight: true
- credential read performed at owner runtime: true
- account ID read performed at owner runtime: true
- credential value printed: false
- account ID value printed: false
- blockers: none
- token valid: true
- account visible to token: true
- account details accessible: true
- account summary accessible: true
- instruments accessible: true
- `EUR_USD` available: true
- trading permission likely from read-only metadata: true
- likely prior 403 root cause: `order_permission_restricted`
- endpoints attempted: 4
- read-only only: true
- order placement performed: false
- orders endpoint called: false
- live endpoint used: false
- dotenv read: false
- vault value persisted to repo: false

## Evidence Interpretation

The approved Windows Vault labels were loaded by the owner-run command at runtime only. The values are not present in this report.

The OANDA practice metadata path reached approved read-only endpoints for account visibility, account details, account summary, and instruments. The result supports that the account/token path is valid for read-only OANDA practice metadata and that `EUR_USD` is available.

This does not prove order permission, live trading readiness, profitability, or a guaranteed campaign outcome. The prior broker write rejection remains relevant because the likely root cause is order-permission restricted.

## No Broker Mutation Evidence

- No order was placed.
- No order endpoint was called.
- No live endpoint was used.
- No credential value was printed.
- No account ID value was printed.
- No credential or account value was persisted to the repo.
- No scheduler, daemon, webhook, retry loop, or unattended trading path was created.

## Execution Authority

Execution authority remains false:

- execution allowed: false
- demo order allowed: false
- live order allowed: false
- autonomous order allowed: false
- scheduler allowed: false
- daemon allowed: false
- webhook allowed: false

## Next Safe Use

The sanitized read-only preflight result may feed a separate one-trade readiness evaluator. It does not authorize Codex to call OANDA, place a demo order, place a live order, read credentials, read account IDs, or create unattended trading automation.
