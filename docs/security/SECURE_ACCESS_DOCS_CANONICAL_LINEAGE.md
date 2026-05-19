# AI_OS Secure Access Docs Canonical Lineage

Status: canonical security lineage note
Sources: `docs/AI_OS/security/secure_access`, `docs/AI_OS/security/phase_15_secure_access`

## Purpose

This document records the lineage decision for secure access documentation. It does not configure Cloudflare, Microsoft Entra, YubiKey, passkeys, GitHub permissions, secrets, accounts, or live trading.

## Lineage Decision

`docs/AI_OS/security/secure_access` is the stronger canonical source candidate for secure access architecture because it contains the broader access model, front-door model, GitHub identity boundary, admin reauth rules, and setup checklist template.

`docs/AI_OS/security/phase_15_secure_access` appears to be a phase-specific planning lineage. It overlaps with `secure_access` and should be treated as an archive candidate only after active references and validator expectations are reviewed.

No secure access folder is archive-ready in this pass.

## Preserved Boundary

Secure access protects AI_OS access. It does not change trading mode.

Trading Lab remains paper-only:

- no broker login.
- no live orders.
- no OANDA or broker connection.
- no trading execution activation.

## Required Future Review

Before any secure access docs move:

- scan active automation/security references.
- confirm which validator treats which lineage as required.
- preserve Cloudflare Access, Microsoft Entra, YubiKey/passkey, GitHub identity, portal zone, and admin reauth concepts.
- confirm no secrets or live configuration are introduced.
- move only with `git mv` after final scans are clear.

