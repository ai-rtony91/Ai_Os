# AI_OS Cloudflare Access Dashboard Action Prep

Status: DRY_RUN DASHBOARD ACTION PREP READY FOR REVIEW
Packet: AIOS-CLOUDFLARE-ACCESS-DASHBOARD-ACTION-PREP-DRY-RUN-V1
Lane: cloudflare-access-dashboard-action-prep
Mode: DRY_RUN
Generated: 2026-06-12

## Executive Summary

This DRY_RUN prep checklist defines the future human-guided Cloudflare dashboard actions needed for AI_OS Cloudflare Access and post-Access Turnstile policy review. It does not configure Cloudflare, Turnstile, Azure, Entra, GitHub OAuth, Google OAuth, OTP, DNS, tunnels, dashboard exposure, secrets, credentials, runtime, scheduler, queues, broker paths, or live trading.

The future login order remains:

1. AI_OS URL.
2. Cloudflare Access identity login.
3. AI_OS post-login Turnstile check.
4. AI_OS dashboard/session.
5. Extra Turnstile only before third-party service handoff or login screens.

Cloudflare Access is the front-door identity gate. Turnstile is mandatory after successful Access identity login and before AI_OS app session creation, and mandatory before in-app third-party service handoff/login screens such as TradingView. Turnstile must not run before Cloudflare Access, on every dashboard page load, on every click, or during normal authenticated navigation.

## Current Identity Baseline

| Identity surface | Current value | Status | Rule |
|---|---|---|---|
| Azure CLI production account | `ai.tradeplatform@Algotradez.onmicrosoft.com` | CONFIRMED | Production AI_OS cloud account unless separately approved. |
| Azure tenant ID | `feb18abf-17ea-4d88-a4ac-05ffcd6ecb8b` | CONFIRMED_NON_SECRET_METADATA | May be recorded; not a secret. |
| Azure subscription name | `Subscription 1` | CONFIRMED | Non-secret metadata. |
| GitHub CLI identity | `ai-rtony91` | CONFIRMED | Repo/operator identity and Access backup candidate. |
| Git author | `ai-rtony91` | CONFIRMED | Repo commit identity. |
| Omen/Windows login | Anthony local workstation login | CONFIRMED_UNCHANGED | Local fallback; not end-user or provider authority. |
| Cloudflare account identity | Not confirmed in repo evidence | UNRESOLVED | Must be manually confirmed before dashboard action. |
| Break-glass/recovery details | Not confirmed in repo evidence | UNRESOLVED | Must be manually confirmed before exposure. |

## Dashboard Action Prep Scope

All steps below are preparation only. Every future dashboard action is `NOT AUTHORIZED YET`.

The future human-guided dashboard lane may ask Anthony to open Cloudflare and verify UI state manually, but this prep packet does not open Cloudflare, click Cloudflare controls, create provider records, configure Access, configure Turnstile, create DNS records, create tunnels, expose the dashboard, or handle secrets.

## Cloudflare Dashboard Account Identity Confirmation

Future manual confirmation required before any dashboard action:

1. `NOT AUTHORIZED YET`: Open the Cloudflare dashboard in the intended business/admin account.
2. `NOT AUTHORIZED YET`: Confirm Cloudflare account display name or account class.
3. `NOT AUTHORIZED YET`: Confirm whether the signed-in Cloudflare identity is Anthony-owned and admin-class.
4. `NOT AUTHORIZED YET`: Confirm at least two independent Cloudflare admin or recovery paths exist.
5. `NOT AUTHORIZED YET`: Confirm Cloudflare recovery does not depend only on the same Microsoft reset loop as the primary admin.
6. `NOT AUTHORIZED YET`: Capture only sanitized screenshot/manual confirmation if later approved.

Do not record passwords, recovery codes, session cookies, Cloudflare API tokens, Turnstile secret keys, OAuth client secrets, or `.env` values.

## Cloudflare Zero Trust And Access Navigation Path

Current Cloudflare documentation describes adding a self-hosted public application through Cloudflare One / Zero Trust under Access controls and Applications, then selecting an application type such as Self-hosted. In a future approved lane, use the visible Cloudflare dashboard labels as the source of truth. If labels differ, stop and record what is visible instead of guessing.

Future path sketch, all `NOT AUTHORIZED YET`:

1. Open Cloudflare dashboard.
2. Go to Cloudflare One / Zero Trust.
3. Locate Access controls.
4. Open Applications.
5. Start Add an application.
6. Select Self-hosted application for the future AI_OS protected web surface.
7. Stop before saving, creating, publishing, adding DNS, creating tunnels, or exposing AI_OS.

## Future Self-Hosted Application Object

The future Cloudflare Access object should be treated as a self-hosted application that will eventually protect AI_OS remote access. It is not created by this packet.

Planned object properties:

| Field | Prep value | Status |
|---|---|---|
| Application type | Self-hosted application | PLANNED_NOT_CREATED |
| Application purpose | Protect future AI_OS remote dashboard/app entry | PLANNED_NOT_CREATED |
| Application name | `AI_OS Access - Production` or Anthony-approved variant | UNRESOLVED_FINAL_NAME |
| Public hostname | Domain/subdomain target not selected | UNRESOLVED |
| Session duration | Not selected | UNRESOLVED |
| Identity providers | Microsoft/Entra primary, GitHub backup, Google optional, OTP emergency | PLANNED_ORDER_ONLY |
| Policies | Deny by default; separate admin and end-user policies | PLANNED_NOT_CREATED |

## Application Name Convention

Recommended naming convention for future review:

- `AI_OS Access - Production` for the protected production-facing AI_OS Access app.
- `AI_OS Access - Staging` only if a separate staging surface is approved.
- `AI_OS Access - Local Proof` only if a temporary proof object is separately approved and not exposed publicly.

