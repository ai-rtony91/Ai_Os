# AI_OS Access Model Overview

## Plain-English Model

AI_OS should sit behind a secure front door.

- Cloudflare Access protects the public URL.
- Microsoft Entra verifies the user identity.
- YubiKey or passkey provides phishing-resistant proof.
- AI_OS receives only approved users.
- Admin and dangerous zones require stronger re-checks.

## Identity Roles

GitHub is for code identity: repo permissions, commits, pull, and push.

Microsoft Entra is for user login identity: SSO, future organization users, and future role groups.

YubiKey/passkey is for strong physical login proof.

Cloudflare Access is the front door that blocks unauthenticated visitors before AI_OS loads.

## Trading Safety

Secure access protects the app. It does not change trading mode or grant broker authority.

Trading Lab / Forex remains in the default paper/simulation or approved demo-review stage unless separate governed approval changes it:

- no broker login
- no live orders
- no OANDA or Webull connection
- no trading execution activation

