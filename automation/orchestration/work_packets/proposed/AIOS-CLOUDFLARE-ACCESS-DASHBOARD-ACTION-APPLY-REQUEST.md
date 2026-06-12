# AIOS Cloudflare Access Dashboard Action Apply Request

Status: APPLY REQUEST ONLY / NOT EXECUTABLE / REVIEW REQUIRED

This file is not an executable Codex packet. It does not contain `AI_OS EXECUTION TOKEN` and does not authorize Cloudflare, Turnstile, Azure, Entra, GitHub OAuth, Google OAuth, OTP, DNS, tunnel, dashboard exposure, secret, credential, runtime, scheduler, queue, broker, live-trading, commit, push, merge, PR closure, or destructive cleanup actions.

## Purpose

Request a future, separately approved human-guided Cloudflare dashboard APPLY lane for AI_OS Access setup preparation. The future lane must preserve the lockout-safe design and post-Access Turnstile policy.

## Required Anthony Confirmations

Before any future dashboard action, Anthony must confirm:

- Cloudflare account identity and admin class.
- Cloudflare admin/recovery path independence.
- domain/subdomain target.
- Access app name.
- primary Microsoft/Entra account.
- GitHub backup account.
- whether Google fallback is enabled.
- OTP emergency boundary.
- break-glass/recovery path.
- no secrets in repo.
- no DNS, tunnel, or dashboard exposure until Access policy is proven.

## Future Dashboard Action Boundary

A future executable packet may request approval to inspect or prepare one Cloudflare dashboard step at a time. Candidate future steps:

1. Confirm Cloudflare account and recovery state.
2. Navigate to Cloudflare One / Zero Trust and Access controls / Applications if visible.
3. Draft a self-hosted Access application object for AI_OS without exposing it.
4. Confirm Access application name.
5. Confirm domain/subdomain target without DNS changes.
6. Draft identity provider ordering: Microsoft/Entra primary, GitHub backup, Google optional, OTP emergency.
7. Confirm deny-by-default and separate admin/end-user policy design.
8. Confirm post-Access Turnstile placement.
9. Stop before save, publish, DNS, tunnel, dashboard exposure, provider mutation, or secret handling unless a later packet explicitly approves that exact action.

## Turnstile Policy Boundary

Future setup must preserve this login flow:

1. AI_OS URL.
2. Cloudflare Access identity login.
3. AI_OS post-login Turnstile check.
4. AI_OS dashboard/session.
5. Extra Turnstile only before third-party service handoff or login screens.

Turnstile must run after successful Cloudflare Access identity login and before AI_OS app session creation. It must also run before in-app third-party service handoff/login screens such as TradingView.

Turnstile must not run before Cloudflare Access identity login, on every dashboard page load, on every admin click, or during normal authenticated navigation. Turnstile is not identity authority and does not replace Microsoft, GitHub, Google, OTP, Cloudflare Access, backend roles, or AI_OS approval gates.

## No-Secrets Boundary

Never store or commit:

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

Allowed non-secret metadata includes account display/class, provider names, policy names, tenant ID, app name, domain/subdomain class, and sanitized pass/fail proof.

## Required Future Proof

Before any remote dashboard exposure, future work must prove:

- Cloudflare Access identity login succeeds first.
- Microsoft/Entra primary admin can log in.
- GitHub backup can log in.
- break-glass path is independently recoverable.
- AI_OS post-login Turnstile check runs after Access login and before app session creation.
- Turnstile runs before third-party service handoff/login screens.
- Turnstile does not run before Cloudflare Access.
- Turnstile does not run globally on dashboard page loads, clicks, or normal authenticated navigation.
- dashboard is inaccessible without Cloudflare Access.
- local Omen fallback still works.
- no secrets were committed.
- AI_OS approval gates still control protected actions.

## Stop Point

Stop after Anthony reviews this apply request. Do not execute provider setup from this file.

## Safe Next Action

Generate a complete tokenized Cloudflare dashboard APPLY packet only after Anthony explicitly approves the exact dashboard action and supplies the unresolved non-secret identity, recovery, and domain/subdomain inputs.
