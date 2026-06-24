# AIOS Forex OANDA Demo Vault Preflight Truth Runbook V1

## 1. Current Repo Truth

Observed on 2026-06-24 from `C:\Dev\Ai.Os`.

- Current local branch: `feature/forex-oanda-demo-read-only-preflight-from-vault-v1`
- Current local status before this runbook: clean, tracking `origin/feature/forex-oanda-demo-read-only-preflight-from-vault-v1`
- Remote: `origin https://github.com/ai-rtony91/Ai_Os.git`
- Latest local commit before this runbook: `dc1c29b4 feat(forex): add OANDA demo read-only preflight from vault`
- README and AGENTS still identify `main` as the active default branch, but this packet used `branch: resolve after preflight`; no branch switch was performed.
- GitHub PR #1070 is closed and merged into `main`.
- PR #1070 title: `feat(forex): add OANDA demo read-only preflight from vault`
- PR #1070 head: `feature/forex-oanda-demo-read-only-preflight-from-vault-v1` at `dc1c29b4f32e353075923c7069dee2c0c6a8e7f4`
- PR #1070 base: `main` at `ec590a353410cfde4e64b9675dc6b39e75705e79`
- PR #1070 merge commit: `e8da54dee8bf388ec5c007e22f845503aa022d95`
- PR #1070 merged at: `2026-06-24T18:40:34Z`

This runbook is local operator guidance and evidence synthesis only. It does not create trading doctrine, does not override `AGENTS.md`, `README.md`, `WHITEPAPER.md`, `RISK_POLICY.md`, or `docs/governance/source-of-truth-map.md`, and does not authorize commit, push, broker mutation, live trading, or order placement.

## 2. Existing Broker Evidence

The first OANDA demo runtime HTTP transport attempt reached the OANDA practice broker endpoint once and returned HTTP `403 forbidden`.

Existing evidence classification:

- `TRANSPORT_FAILED / BROKER_AUTH_OR_PERMISSION_REJECTED`
- Broker error message: `The provided request was forbidden.`
- Order attempt count: `1`
- Order placement performed: `false`
- `orderCreateTransaction` observed: `false`
- `orderFillTransaction` observed: `false`
- Stop loss and take profit were not attached because the broker rejected the request before placement.
- The one-order-attempt cap history is preserved. No second order attempt is allowed from this runbook.

The next landed correction path is read-only credential, account, and permission preflight. It uses OANDA practice account metadata GET endpoints only and is designed to diagnose token/account visibility and permission problems without placing another order.

## 3. Latest Merged Milestone

PR #1070 landed the vault-backed OANDA demo read-only preflight milestone.

The milestone created:

- `automation/forex_engine/oanda_demo_read_only_preflight_from_vault_v1.py`
- `scripts/forex_delivery/run_oanda_demo_read_only_preflight_from_vault_v1.py`
- `tests/forex_engine/test_oanda_demo_read_only_preflight_from_vault_v1.py`
- `Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_READ_ONLY_PREFLIGHT_FROM_VAULT_V1.md`
- `Reports/forex_delivery/AIOS_FOREX_120_PERCENT_PROFITABILITY_CAMPAIGN_ANCHOR_V1.md`

What this milestone can prove:

- whether the approved Windows vault labels can be loaded at owner runtime.
- whether the token-visible OANDA demo account can access OANDA practice account metadata through read-only GET endpoints.
- whether account visibility, account detail access, summary access, instruments access, and EUR/USD availability look permission-compatible.

What it cannot prove:

- order placement.
- live trading readiness.
- profitability.
- a +120% return.
- broker write authority.
- scheduler, daemon, webhook, or autonomous trading readiness.

## 4. Exact Owner Manual Commands

Run the template command first. It prints the expected vault labels, confirmations, allowed endpoints, and forbidden broker actions. It must not read credentials, read an account ID, or call OANDA.

```powershell
python scripts/forex_delivery/run_oanda_demo_read_only_preflight_from_vault_v1.py --print-template
```

Run the read-only preflight command only if the owner wants metadata-only OANDA practice verification from Windows vault values. This command should be run by the owner, not by Codex.

```powershell
python scripts/forex_delivery/run_oanda_demo_read_only_preflight_from_vault_v1.py --execute-read-only-preflight-from-vault --i-confirm-demo-only --i-confirm-read-only-preflight --i-confirm-windows-vault-only --i-confirm-no-env-file --i-confirm-no-repo-persistence --i-confirm-no-live-credentials --i-confirm-token-visible-account --i-confirm-no-order-endpoint --i-confirm-no-trade-mutation --i-confirm-no-second-order-attempt
```

