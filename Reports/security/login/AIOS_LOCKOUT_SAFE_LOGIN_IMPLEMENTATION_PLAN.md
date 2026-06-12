# AI_OS Lockout-Safe Login Implementation Plan

Status: DRY_RUN IMPLEMENTATION PLAN READY FOR REVIEW
Packet: AIOS-CLOUDFLARE-ACCESS-LOCKOUT-SAFE-LOGIN-IMPLEMENTATION-PLAN-DRY-RUN-V1
Lane: login-security-implementation-plan
Mode: DRY_RUN
Generated: 2026-06-11

## Executive Summary

This plan defines the future implementation sequence for the AI_OS lockout-safe login and security stack. It covers Cloudflare Access, Turnstile, Microsoft/Entra primary admin login, GitHub backup login, optional Google fallback, Cloudflare OTP emergency fallback, break-glass recovery, local Omen fallback, end-user roles, rollback, lockout drills, and proof requirements.

This packet made no provider changes. It does not configure Cloudflare, Azure, Entra, GitHub OAuth, Google OAuth, DNS, tunnels, Turnstile, OTP, dashboard exposure, secrets, credentials, runtime, scheduler, queues, broker paths, or live trading.

The safest path is staged: confirm identities and recovery first, design Cloudflare Access policy second, configure primary and backup admin paths only after explicit provider-setup approval, prove login and recovery paths before any dashboard exposure, and keep AI_OS protected actions behind internal approval gates even after login works.

## Current Identity Baseline

| Identity surface | Current value | Status | Rule |
|---|---|---|---|
| Windows/Omen login | Anthony local workstation login | CONFIRMED_UNCHANGED | Remains local fallback; not an end-user or provider-admin substitute. |
| Azure CLI production account | `ai.tradeplatform@Algotradez.onmicrosoft.com` | CONFIRMED | Use for production AI_OS cloud resources unless Anthony approves another identity. |
| Azure tenant ID | `feb18abf-17ea-4d88-a4ac-05ffcd6ecb8b` | CONFIRMED_NON_SECRET_METADATA | May be recorded; not a secret. |
| Azure subscription name | `Subscription 1` | CONFIRMED | Non-secret metadata. |
| Azure subscription state | `Enabled` | CONFIRMED | Non-secret metadata. |
| Prior Azure CLI account | `my.laboratory@outlook.com` | DO_NOT_USE_BY_DEFAULT | Do not use for production AI_OS cloud resources without separate approval. |
| GitHub CLI identity | `ai-rtony91` | CONFIRMED | Repo/operator identity and backup login candidate. |
| Git author | `ai-rtony91` | CONFIRMED | Repo commit identity. |
| Git email | `270783377+ai-rtony91@users.noreply.github.com` | CONFIRMED | Repo commit email. |
| Azure Portal browser identity | Not yet manually confirmed | UNRESOLVED | Must use AI TRADEZ in a dedicated browser profile before provider work. |
| Cloudflare admin identity | Not yet manually confirmed | UNRESOLVED | Must be business/admin class and independently recoverable. |
| Recovery email class | Not yet manually confirmed | UNRESOLVED | Must be separate from primary Microsoft reset loop. |
| Break-glass account | Required, details not confirmed | UNRESOLVED | Must not depend on same Microsoft reset loop. |
| Optional Google fallback | Not decided | UNRESOLVED | Use only if it reduces lockout risk without account sprawl. |

## Implementation Phases

| Phase | Name | Future action | Required gate | Stop point |
|---|---|---|---|---|
| 0 | Repo, T9, and identity baseline | Confirm clean repo, create T9 savepoint, reread identity inventory, verify no unresolved local work. | Clean Git status, current `origin/main`, T9 savepoint approval. | Stop before provider dashboards. |
| 1 | Cloudflare account/admin identity confirmation | Manually confirm Cloudflare admin account class, owner, recovery paths, and second admin path. | Anthony manual confirmation; no API tokens. | Stop before changing Cloudflare. |
| 2 | Cloudflare Access application design | Define app name, protected hostname, policies, admin group, end-user group, session duration, and deny-by-default behavior. | Review-only policy design approval. | Stop before creating Access app. |
| 3 | Microsoft/Entra primary provider setup plan | Plan Microsoft/Entra as primary admin login provider for Cloudflare Access. | Confirm Azure Portal uses AI TRADEZ in dedicated browser profile; confirm recovery separation. | Stop before Entra/Cloudflare provider setup. |
| 4 | GitHub backup provider setup plan | Plan GitHub login as backup operator path for Cloudflare Access. | Confirm `ai-rtony91` account health and recovery path. | Stop before GitHub OAuth/provider setup. |
| 5 | Google optional fallback decision | Decide whether Google improves recovery or creates unnecessary account sprawl. | Anthony decision based on independent recovery and MFA. | Stop before Google OAuth/provider setup. |
| 6 | Cloudflare OTP emergency fallback constraints | Define allowed OTP addresses, emergency-only use, audit cadence, and reset-loop checks. | Confirm OTP mailbox is independently recoverable. | Stop before enabling OTP. |
| 7 | Break-glass account and recovery procedure | Define owner, account class, MFA/recovery separation, storage-free recovery process, and drill cadence. | Anthony manual confirmation. | Stop before relying on break-glass for exposure. |
| 8 | Turnstile site and secret handling plan | Define future site key use, server-side secret handling, and backend verification path. | Secret handling plan approved; no secret in repo or browser. | Stop before Turnstile creation or secret handling. |
| 9 | Local dashboard exposure boundary | Define local-only dashboard state and remote exposure prerequisites. | Cloudflare Access proof plan approved. | Stop before DNS, tunnel, or dashboard exposure. |
| 10 | Dry proof before remote exposure | Prove Access login paths, denial behavior, no-secret status, and local Omen fallback without exposing dashboard. | Proof checklist complete. | Stop before remote exposure. |
| 11 | Staged implementation packet | Generate exact APPLY packets for one provider change at a time. | Separate Anthony approval for each provider action. | Stop after each packet and validation. |
| 12 | Rollback and lockout drill | Run safe lockout drill, verify rollback path, and record proof. | Anthony approval and no-secrets evidence. | Stop after clean Git status and T9 savepoint. |

