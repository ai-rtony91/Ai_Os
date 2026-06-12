# AIOS Cloudflare Access Provider Setup Apply Request - Turnstile Post-Access Revision

Status: APPLY REQUEST ONLY / NOT EXECUTABLE / REVIEW REQUIRED

This file is not an executable Codex packet. It does not contain `AI_OS EXECUTION TOKEN` and does not authorize Cloudflare, Turnstile, Azure, Entra, GitHub OAuth, Google OAuth, DNS, tunnel, dashboard exposure, OTP, secret, credential, runtime, scheduler, queue, broker, live-trading, commit, push, merge, PR closure, or destructive cleanup actions.

## Purpose

Revise the future Cloudflare Access provider setup apply request so the Turnstile boundary is explicit:

1. AI_OS URL.
2. Cloudflare Access identity login.
3. AI_OS post-login Turnstile check.
4. AI_OS dashboard/session.
5. Extra Turnstile only before third-party service handoff or login screens.

## Required Separate Approval

Before any provider dashboard action, a future executable packet must include:

- `CODEX-ONLY PROMPT`
- `AI_OS EXECUTION TOKEN`
- `AI_OS BOOTSTRAP REQUIRED`
- explicit Anthony approval for the exact provider dashboard action
- exact allowed provider surface
- exact forbidden actions
- no-secrets rule
- rollback path
- proof checklist
- stop point

## Turnstile Policy Revision

Future provider setup must treat Cloudflare Access as the front-door identity gate. Turnstile must not run before Cloudflare Access identity login.

Turnstile is mandatory only:

- after successful Cloudflare Access identity login and before AI_OS app session creation.
- before AI_OS initiates or displays in-app third-party service login or handoff screens such as TradingView or similar connected services.

Turnstile is not mandatory:

- globally on every dashboard page load.
- for every admin click.
- for normal already-authenticated navigation.
- for local Omen-only access unless that local flow is later approved for remote exposure.

Turnstile is not identity authority and does not replace Microsoft, GitHub, Google, OTP, Cloudflare Access, backend roles, or AI_OS approval gates.

## Third-Party Service Handoff Boundary

AI_OS must not store third-party service credentials in frontend code or the repo. Future third-party service handoff work must preserve:

- no passwords in repo.
- no OAuth client secrets in repo.
- no refresh tokens in repo.
- no session cookies in repo.
- no broker credentials in repo.
- no `.env` edits from this request.
- backend verification before privileged app access.
- AI_OS approval gates for protected runtime, scheduler, queue, broker, and live-trading actions.

External service handoff must not grant broker or trading authority without the required AI_OS approval gates.

## Non-Negotiable Boundaries

- No Cloudflare configuration from this request.
- No Turnstile configuration from this request.
- No Azure or Entra configuration.
- No GitHub OAuth configuration.
- No Google OAuth configuration.
- No OTP configuration.
- No DNS changes.
- No tunnel creation or mutation.
- No dashboard exposure until Access policy is proven.
- No secrets in repo.
- No Cloudflare API tokens.
- No Turnstile secret key.
- No passwords.
- No recovery codes.
- No session cookies.
- No `.env` edits.
- No runtime, scheduler, queue, worker inbox, approval inbox, command queue, broker, or live-trading changes.

## Required Future Proof

Before any remote dashboard exposure, future APPLY work must prove:

- Cloudflare Access identity login succeeds first.
- AI_OS post-login Turnstile check runs only after Access authentication.
- AI_OS app session is created only after backend verification.
- Turnstile does not run before Cloudflare Access.
- Turnstile does not run on every dashboard page, click, or normal authenticated navigation.
- Turnstile runs before third-party service handoff or login screens.
- Microsoft/Entra primary login path remains available.
- GitHub backup login path remains available.
- break-glass path remains independently recoverable.
- local Omen fallback still works.
- no secrets were committed.
- AI_OS approval gates still control protected actions.

## Stop Point

Stop after Anthony reviews this revised apply request. Do not execute provider setup from this file.

## Safe Next Action

Generate a complete tokenized provider-dashboard packet only after Anthony explicitly approves the exact Cloudflare or Turnstile dashboard action and confirms unresolved identity and recovery inputs.