Do not place an access token or account ID in the command. Do not paste credentials into Codex, ChatGPT, Claude, GitHub, a report, `.env`, or a repo file.

## 5. Windows Vault Labels Expected

The landed code expects exactly these Windows vault credential names:

```text
AIOS_OANDA_DEMO_ACCESS_TOKEN
AIOS_OANDA_DEMO_ACCOUNT_ID
```

Only the labels belong in repo documentation. The values are runtime-only and must stay out of the repository, prompts, reports, logs, screenshots, and terminal command text.

## 6. Allowed Read-Only OANDA Practice Endpoints

The vault-backed preflight permits only OANDA practice GET metadata endpoints:

```text
GET https://api-fxpractice.oanda.com/v3/accounts
GET https://api-fxpractice.oanda.com/v3/accounts/<runtime_account_id>
GET https://api-fxpractice.oanda.com/v3/accounts/<runtime_account_id>/summary
GET https://api-fxpractice.oanda.com/v3/accounts/<runtime_account_id>/instruments
```

The account identifier is a runtime-only value. The endpoint templates above are not permission to store or print the real account ID.

## 7. Forbidden Broker Endpoints

Forbidden endpoint classes:

- `/orders`
- `/trades`
- `/positions`
- `/transactions`
- `api-fxtrade.oanda.com`
- any non-practice OANDA base URL
- any broker mutation endpoint
- any POST, PUT, PATCH, or DELETE broker request

Forbidden actions:

- demo order placement from this runbook.
- live order placement.
- order retry.
- position mutation.
- trade mutation.
- scheduler, daemon, webhook, or unattended trading path.
- credential or account ID persistence in the repo.

## 8. Expected Evidence Outcomes

The template command should return:

- `script_status`: `VAULT_PREFLIGHT_TEMPLATE_ONLY`
- `broker_network_call_performed`: `false`
- `credential_read_performed`: `false`
- `account_id_read_performed`: `false`
- `order_placement_performed`: `false`
- `dotenv_read`: `false`

The read-only execute command may return one of these outcome classes:

- `VAULT_PREFLIGHT_READ_ONLY_ATTEMPTED`: the vault-backed read-only preflight attempted the approved GET metadata path. This is not automatically a trading PASS; inspect the nested root-cause summary.
- `BLOCKED_MISSING_REQUIRED_CONFIRMATIONS`: required owner confirmations were omitted; no vault or broker call should occur.
- `VAULT_PREFLIGHT_BLOCKED_MISSING_TOKEN`: the approved access-token vault label was missing or unreadable.
- `VAULT_PREFLIGHT_BLOCKED_MISSING_ACCOUNT_ID`: the approved account-ID vault label was missing or unreadable.
- `VAULT_PREFLIGHT_BLOCKED_MISSING_VAULT_ADAPTER`: no approved vault loader was available.
- `VAULT_PREFLIGHT_BLOCKED_LIVE_MODE`: the context tried to move out of demo/practice mode.
- `VAULT_PREFLIGHT_BLOCKED_UNSAFE_ENDPOINT`: a live, mutation, or unsupported endpoint path was detected.

If read-only endpoint responses include HTTP `401`, `403`, or `404`, the preflight result can still be useful diagnostic evidence. Do not treat command completion alone as a PASS.

## 9. PASS Interpretation

Treat the vault preflight as a practical PASS only when the redacted output shows all of the following:

- `script_status` is `VAULT_PREFLIGHT_READ_ONLY_ATTEMPTED`.
- `order_placement_performed` is `false`.
- `orders_endpoint_called` is `false`.
- `credential_value_printed` is `false`.
- `account_id_value_printed` is `false`.
- `dotenv_read` is `false`.
- the nested root-cause summary reports token validity, token-visible account access, account details access, account summary access, instruments access, EUR/USD availability, and practice-account confirmation as favorable.
- `trading_permission_likely` is `true`.

A PASS means the vault-backed read-only OANDA practice metadata path appears healthy. It does not mean AIOS may place an order. It only means the next Codex packet can capture sanitized owner evidence and prepare a separately approved governed demo-trade readiness lane.

## 10. 403/BLOCKED Interpretation

Treat the outcome as `403/BLOCKED` when any of these are true:

- the command returns `BLOCKED_MISSING_REQUIRED_CONFIRMATIONS`.
- the command returns any `VAULT_PREFLIGHT_BLOCKED_*` status.
- the nested read-only preflight result shows HTTP `401`, `403`, or `404` on required metadata endpoints.
- `token_valid` is `false`.
- `account_visible_to_token` is `false`.
- account details, summary, instruments, or EUR/USD access is false or unknown.
- `trading_permission_likely` is not `true`.
- `likely_403_root_cause` reports token expiration, token/account mismatch, account permission restriction, account not visible to token, order permission restriction, or unknown owner broker review.

Interpretation guide:

- `token_invalid_or_expired`: owner should review the OANDA demo access token in the broker portal and Windows vault.
- `token_account_mismatch`: owner should confirm the vault account ID belongs to the same token-visible OANDA practice account.
- `account_permission_restricted`: owner should review account access or broker-side permission state.
- `account_not_visible_to_token`: owner should confirm the account is visible to the token before any new packet.
- `order_permission_restricted`: read-only metadata works, but the previous order 403 may still be order-permission specific. This still does not authorize an order retry.
- `unknown_requires_owner_broker_review`: stop and capture sanitized evidence before changing credentials or retrying anything.

## 11. Next Safe Packet If PASS

Packet brief only. This is not an executable Codex prompt.

Recommended next packet ID:

```text
AIOS-FOREX-OANDA-DEMO-VAULT-PREFLIGHT-PASS-EVIDENCE-CAPTURE-V1
```

Recommended mode:

```text
APPLY
```

Recommended mission:

Create one sanitized owner-result evidence report from the vault-backed read-only preflight output. The packet should record the PASS interpretation, confirm no order endpoint was called, confirm no credential or account ID value was captured, and propose the next separately approved governed demo-trade readiness packet. It must not run OANDA, read credentials, read account IDs, place orders, stage, commit, or push.

Recommended allowed path:

```text
Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_VAULT_PREFLIGHT_PASS_EVIDENCE_CAPTURE_V1.md
```

Recommended validator chain:

```text
git diff --check
git status --short --branch
```

Stop after creating the one sanitized evidence report. Do not place a demo order.

## 12. Next Safe Packet If 403/BLOCKED

Packet brief only. This is not an executable Codex prompt.

Recommended next packet ID:

```text
AIOS-FOREX-OANDA-DEMO-VAULT-PREFLIGHT_403_BLOCKED_EVIDENCE_CAPTURE_V1
```

Recommended mode:

```text
APPLY
```

Recommended mission:

Create one sanitized 403/BLOCKED evidence report from the owner-run preflight output. The packet should classify the root cause from redacted fields, preserve runtime-only credential doctrine, preserve the no-second-order-attempt boundary, and recommend owner-side broker/account correction steps without retrying an order or reading secrets.

Recommended allowed path:

```text
Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_VAULT_PREFLIGHT_403_BLOCKED_EVIDENCE_CAPTURE_V1.md
```

Recommended validator chain:

```text
git diff --check
git status --short --branch
```

Stop after creating the one sanitized evidence report. Do not call OANDA from Codex and do not retry an order.

## 13. What AIOS Still Cannot Claim

AIOS still cannot claim:

- that the +120% campaign target is guaranteed or achievable.
- that AIOS is profitable.
- that one trade can or must reach the campaign target.
- that compounding or withdrawal is automatic.
- that live trading is authorized.
- that broker writes are authorized.
- that a second order attempt is authorized.
- that OANDA account permissions are fixed until the owner-run read-only preflight evidence proves it.
- that an order can be placed until a separate packet, separate approval, and separate safety gate authorize the exact action.

The +120% item remains a campaign target only. It is not a performance claim.

## 14. Tonight Finish-Line Checklist

1. Stay in `C:\Dev\Ai.Os`.
2. Do not paste tokens or account IDs into any AI chat, repo file, report, shell command, or screenshot.
3. Run the template command.
4. Confirm the template names only these vault labels: `AIOS_OANDA_DEMO_ACCESS_TOKEN` and `AIOS_OANDA_DEMO_ACCOUNT_ID`.
5. Confirm the template allows only OANDA practice GET metadata endpoints.
6. Confirm the template forbids orders, trades, positions, transactions, live endpoints, and broker writes.
7. If the owner wants the read-only broker metadata check, run the execute command manually.
8. Inspect the redacted JSON result.
9. If PASS, create the PASS evidence-capture Codex packet briefed above.
10. If `403/BLOCKED`, create the 403/BLOCKED evidence-capture Codex packet briefed above.
11. Stop before any demo order retry, live order, credential persistence change, scheduler, daemon, webhook, commit, or push.
