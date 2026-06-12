# AI_OS Turnstile Post-Access Login And Service-Handoff Policy

Status: DRY_RUN POLICY READY FOR REVIEW
Packet: AIOS-TURNSTILE-POST-ACCESS-LOGIN-AND-SERVICE-HANDOFF-POLICY-V1
Lane: turnstile-post-access-login-service-handoff-policy
Mode: DRY_RUN
Generated: 2026-06-12

## Executive Summary

This policy correction makes the AI_OS login sequence explicit: Cloudflare Access identity login comes first, then AI_OS performs a post-login Turnstile check before creating the AI_OS app session. Turnstile is also mandatory before AI_OS initiates or displays in-app third-party service login or handoff screens, including TradingView or similar connected services.

Turnstile must not run before Cloudflare Access identity login. It must not run on every dashboard page load, every admin click, or normal already-authenticated navigation. Cloudflare Access remains the front-door identity gate, and AI_OS backend roles plus internal approval gates remain mandatory for authorization and protected actions.

This DRY_RUN policy does not configure Cloudflare, Turnstile, Azure, Entra, GitHub OAuth, Google OAuth, DNS, tunnels, dashboard exposure, secrets, credentials, runtime, scheduler, queues, broker paths, or live trading.

## Exact Login Flow

1. AI_OS URL.
2. Cloudflare Access identity login.
3. AI_OS post-login Turnstile check.
4. AI_OS dashboard/session creation.
5. Extra Turnstile only before third-party service handoff or login screens.

The Turnstile checkpoint belongs after successful Cloudflare Access authentication and before AI_OS creates an application session. It is not a pre-Access challenge.

## Policy Correction

Cloudflare Access is the front-door identity gate for remote AI_OS access. Microsoft/Entra primary login, GitHub backup login, Google optional fallback, OTP emergency fallback, and break-glass recovery remain part of the no-lockout login stack.

Turnstile is a post-Access bot/human verification layer. It must run:

- after successful Cloudflare Access identity login.
- before AI_OS app session creation.
- before in-app third-party service login or handoff flows such as TradingView or similar connected services.

Turnstile must not run:

- before Cloudflare Access identity login.
- globally on every dashboard page load.
- for every admin click.
- for normal already-authenticated navigation.
- as a replacement for backend roles, provider identity, or AI_OS approval gates.

## Cloudflare Access Role

Cloudflare Access remains the real front-door identity gate. Any future remote AI_OS surface must require Cloudflare Access before the AI_OS application can create a session.

Access identity login determines whether the user may reach the AI_OS application boundary. It does not grant app role authority, protected-action authority, provider authority, repo authority, runtime authority, scheduler authority, broker authority, or live-trading authority.

## Turnstile Role

Turnstile is mandatory only in the post-Access login and service-handoff contexts defined by this policy. It is not identity authority.

Future backend implementation must verify Turnstile tokens server-side. Browser-visible Turnstile data may include only public site-key material. The Turnstile secret key must never be committed, echoed into reports, stored in `.env`, or placed in frontend code.

Passing Turnstile does not create an AI_OS role by itself. It only satisfies the bot/human checkpoint required before app session creation or before third-party service handoff screens.

## Third-Party Service Handoff Policy

AI_OS must require an additional Turnstile check before entering in-app third-party service login or handoff flows, including TradingView or similar connected services.

Third-party service handoff must not grant broker, trading, scheduler, runtime, queue, secret, or repo authority. Any handoff that could affect protected AI_OS behavior still requires backend role checks and AI_OS approval gates.

AI_OS must not store third-party service credentials in frontend code or the repo. Passwords, API keys, OAuth client secrets, refresh tokens, session cookies, recovery codes, broker credentials, and `.env` values remain forbidden.

## Non-Mandatory Turnstile Contexts

Turnstile is not mandatory for:

- Cloudflare Access identity login before Access has authenticated the user.
- every dashboard page load.
- every admin click.
- normal already-authenticated navigation.
- local Omen-only access unless that local flow is separately approved for remote exposure later.

This boundary prevents Turnstile from becoming noisy friction across normal authenticated use while preserving it at the two risk points that matter for this policy: session creation and third-party handoff.

## Preserved Login And Recovery Stack

This correction preserves the existing no-lockout stack:

- Microsoft/Entra remains the primary admin login path candidate.
- GitHub remains the backup operator login path candidate.
- Google remains optional fallback only.
- Cloudflare OTP remains constrained emergency fallback only.
- Break-glass recovery remains required before exposure.
- Local Omen fallback remains unchanged.
- At least two independent admin paths remain required before any dashboard exposure.

## AI_OS Approval-Gate Separation

Login and Turnstile checks do not authorize protected actions. AI_OS internal approval gates remain mandatory for runtime mutation, scheduler mutation, queue mutation, approval inbox mutation, worker inbox mutation, command queue mutation, broker actions, live trading, provider configuration, DNS changes, tunnel changes, dashboard exposure, commits, pushes, merges, PR closure, destructive cleanup, and secret handling.

External service handoffs must not grant broker or trading authority without the required AI_OS approval gates.

## Frontend And No-Secrets Assumptions

The frontend is untrusted. Browser code can be inspected, replayed, altered, or bypassed.

Required controls:

- no secrets in browser code.
- no secrets in repo.
- no third-party service credentials in frontend code.
- backend verifies Cloudflare Access/session state.
- backend verifies AI_OS app role before privileged access.
- backend verifies Turnstile token server-side in future implementation.
- protected actions continue through AI_OS approval gates.

## Exact Stop Point

Stop here. Do not configure Cloudflare, Turnstile, Azure, Entra, GitHub OAuth, Google OAuth, OTP, DNS, tunnels, dashboard exposure, provider dashboards, secrets, credentials, `.env`, runtime, scheduler, queues, approval inbox, worker inbox, command queue, broker paths, or live trading from this policy lane.
