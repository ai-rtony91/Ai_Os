# AI_OS Cloudflare Access Provider Setup Review

Status: DRY_RUN PROVIDER SETUP REVIEW READY
Packet: AIOS-CLOUDFLARE-ACCESS-PROVIDER-SETUP-REVIEW-DRY-RUN-V1
Lane: cloudflare-access-provider-setup-review
Mode: DRY_RUN
Generated: 2026-06-11

## Executive Summary

This review prepares the Cloudflare Access provider setup checklist for the AI_OS lockout-safe login stack. It defines the provider-dashboard steps that will be needed later, but every provider action is marked `NOT AUTHORIZED YET`.

No Cloudflare, Azure, Entra, GitHub OAuth, Google OAuth, DNS, tunnel, Turnstile, OTP, dashboard, secret, credential, runtime, scheduler, queue, broker, or live-trading configuration was changed.

Cloudflare Access remains the planned front-door identity gate. Turnstile remains a later anti-bot layer, not identity authority. Microsoft/Entra remains the primary admin provider candidate, GitHub remains the backup operator login candidate, Google remains optional, OTP remains emergency-only, and break-glass recovery must be proven before any exposure.

## Current Identity Baseline

| Identity surface | Current value | Status | Rule |
|---|---|---|---|
| Azure CLI production account | `ai.tradeplatform@Algotradez.onmicrosoft.com` | CONFIRMED | Use for production AI_OS cloud resources unless separately approved. |
| Azure tenant ID | `feb18abf-17ea-4d88-a4ac-05ffcd6ecb8b` | CONFIRMED_NON_SECRET_METADATA | Tenant ID is not a secret. |
| Azure subscription name | `Subscription 1` | CONFIRMED | Non-secret metadata. |
| Azure subscription state | `Enabled` | CONFIRMED | Non-secret metadata. |
| GitHub CLI identity | `ai-rtony91` | CONFIRMED | Repo/operator identity and backup login candidate. |
| Git author | `ai-rtony91` | CONFIRMED | Repo commit identity. |
| Git email | `270783377+ai-rtony91@users.noreply.github.com` | CONFIRMED | Repo commit email. |
| Omen/Windows login | Anthony local workstation login | CONFIRMED_UNCHANGED | Local fallback; not end-user or provider authority. |
| Cloudflare account identity | Not confirmed in repo evidence | UNRESOLVED | Must be manually confirmed before provider work. |
| Google fallback identity | Not confirmed in repo evidence | UNRESOLVED | Optional; decide later. |
| Break-glass/recovery details | Not confirmed in repo evidence | UNRESOLVED | Required before exposure. |

## Unresolved Identity Inputs

| Input | Why it matters | Safe collection method |
|---|---|---|
| Cloudflare admin account identity | Required before any Access policy or provider dashboard change. | Manual confirmation or sanitized screenshot only; no API tokens, cookies, passwords, or recovery codes. |
| Cloudflare second admin path | Prevents Cloudflare-side lockout. | Manual confirmation of independent admin/recovery path. |
| Azure Portal browser identity | Must match intended AI TRADEZ production admin profile. | Manual confirmation in dedicated browser profile; no browser scraping. |
| Recovery email class | Must be separate from primary Microsoft reset loop. | Manual classification only; no password or mailbox contents. |
| Break-glass account details | Required for emergency recovery. | Manual confirmation of owner, account class, MFA, and recovery independence. |
| Optional Google fallback identity | Needed only if Google reduces lockout risk. | Manual decision and account-class confirmation. |
| OTP emergency mailbox class | Must not depend on same Microsoft reset loop. | Manual confirmation only. |

## Cloudflare Access Provider Setup Checklist

All Cloudflare dashboard actions below are `NOT AUTHORIZED YET`.

Future dashboard steps needed later:

1. `NOT AUTHORIZED YET`: Open Cloudflare dashboard in the intended admin account.
2. `NOT AUTHORIZED YET`: Confirm account name, account owner/admin class, and recovery path by sanitized screenshot or manual statement.
3. `NOT AUTHORIZED YET`: Confirm at least two independent Cloudflare admin access paths.
4. `NOT AUTHORIZED YET`: Locate Zero Trust / Access application setup area.
5. `NOT AUTHORIZED YET`: Draft the Access application name and protected hostname.
6. `NOT AUTHORIZED YET`: Draft deny-by-default policy.
7. `NOT AUTHORIZED YET`: Draft admin policy using Microsoft/Entra primary and GitHub backup.
8. `NOT AUTHORIZED YET`: Draft end-user policy separately from admin policy.
9. `NOT AUTHORIZED YET`: Confirm no DNS, tunnel, or dashboard exposure occurs during provider setup.
10. `NOT AUTHORIZED YET`: Record sanitized proof only after Anthony approves a future provider-dashboard lane.

Required before any future Cloudflare action:

- Separate Anthony approval for the exact dashboard action.
- Clean repo and current branch state.
- T9 savepoint before provider mutation.
- No secrets in repo.
- No API token handling.
- No DNS, tunnel, or dashboard exposure.

## Microsoft/Entra Provider Setup Checklist

All Microsoft/Entra provider actions below are `NOT AUTHORIZED YET`.

Future steps needed later:

1. `NOT AUTHORIZED YET`: Confirm Azure Portal browser session uses AI TRADEZ in a dedicated browser profile.
2. `NOT AUTHORIZED YET`: Confirm tenant `feb18abf-17ea-4d88-a4ac-05ffcd6ecb8b` is selected.
3. `NOT AUTHORIZED YET`: Confirm recovery email class is independent from the primary Microsoft reset loop.
4. `NOT AUTHORIZED YET`: Confirm break-glass account exists before relying on Microsoft primary.
5. `NOT AUTHORIZED YET`: Draft Microsoft/Entra provider settings for Cloudflare Access.
6. `NOT AUTHORIZED YET`: Record sanitized UI confirmation only after approval.

Microsoft/Entra must be primary admin login, not end-user action authority and not a replacement for AI_OS approval gates.

## GitHub Provider Setup Checklist

All GitHub provider actions below are `NOT AUTHORIZED YET`.

Future steps needed later:

1. `NOT AUTHORIZED YET`: Confirm `ai-rtony91` account health and recovery path.
2. `NOT AUTHORIZED YET`: Confirm GitHub login is independent from Microsoft recovery.
3. `NOT AUTHORIZED YET`: Draft GitHub backup provider settings for Cloudflare Access.
4. `NOT AUTHORIZED YET`: Confirm repo permissions remain separate from AI_OS app roles.
5. `NOT AUTHORIZED YET`: Confirm GitHub login does not bypass commit, push, merge, or PR gates.

GitHub is backup login only. It does not approve protected AI_OS actions.

## Google Optional Provider Setup Checklist

All Google provider actions below are `NOT AUTHORIZED YET`.

Future decision steps:

1. `NOT AUTHORIZED YET`: Decide whether Google adds independent recovery value.
2. `NOT AUTHORIZED YET`: Confirm Google account class and owner if used.
3. `NOT AUTHORIZED YET`: Confirm Google recovery is independent from Microsoft and GitHub.
4. `NOT AUTHORIZED YET`: Reject Google fallback if it creates account sprawl or weak recovery.
5. `NOT AUTHORIZED YET`: Draft provider settings only after Anthony approves Google fallback.

## OTP Emergency Fallback Checklist

All OTP actions below are `NOT AUTHORIZED YET`.

Future steps:

1. `NOT AUTHORIZED YET`: Identify emergency email class.
2. `NOT AUTHORIZED YET`: Confirm OTP email does not depend on the same Microsoft reset loop.
3. `NOT AUTHORIZED YET`: Constrain OTP to emergency use only.
4. `NOT AUTHORIZED YET`: Define audit/review cadence.
5. `NOT AUTHORIZED YET`: Test only after Microsoft, GitHub, and break-glass recovery are reviewed.

OTP must not become the daily login or a weaker bypass.

