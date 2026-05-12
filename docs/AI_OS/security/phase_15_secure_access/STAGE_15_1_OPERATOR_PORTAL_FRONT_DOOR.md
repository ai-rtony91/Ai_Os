# Stage 15.1 Operator Portal Front Door

## Purpose

Stage 15.1 defines the protected entry path for AI_OS.

AI_OS should not load for unauthenticated public visitors. Cloudflare Access should stand in front of the portal and require approved identity before the application is visible.

## Entry URL

`https://aios.algobots.trade`

## Front Door Flow

1. User opens the AI_OS URL.
2. Cloudflare Access evaluates access policy.
3. Microsoft Entra SSO confirms user identity.
4. YubiKey or FIDO2 passkey challenge confirms strong login.
5. AI_OS Home Portal opens.

## Not Included

This document does not configure live DNS, tunnels, account settings, identity provider settings, application IDs, tokens, or secrets.

