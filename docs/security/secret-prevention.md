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