## Turnstile Later-Phase Checklist

All Turnstile actions below are `NOT AUTHORIZED YET`.

Future steps:

1. `NOT AUTHORIZED YET`: Decide which AI_OS forms need bot/human checks.
2. `NOT AUTHORIZED YET`: Plan site key placement as public browser configuration only.
3. `NOT AUTHORIZED YET`: Plan secret key storage outside the repo.
4. `NOT AUTHORIZED YET`: Plan backend server-side token verification.
5. `NOT AUTHORIZED YET`: Prove Turnstile token verification in backend only.

Turnstile is anti-bot protection. It is not identity authority, app role authority, or protected-action approval.

## Break-Glass Checklist

Break-glass is required before exposure. All account/provider actions are `NOT AUTHORIZED YET`.

Future checks:

1. Confirm owner is Anthony.
2. Confirm account class and recovery path.
3. Confirm independence from primary Microsoft reset loop.
4. Confirm MFA/recovery path works without daily admin.
5. Confirm account is not used by automation or end users.
6. Confirm no password, recovery code, token, or secret is stored in repo.
7. Run a controlled lockout drill before remote exposure.

## Local Omen Fallback Checklist

Omen/Windows login remains unchanged.

Future checks:

1. Confirm local Omen login still works before provider setup.
2. Confirm local repo access still works after provider setup.
3. Confirm local dashboard remains accessible locally.
4. Confirm Cloudflare Access work does not alter local login.
5. Stop if local fallback is impaired.

## No-Secrets Checklist

Never commit or report:

- passwords.
- personal access tokens.
- OAuth client secrets.
- refresh tokens.
- session cookies.
- MFA codes.
- recovery codes.
- Cloudflare API tokens.
- Turnstile secret key.
- broker credentials.
- `.env` values.

Allowed non-secret metadata:

- tenant ID.
- account display/email class.
- provider names.
- policy names.
- sanitized UI state.
- proof that a gate passed or failed.

## No-Lockout Checklist

Before any provider action:

1. Confirm at least two independent admin login paths.
2. Confirm break-glass account is independent from the Microsoft reset loop.
3. Confirm recovery email class is separate from primary Microsoft account.
4. Confirm local Omen fallback works.
5. Confirm GitHub backup is available or explicitly deferred with documented risk.
6. Confirm Cloudflare admin recovery is not single-path.
7. Confirm rollback path for the exact provider action.
8. Confirm no DNS, tunnel, or dashboard exposure is included.

## Proof Checklist

Future proof required before remote exposure:

- Cloudflare Access test user can log in.
- Microsoft primary admin can log in.
- GitHub backup can log in.
- break-glass path is tested without daily admin.
- optional Google fallback decision is recorded.
- OTP emergency fallback is constrained or explicitly deferred.
- Turnstile token validation is proven in backend only.
- dashboard is inaccessible without Cloudflare Access.
- local Omen fallback still works.
- no secrets committed.
- `git status --short --branch` is clean after each step.
- T9 savepoint exists after each major merge.
- AI_OS approval gates still control protected actions.

## Rollback Checklist

Before each future provider action:

1. Confirm clean repo.
2. Record T9 savepoint.
3. Capture sanitized current provider UI state.
4. Confirm primary and backup admin paths.
5. Define exact rollback action.
6. Stop if any recovery path is unclear.

After each future provider action:

1. Test changed login path.
2. Test independent backup login path.
3. Test local Omen fallback.
4. Confirm dashboard remains unexposed unless explicitly approved later.
5. Confirm no secrets entered the repo.
6. Confirm Git status is clean.
7. Stop and revert only the last provider change if login proof fails.

## Exact Stop Point Before Provider Changes

Stop here. Do not configure Cloudflare, Azure, Entra, GitHub OAuth, Google OAuth, OTP, Turnstile, DNS, tunnels, dashboard exposure, provider dashboards, secrets, credentials, `.env`, runtime, scheduler, queues, approval inbox, worker inbox, command queue, broker paths, or live trading from this review lane.

