# AI_OS Lockout-Safe Login Stack Design

Status: DRY_RUN DESIGN READY FOR REVIEW
Packet: AIOS-CLOUDFLARE-ACCESS-LOCKOUT-SAFE-LOGIN-DESIGN-DRY-RUN-V1
Lane: login-security-stack-design
Mode: DRY_RUN
Generated: 2026-06-11

## Executive Summary

This design defines a lockout-safe AI_OS login and security stack before any provider configuration occurs. The recommended stack is Cloudflare Access as the front-door identity gate, Microsoft/Entra as the primary admin login, GitHub as a backup operator login, optional Google fallback, constrained Cloudflare OTP emergency fallback, Turnstile for bot/human checks on AI_OS login or sensitive forms, AI_OS backend roles for app authorization, and AI_OS internal approval gates for protected actions.

The design preserves local Omen access and separates login identity from action authority. End users must use their own identities and must not touch Anthony's Azure, Omen, GitHub admin, repo, scheduler, runtime, broker, or secret-bearing identities. No Cloudflare, Azure, Entra, GitHub OAuth, Google OAuth, DNS, tunnel, dashboard exposure, credential, runtime, scheduler, queue, broker, or live-trading configuration is approved by this design.

## Identity Separation Table

| Identity surface | Owner | Purpose | Must not be used for | Lockout control |
|---|---|---|---|---|
| Windows desktop / Omen machine login | Anthony | Local workstation access and local fallback control | End-user app login, Azure resource ownership, Cloudflare policy decisions, GitHub repo delegation | Keep unchanged and independent from cloud login experiments |
| Browser Azure Portal login | Anthony / production cloud admin | Human cloud-resource administration in Azure Portal | AI_OS end-user login, local Omen login, GitHub repo identity, app role authorization | Inventory the active account before provider setup; require recovery path outside the same Microsoft reset loop |
| Azure CLI login | Production AI_OS cloud operator account | CLI-scoped cloud resource work after separate approval | Personal Outlook account use, end-user access, browser-session assumptions, app secrets in repo | Verify active CLI account before every future Azure packet |
| GitHub repo/operator identity | Anthony / `ai-rtony91` | Repo ownership, branch work, PRs, issue/CI review | Azure admin replacement, end-user login, internal AI_OS protected-action approval bypass | Keep as independent backup login provider candidate for Cloudflare Access |
| Cloudflare account/admin identity | Anthony / future Cloudflare admin | Access policy, DNS, tunnel, Turnstile, and front-door security administration after approval | AI_OS backend role authority, Azure admin authority, end-user shared login | Must have at least two independent admin paths before exposing dashboard |
| AI_OS admin identity | Anthony / designated AI_OS admin role | Application administration after backend role checks | Cloud provider control, repo admin control, local Omen login | Separate role assignment from external identity provider login |
| AI_OS end-user identity | Each end user | User authentication to AI_OS app surfaces | Admin login, Azure, Omen, GitHub repo, scheduler, runtime, broker, secrets | Provider-owned user account plus AI_OS backend role authorization |
| Recovery email | Anthony-controlled independent mailbox | Account recovery and reset notification path | Daily admin work, shared user login, repo automation | Must be separate from the primary Microsoft account |
| Break-glass account | Anthony-controlled emergency account | Emergency Cloudflare Access/admin recovery | Routine daily use, automation, end-user login | Independent provider/reset path, documented owner, MFA/recovery separate from primary admin |

## Admin Account Model

Admin access should use multiple independent paths, not one chain where Microsoft, Cloudflare, and recovery all depend on the same mailbox or device.

Recommended admin paths:

- Primary: Microsoft/Entra identity through Cloudflare Access for normal AI_OS admin login.
- Backup: GitHub identity through Cloudflare Access for operator recovery and repo-aligned admin access.
- Optional fallback: Google identity only if it reduces lockout risk without adding unmanaged account sprawl.
- Emergency fallback: Cloudflare OTP constrained to known emergency email addresses and reviewed before enabling.
- Break-glass: a separately controlled emergency account that is not dependent on the same Microsoft account, same recovery mailbox, or same reset loop as the primary admin.
- Local fallback: Omen/Windows login remains unchanged and can access local repo/operator tools even if cloud identity is down.

Admin login does not grant protected-action authority by itself. Commits, pushes, merges, PR closure, provider changes, runtime mutation, queue mutation, scheduler mutation, dashboard exposure, secrets, broker actions, and live trading still require AI_OS approval gates and exact scoped packets.

## End-User Account Model

End users authenticate with their own provider accounts. They must not use Anthony's Azure account, Windows/Omen login, GitHub admin identity, repo credentials, Cloudflare admin identity, scheduler access, runtime access, broker identity, or secrets.

AI_OS must treat external identity as authentication only. The backend must map a verified session to explicit AI_OS app roles such as `viewer`, `operator`, `admin`, or future domain-specific roles. Login identity never equals action authority. A user with a valid Cloudflare Access session still cannot perform protected repo, runtime, approval, scheduler, provider, broker, or live-trading actions unless a separate AI_OS approval gate authorizes that exact action.

