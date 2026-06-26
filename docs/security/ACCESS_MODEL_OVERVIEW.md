# AI_OS Access Model Overview

Status: canonical security summary
Source: `docs/AI_OS/security/secure_access/AIOS_ACCESS_MODEL_OVERVIEW.md`

## Plain-English Model

AI_OS should sit behind a secure front door.

- Cloudflare Access can protect a public URL.
- Microsoft Entra can verify user identity.
- YubiKey or passkey can provide phishing-resistant proof.
- AI_OS should receive only approved users.
- Admin and dangerous zones require stronger re-checks.

## Identity Roles

GitHub is for code identity: repository permissions, commits, pull, and push.

Microsoft Entra is for login identity: SSO, future organization users, and future role groups.

YubiKey/passkey is for strong physical login proof.

Cloudflare Access is the front door that blocks unauthenticated visitors before AI_OS loads.

## Trading Safety

Secure access does not enable trading or broker authority.

Trading Lab / Forex remains in the default paper/simulation or approved demo-review stage unless a separate reviewed policy changes it:

- no broker login.
- no live orders.
- no OANDA or broker connection.
- no trading execution activation.

