# Cloudflare Access Setup Plan

## Purpose

Cloudflare Access is the secure front door for AI_OS.

It should block unauthenticated traffic before AI_OS loads.

## Planned Role

- Protect `https://aios.algobots.trade`.
- Require approved identity.
- Send login to Microsoft Entra SSO.
- Allow only approved operators to reach AI_OS.

## Setup Planning Steps

1. Confirm the public AI_OS hostname.
2. Define the protected application concept.
3. Define who may reach the portal.
4. Require Microsoft Entra as the identity provider.
5. Keep Admin Zone behind stronger checks.

## Boundary

This is a plan only. It includes no live Cloudflare settings and makes no account changes.

