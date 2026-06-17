# Secret Prevention Guidance

Status: baseline scaffold, pending human review.

## Never Commit

- API keys
- broker tokens
- passwords
- private keys
- session cookies
- .env files
- account identifiers
- sensitive logs

## Local Handling

Use environment variables or an approved secret manager.

## Future Broker Credential Boundary

Broker credentials for any future Single Live Micro-Trade Exception must live only in an external Human Owner-controlled vault outside the repo and outside AI-readable runtime.

AI_OS may store only non-sensitive proof or opaque references. Stored proof or references must not reveal credential values, account identifiers, broker order identifiers, live payloads, private account data, or secret material.

Credentials, tokens, account identifiers, broker order IDs, live payloads, private account data, and secret values must never enter repo files, logs, prompts, reports, screenshots, telemetry, or fixtures.

Codex, ChatGPT, validators, dashboards, reports, queues, routers, tests, fixtures, and generated evidence must never see secrets. These surfaces may receive only redacted evidence such as pass/fail facts, approval status, expiration status, and non-sensitive policy references.

## Review Before Push

Run:

git status
git diff --staged
git diff

Search for secret-like terms before committing.

## If A Secret Is Committed

1. Stop using the secret immediately.
2. Revoke or rotate the credential.
3. Remove it from tracked files.
4. Review Git history exposure.
5. Document the incident.
