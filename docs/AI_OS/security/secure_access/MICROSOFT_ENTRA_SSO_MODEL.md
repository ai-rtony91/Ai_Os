# Microsoft Entra SSO Model

## Purpose

Microsoft Entra is the intended main SSO identity provider for AI_OS.

It should provide:

- user identity
- future organization login
- future role groups
- centralized access review

## Role In The Flow

Cloudflare Access sends approved login attempts to Microsoft Entra for SSO.

Microsoft Entra confirms the user, then the strong factor challenge can be required for sensitive access.

## Not In This Stage

This document does not include tenant identifiers, app identifiers, credential material, live configuration, or account changes.

## Future Role Groups

Future AI_OS roles may include:

- Home Portal user
- Trading Lab paper reviewer
- Work Table user
- Personal Apps user
- Admin Zone operator

Admin roles should require stronger re-checks.