## Cloudflare Access Role

Cloudflare Access is the recommended front-door identity gate for any exposed AI_OS dashboard or operator surface. It should sit before the AI_OS app so unauthenticated traffic does not reach the dashboard directly.

Cloudflare Access should:

- enforce approved identity providers and policy groups.
- require at least two independent admin login paths before dashboard exposure.
- keep end-user and admin policies separate.
- block dashboard exposure until Access policy is proven in a future packet.
- avoid becoming the only recovery path for itself.

Cloudflare Access should not:

- store AI_OS app secrets in the repo.
- replace backend role checks.
- replace AI_OS approval gates.
- expose local dashboard surfaces before policy proof.
- be configured by this design packet.

## Turnstile Role

Turnstile is a bot/human check for AI_OS login or sensitive forms. It is not an identity provider and does not authorize user actions.

Future implementation rules:

- The browser receives a Turnstile token only as a challenge result.
- The backend must verify the token server-side with Cloudflare.
- The Turnstile secret key must never be committed, echoed into reports, or stored in `.env` through this lane.
- Passing Turnstile does not grant app role access, admin access, provider access, or protected-action authority.

## Microsoft/Entra Role

Microsoft/Entra should be the primary admin login path for Cloudflare Access once the account inventory confirms the correct tenant, account, recovery route, and ownership. The known tenant ID `feb18abf-17ea-4d88-a4ac-05ffcd6ecb8b` is non-secret metadata and may be recorded in design and inventory reports. Passwords, tokens, client secrets, refresh tokens, API keys, and `.env` values must not be recorded.

Known Azure identity facts recorded for future inventory:

- Azure CLI production account: `ai.tradeplatform@Algotradez.onmicrosoft.com`
- Azure tenant ID: `feb18abf-17ea-4d88-a4ac-05ffcd6ecb8b`
- Azure subscription name: `Subscription 1`
- Azure subscription state: `Enabled`
- Azure CLI default status for the AI TRADEZ subscription: `True`
- Previous Azure CLI identity: `my.laboratory@outlook.com`

The previous Azure CLI identity should not be used for production AI_OS cloud resources unless Anthony separately approves that exception.

## GitHub Role

GitHub should be a backup operator login provider for Cloudflare Access and remains the repo/operator identity path. Known GitHub identity facts:

- GitHub CLI identity: `ai-rtony91`
- Git author identity: `270783377+ai-rtony91@users.noreply.github.com`

GitHub login can help recover access if Microsoft/Entra is unavailable, but it must not become an authorization bypass. Repo privileges, AI_OS app roles, and protected-action gates remain separate.

## Google Role

Google is an optional fallback only. It should be added if it materially improves lockout resilience and has a clearly owned recovery path. If it only adds unmanaged account sprawl, it should be deferred.

Decision rule for Phase 4:

- Use Google fallback only if the account is independently recoverable, MFA-protected, owned by Anthony, and documented as a backup login path.
- Skip Google fallback if Microsoft plus GitHub plus constrained OTP plus break-glass gives enough resilience.

## OTP Role

Cloudflare OTP can be a constrained emergency fallback. It should not be the primary daily login method. OTP should be limited to approved emergency email addresses and reviewed for reset-loop risk before activation.

OTP must not point to the same inbox that would already be inaccessible during a Microsoft lockout unless another independent recovery path exists.

## Break-Glass Account Design

The break-glass account exists to prevent total administrative lockout. It should be rarely used, separately protected, and documented outside normal application login flow.

Required properties:

- Owned by Anthony.
- Independent from the primary Microsoft reset loop.
- Uses a recovery email that is not the same as the primary Microsoft account.
- Has MFA/recovery controls that Anthony can access if the primary provider is unavailable.
- Is eligible for Cloudflare Access or Cloudflare admin recovery only after deliberate provider setup.
- Is not used by end users or automation.
- Is reviewed on a regular cadence in future security maintenance packets.

The break-glass account must not be stored as a password, token, client secret, refresh token, API token, or `.env` value in the repo.

## Local Omen Fallback

Omen/Windows login remains unchanged. This is the local fallback path for repo inspection, local development, and operator recovery if cloud identity is unavailable. Cloudflare Access, Azure Portal, Azure CLI, GitHub, Google, OTP, and AI_OS app login changes must not modify the local Omen login.

No future dashboard exposure should remove the ability to operate AI_OS locally on Omen under governed repo rules.

## Azure CLI Identity Warning

Future Azure work must not assume the browser Azure Portal identity and Azure CLI identity are the same. Azure CLI currently has known production identity facts, but each Azure packet must collect current CLI identity evidence before mutation.

Production cloud work should use `ai.tradeplatform@Algotradez.onmicrosoft.com` unless Anthony separately approves a different identity. `my.laboratory@outlook.com` is a previous CLI identity and should not be used for production AI_OS cloud resources by default.

## Tenant ID Handling Rule