## Account Separation Map

| Account class | Required owner/use | Separation rule |
|---|---|---|
| Windows/Omen login | Anthony local workstation access | Keep local and personal unless separately approved; never use as end-user identity. |
| Azure CLI | AI TRADEZ production cloud account | Keep `ai.tradeplatform@Algotradez.onmicrosoft.com`; do not fall back to `my.laboratory@outlook.com` without approval. |
| Azure Portal browser | AI TRADEZ dedicated browser profile | Do not mix personal Outlook and production portal sessions. |
| GitHub | `ai-rtony91` repo/operator identity | Repo identity and backup Access provider candidate; not an app role bypass. |
| Cloudflare admin | Business/admin class identity | Must have independent recovery and at least two admin access paths. |
| AI_OS owner/admin | AI_OS backend role | App authority only after backend role check; not provider authority. |
| AI_OS operator | AI_OS backend role | Operational app use only; protected actions still need gates. |
| AI_OS viewer/client/end-user | End-user owned identity | Cannot access repo, scheduler, runtime, queues, broker, secrets, or provider admin. |
| Emergency read-only | Restricted emergency role | Visibility only during recovery; no mutation authority. |
| Break-glass | Anthony-controlled emergency identity | Not daily admin; not automation; not dependent on same Microsoft reset loop. |

## Cloudflare Access Setup Plan

Cloudflare Access should become the front-door identity gate before any AI_OS dashboard is reachable from outside the local machine.

Future setup order:

1. Confirm Cloudflare admin account and recovery.
2. Define Access application and protected hostname in review-only mode.
3. Define deny-by-default policy.
4. Add Microsoft/Entra primary admin provider only after recovery checks pass.
5. Add GitHub backup provider only after GitHub account health is confirmed.
6. Decide whether Google fallback and OTP are needed.
7. Prove Access blocks unauthenticated access before any dashboard exposure.

Cloudflare Access must not replace AI_OS backend role checks or protected-action approval gates.

## Microsoft/Entra Primary Login Plan

Microsoft/Entra should be the primary admin login path only after:

- Azure Portal browser identity is confirmed as AI TRADEZ in a dedicated browser profile.
- recovery email class is separate from the primary Microsoft reset loop.
- break-glass account is defined.
- Cloudflare admin access has at least two recovery paths.
- no secrets are copied into the repo.

Future proof must show the Microsoft primary admin can log in through Cloudflare Access without using the break-glass account.

## GitHub Backup Login Plan

GitHub should be the backup operator login path for Cloudflare Access. The known repo/operator identity is `ai-rtony91`.

Future setup requirements:

- confirm GitHub account recovery and MFA are healthy.
- confirm GitHub login works independently from Microsoft.
- keep GitHub repo permissions separate from AI_OS app role authority.
- keep commits, pushes, merges, and PR actions under AI_OS protected-action gates.

GitHub backup login must not become a shortcut around AI_OS approvals.

## Google Fallback Decision Point

Google remains optional. It should be added only if it improves lockout resilience with a clearly owned, independently recoverable account.

Decision rule:

- Choose Google fallback if it gives a genuinely independent recovery path.
- Defer Google if Microsoft, GitHub, OTP, and break-glass provide enough resilience.
- Reject Google if it adds unmanaged account sprawl or weak recovery.

## Cloudflare OTP Emergency Fallback Plan

Cloudflare OTP should be constrained to emergency use. It should not be the daily admin login.

Constraints:

- allow only approved emergency email classes.
- do not use a mailbox trapped in the same Microsoft reset loop.
- document owner and recovery path.
- test without exposing secrets.
- review periodically.
- disable or adjust if it creates a weaker bypass than Microsoft/GitHub.

## Break-Glass Account Plan

The break-glass account is a recovery control, not a daily login.

Required properties:

- Anthony-controlled.
- independent of the primary Microsoft reset loop.
- recovery email class separate from primary Microsoft account.
- MFA/recovery path available if Microsoft primary fails.
- not used by end users, automation, or routine provider work.
- no password, token, recovery code, or secret stored in repo.
- tested with a controlled lockout drill before dashboard exposure.

## Turnstile Integration Plan

Turnstile is a bot/human check, not identity authority.

Future integration rules:

- Browser may receive a public site key only.
- Turnstile secret key must live outside the repo.
- Backend must verify Turnstile token server-side.
- Passing Turnstile does not grant user role, admin role, provider authority, or protected-action authority.
- Turnstile proof must be backend-only before any sensitive form depends on it.

## Frontend Compromise Assumptions

The frontend is untrusted. Browser code can be inspected, modified, replayed, or bypassed.

Required controls:

- no secrets in browser.
- no secrets in repo.
- backend verifies Cloudflare Access/session claims.
- backend maps identity to AI_OS app role.
- backend verifies Turnstile server-side in future implementation.
- protected actions still route through AI_OS approval gates.

## No-Secrets Handling

Never commit or report:

- passwords.
- personal access tokens.
- OAuth client secrets.
- refresh tokens.
- session cookies.
- MFA codes.
- recovery codes.
- Cloudflare API tokens.
- Turnstile secret keys.
- broker credentials.
- `.env` values.

Tenant ID `feb18abf-17ea-4d88-a4ac-05ffcd6ecb8b` is non-secret metadata and may appear in reports.

## Local Omen Fallback

Omen/Windows login remains unchanged and is the local fallback for repo inspection, local dashboard access, and operator recovery. Cloudflare Access, Azure, GitHub, Google, OTP, and Turnstile work must not alter Omen login.

Local dashboard remains local-only until Cloudflare Access policy is proven and a separate exposure packet is approved.

## End-User Login Model

End users authenticate with their own provider identities. AI_OS maps identity to app roles.

App roles:

- `owner_admin`: full app administration after backend role check; protected actions still require AI_OS gates.
- `operator`: approved operational use without provider, repo, scheduler, broker, or secret authority.
- `viewer`: read-only app visibility.
- `client_end_user`: scoped end-user access to assigned app functions only.
- `emergency_read_only`: restricted recovery visibility without mutation authority.

No end user can touch scheduler, runtime, queues, broker, live trading, secrets, repo authority, provider admin, or approval gates unless Anthony separately approves a future packet.

## Rollback Plan

Before each future provider APPLY step:

1. Confirm clean repo and record T9 savepoint.
2. Record current provider state using screenshots/manual confirmation only, with no secrets.
3. Confirm at least two admin access paths exist.
4. Define a backout path for the exact provider change.
5. Stop if primary and backup logins are not both available.

After each provider APPLY step:

1. Test the changed login path.
2. Test at least one independent backup login path.
3. Verify local Omen fallback still works.
4. Verify no secrets were committed.
5. Verify Git status is clean after merge.
6. Create T9 savepoint after major merge.

If any login path fails, stop and use the last known admin path to revert only the last provider change. Do not make additional provider changes while locked out or partially locked out.

## Lockout Drill

Lockout drill objective: prove recovery without using the daily admin path as the only route.

Drill steps:

1. Confirm Microsoft primary login works.
2. Confirm GitHub backup login works independently.
3. Confirm break-glass path works without daily admin.
4. Confirm OTP fallback only works for approved emergency address class if enabled.
5. Confirm dashboard is inaccessible without Cloudflare Access.
6. Confirm local Omen fallback still reaches local AI_OS.
7. Confirm AI_OS protected actions still require approval gates after login.
8. Confirm no secrets are committed.
9. Stop and record proof before any remote dashboard exposure.

## Proof Checklist

Required proof before remote exposure:

- Cloudflare Access test user can log in.
- Microsoft primary admin can log in.
- GitHub backup can log in.
- break-glass path is tested without using daily admin.
- Turnstile token validation is proven in backend only.
- dashboard is inaccessible without Cloudflare Access.
- local Omen fallback still works.
- no secrets committed.
- `git status --short --branch` clean after each step.
- T9 savepoint after each major merge.
- AI_OS approval gates still control protected actions.

## Exact Stop Point Before Provider Changes

Stop here. Do not configure Cloudflare, Azure, Entra, GitHub OAuth, Google OAuth, OTP, Turnstile, DNS, tunnels, dashboard exposure, provider dashboards, secrets, credentials, `.env`, runtime, scheduler, queues, approval inbox, worker inbox, command queue, broker paths, or live trading from this implementation-plan lane.

