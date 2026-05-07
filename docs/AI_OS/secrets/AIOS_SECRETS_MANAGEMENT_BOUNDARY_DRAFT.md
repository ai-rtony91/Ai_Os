# AIOS Secrets Management Boundary Draft

Status: Draft scaffold

## Purpose

Document how AI_OS should reason about secrets without storing or exposing real secret material.

## Rules

- Never commit real secrets.
- Never paste broker tokens, API keys, private keys, or recovery keys.
- Use placeholders only.
- Treat suspected credentials as protected data.
- Log secret-handling errors to `ERROR_LOG.md` only with redacted values.

## Future Requirements

- Secret scanning policy.
- Local environment variable guidance.
- Deployment secret store decision.
- Rotation and revocation procedure.

## Unknowns

- UNKNOWN: future secret storage provider.
- UNKNOWN: production credential rotation process.