Tenant ID `feb18abf-17ea-4d88-a4ac-05ffcd6ecb8b` is non-secret metadata. It may appear in reports, inventory packets, and design docs.

Never commit or report:

- passwords.
- personal access tokens.
- Cloudflare API tokens.
- Turnstile secret key.
- OAuth client secrets.
- refresh tokens.
- session cookies.
- `.env` values.
- broker credentials.

## Lockout Scenarios And Recovery Paths

| Scenario | Expected impact | Recovery path |
|---|---|---|
| Microsoft/Entra account unavailable | Primary admin login to Cloudflare Access may fail | Use GitHub backup login or break-glass path; do not reconfigure providers from a locked state without inventory |
| Azure Portal browser login unavailable | Portal admin work blocked | Use local Omen access for repo review; verify whether Azure CLI still has intended production identity; defer provider changes until identity is clear |
| Azure CLI account wrong or expired | CLI cloud operations unsafe | Stop future Azure packet; run identity inventory only; do not use previous personal Outlook account for production resources without approval |
| GitHub identity unavailable | Backup operator login and repo actions impaired | Use Microsoft/Entra primary for Access if available; use local Omen for repo state; recover GitHub through GitHub account recovery before repo protected actions |
| Google fallback unavailable | Optional fallback lost | Continue with Microsoft, GitHub, OTP, or break-glass if configured; reassess whether Google adds value |
| Cloudflare account/admin unavailable | Front-door policy and dashboard exposure administration blocked | Use break-glass or alternate Cloudflare admin path; keep local dashboard unexposed; do not change DNS/tunnels from repo |
| Cloudflare Access policy misconfigured | Admin or users may be denied | Use local Omen fallback; use independent Cloudflare admin path; disable or repair policy only through a separately approved provider-change packet |
| OTP email unavailable | Emergency OTP fallback fails | Use GitHub, Microsoft, Google, or break-glass; update OTP target only after identity inventory |
| Local Omen unavailable | Local fallback unavailable | Use cloud/repo recovery paths only if already configured; do not rely on Omen-only secrets because secrets must not be stored in repo |

## Frontend Compromise Model

The frontend is untrusted. Browser code can be inspected, modified, replayed, or bypassed by an attacker. Therefore:

- no secrets go in browser code.
- no `.env` values are exposed to the browser unless explicitly designed as public non-secret values.
- backend verifies Cloudflare Access/session state.
- backend verifies AI_OS app role before returning privileged data.
- backend verifies Turnstile tokens server-side in future implementation.
- backend enforces protected-action routing.
- AI_OS approval gates still control protected actions even for authenticated admins.

## No-Secrets Policy

This lane stores no secrets. It must not request, read, echo, or persist passwords, tokens, client secrets, refresh tokens, Cloudflare API tokens, Turnstile secret keys, session cookies, broker credentials, or `.env` values.

Any future provider implementation packet must use a secret manager or provider dashboard flow outside the repo and must record only non-secret metadata and validation evidence.

## AI_OS Approval-Gate Separation

AI_OS approval gates remain separate from login. External identity proves who authenticated. AI_OS approval gates decide whether a protected action is allowed.

Protected actions include provider configuration, DNS/tunnel changes, dashboard exposure, runtime mutation, scheduler mutation, queue mutation, approval inbox mutation, worker inbox mutation, command queue mutation, broker actions, live trading, commits, pushes, merges, PR closure, destructive cleanup, and secret handling.

Validators may report evidence, but validator PASS does not authorize protected actions.

## Phased Implementation Roadmap

| Phase | Name | Allowed outcome | Stop point |
|---|---|---|---|
| Phase 0 | Identity inventory only | Collect current identity facts and desired account model without secrets | Stop before provider changes |
| Phase 1 | Cloudflare Access design | Define Access app, policies, groups, and no-lockout controls | Stop before configuring Cloudflare |
| Phase 2 | Microsoft/Entra primary plus break-glass design | Define primary admin path and break-glass recovery path | Stop before Azure/Entra changes |
| Phase 3 | GitHub backup login design | Define GitHub backup login path and repo/operator boundary | Stop before GitHub OAuth changes |
| Phase 4 | Google optional fallback decision | Decide whether Google reduces risk or adds account sprawl | Stop before Google OAuth changes |
| Phase 5 | Turnstile design | Define where Turnstile applies and server verification requirements | Stop before Turnstile setup or secret handling |
| Phase 6 | Local dashboard remains blocked until Access is proven | Keep dashboard local-only until Access policy is tested | Stop before dashboard exposure |
| Phase 7 | Implementation packet after review | Generate a provider-specific APPLY packet only after review and approval | Stop before implementation without explicit approval |

## Exact Do Not Configure Yet Stop Point

Stop here. Do not configure Cloudflare, Azure, Entra, GitHub OAuth, Google OAuth, OTP, Turnstile, DNS, tunnels, dashboard exposure, provider dashboards, secrets, credentials, `.env`, runtime, scheduler, queues, approval inbox, worker inbox, command queue, broker paths, or live trading from this design lane.
