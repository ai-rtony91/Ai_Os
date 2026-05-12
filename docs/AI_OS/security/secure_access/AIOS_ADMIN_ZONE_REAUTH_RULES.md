# AI_OS Admin Zone Re-Auth Rules

## Rule

Admin Zone must require stronger re-check before dangerous or administrative actions.

## Re-Check Inputs

The intended re-check is:

- Cloudflare Access session still valid
- Microsoft Entra identity still valid
- YubiKey or FIDO2 passkey challenge satisfied

## Admin Zone Examples

Admin Zone may eventually include:

- user access review
- role group review
- local service state review
- protected configuration review
- deployment readiness review

## Blocked In This Stage

This documentation does not enable configuration changes, installs, live Cloudflare settings, live Azure settings, or trading execution.

## Trading Lab Boundary

Even after admin re-check, Trading Lab remains paper-only until a separate future approval explicitly changes trading mode.

