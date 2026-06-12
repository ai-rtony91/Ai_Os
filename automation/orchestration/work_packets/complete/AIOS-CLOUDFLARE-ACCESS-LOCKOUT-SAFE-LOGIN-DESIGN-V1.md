# Proposed Request Packet: Cloudflare Access Lockout-Safe Login Design v1

Status: PROPOSED / REVIEW-ONLY / NOT EXECUTABLE

This file is not an executable Codex packet. It does not authorize Cloudflare changes, Azure changes, login-provider changes, DNS changes, tunnel changes, dashboard exposure, secret handling, credential storage, broker action, live trading, queue mutation, runtime execution, scheduler mutation, commit, push, merge, PR closure, or destructive cleanup.

## Purpose

Request a future review-only design lane for a lockout-safe identity front door before exposing any AI_OS dashboard or operator surface beyond local access.

## Design Goals

- Use Cloudflare Access as the front-door identity gate.
- Use Microsoft/Entra as the primary login provider.
- Use GitHub as a backup login provider.
- Use Google as an optional fallback login provider.
- Use Cloudflare OTP as an emergency fallback.
- Include a break-glass account design.
- Preserve a no-lockout requirement.
- Preserve local Omen fallback access.
- Store no secrets in the repo.
- Expose no dashboard without Cloudflare Access.
- Keep AI_OS internal approval gates separate from login identity.

## Required Future Packet Fields

Any future design packet must include:

- `CODEX-ONLY PROMPT`
- `AI_OS EXECUTION TOKEN`
- `AI_OS BOOTSTRAP REQUIRED`
- identity marker
- supervisor identity
- packet ID
- mode
- zone
- worker identity
- lane
- worktree
- branch
- exact allowed paths
- exact forbidden paths
- explicit Anthony approval
- validator chain
- stop point
- mission
- preflight
- final report format

## Required Design Questions

- Which AI_OS surfaces need Cloudflare Access first?
- Which surfaces must remain local-only on Omen?
- Which Microsoft/Entra tenant and account class will be primary without storing secrets?
- Which GitHub identity is acceptable as backup?
- Whether Google fallback is needed or too much account sprawl.
- How Cloudflare OTP emergency fallback is constrained.
- What break-glass account exists, where it is controlled, and how lockout is avoided.
- How dashboard exposure stays blocked until Access policy is proven.
- How AI_OS approval gates remain separate from user login identity.

## Required Forbidden Boundaries

The future design lane must explicitly forbid:

- Cloudflare configuration changes;
- Azure or Entra configuration changes;
- login-provider configuration changes;
- DNS changes;
- tunnel creation or mutation;
- dashboard exposure;
- secret or credential access;
- secret storage;
- `.env` edits;
- broker action;
- live trading;
- queue mutation;
- runtime execution;
- scheduler mutation;
- destructive cleanup;
- direct push to `main`;
- merge;
- PR closure.

## Required Output

The future design lane should produce only a review document and an implementation packet proposal. It must not perform provider setup or store credentials.

## Stop Point

Stop after producing a lockout-safe login design and next proposed implementation packet. Do not configure Cloudflare, Azure, GitHub, Google, OTP, tunnels, DNS, dashboard exposure, or secrets.

## Safe Next Action

Prepare a separate tokenized review-only design packet for Cloudflare Access lockout-safe login, with exact read-only documentation outputs and no provider changes.