Names are non-secret metadata. Final name remains unresolved until Anthony confirms the domain/subdomain and target environment.

## Domain And Subdomain Decision Fields

Unresolved fields that must be supplied before any future dashboard action:

| Field | Status | Rule |
|---|---|---|
| Cloudflare zone/domain | UNRESOLVED | Manual confirmation only; no DNS change yet. |
| AI_OS subdomain | UNRESOLVED | Must not be created or changed by this packet. |
| Public hostname | UNRESOLVED | Must not expose dashboard until Access policy is proven. |
| Local origin route | UNRESOLVED | No tunnel or origin routing in this packet. |
| Dashboard exposure target | BLOCKED | Exposure requires separate approval after Access proof. |

## Identity Provider Order

Future provider ordering:

1. Microsoft/Entra primary admin login.
2. GitHub backup operator login.
3. Google optional fallback only if it improves independent recovery.
4. Cloudflare OTP emergency fallback only, constrained to approved emergency mailbox class.

Provider setup is not authorized by this packet. Each provider must have separate Anthony approval, recovery review, no-secrets handling, and proof before use.

## Turnstile Placement

Turnstile placement for future implementation:

1. Cloudflare Access identity login must complete first.
2. AI_OS backend must require a post-login Turnstile check before AI_OS app session creation.
3. AI_OS backend must verify the Turnstile token server-side.
4. AI_OS must require an additional Turnstile check before third-party service handoff/login screens such as TradingView.

Turnstile must not run before Cloudflare Access identity login. It must not run globally on every dashboard page, every click, or normal authenticated navigation. It is not identity authority and does not replace Microsoft, GitHub, Google, OTP, Cloudflare Access, backend roles, or AI_OS approval gates.

## Non-Secret Metadata And Forbidden Values

Allowed non-secret metadata:

- Cloudflare account display/account class.
- Cloudflare zone/domain class.
- Access application name.
- policy names.
- provider names.
- tenant ID `feb18abf-17ea-4d88-a4ac-05ffcd6ecb8b`.
- sanitized proof that a checklist item passed or failed.

Forbidden values:

- passwords.
- personal access tokens.
- Cloudflare API tokens.
- Turnstile secret key.
- OAuth client secrets.
- refresh tokens.
- session cookies.
- MFA codes.
- recovery codes.
- broker credentials.
- `.env` values.
- third-party service credentials.

## Screenshot And Manual Confirmation Checklist

Future screenshots/manual confirmations must be sanitized and separately approved before capture or storage.

Required future confirmations:

1. Cloudflare account identity and account class.
2. Cloudflare admin/recovery path independence.
3. Selected Cloudflare zone/domain class.
4. Proposed Access application name.
5. Proposed public hostname, without creating DNS or tunnel records.
6. Microsoft/Entra primary provider plan.
7. GitHub backup provider plan.
8. Google fallback decision.
9. OTP emergency boundary.
10. Break-glass/recovery path.
11. No DNS/tunnel/dashboard exposure.
12. No secrets entered the repo.

## No-Lockout Controls

Before any future provider action:

1. Confirm at least two independent admin login paths.
2. Confirm break-glass account is independent from the primary Microsoft reset loop.
3. Confirm recovery email class is separate from the primary Microsoft account.
4. Confirm local Omen fallback still works.
5. Confirm Cloudflare admin recovery is not single-path.
6. Confirm GitHub backup is available or explicitly deferred with documented risk.
7. Confirm no DNS, tunnel, or dashboard exposure is included.
8. Confirm exact rollback path for the one dashboard action.

## Rollback Requirements

Before any future dashboard action:

1. Confirm clean repo.
2. Record a T9 savepoint if that lane requires one.
3. Capture sanitized current provider UI state only after approval.
4. Confirm primary and backup admin paths.
5. Define the exact rollback action before making the change.
6. Stop if any recovery path is unclear.

After any future dashboard action:

1. Test the changed login path.
2. Test one independent backup login path.
3. Confirm local Omen fallback still works.
4. Confirm dashboard remains unexposed unless separately approved.
5. Confirm no secrets entered the repo.
6. Confirm Git status is clean.
7. Stop and roll back only the last change if login proof fails.

## Future Proof Checklist

Before any remote dashboard exposure, a future APPLY lane must prove:

- Cloudflare Access identity login succeeds first.
- Microsoft/Entra primary admin can log in.
- GitHub backup can log in.
- break-glass path is tested without daily admin.
- AI_OS post-login Turnstile check runs after Access authentication and before app session creation.
- Turnstile does not run before Cloudflare Access.
- Turnstile does not run on every dashboard page, click, or normal authenticated navigation.
- Turnstile runs before third-party service handoff/login screens.
- dashboard is inaccessible without Cloudflare Access.
- local Omen fallback still works.
- no secrets were committed.
- AI_OS approval gates still control protected actions.

## Reference Docs Consulted

- Cloudflare self-hosted Access app docs: https://developers.cloudflare.com/cloudflare-one/access-controls/applications/http-apps/self-hosted-public-app/
- Cloudflare identity provider docs: https://developers.cloudflare.com/cloudflare-one/integrations/identity-providers/
- Cloudflare Turnstile server-side validation docs: https://developers.cloudflare.com/turnstile/get-started/server-side-validation/

## Exact Stop Point Before Provider Changes

Stop here. Do not configure Cloudflare, Turnstile, Azure, Entra, GitHub OAuth, Google OAuth, OTP, DNS, tunnels, dashboard exposure, provider dashboards, secrets, credentials, `.env`, runtime, scheduler, queues, approval inbox, worker inbox, command queue, broker paths, or live trading from this dashboard-action prep lane.
