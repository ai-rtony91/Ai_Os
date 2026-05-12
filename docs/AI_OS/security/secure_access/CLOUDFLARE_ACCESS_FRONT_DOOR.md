# Cloudflare Access Front Door

## Purpose

Cloudflare Access is the protected HTTPS front door for AI_OS.

It should block unauthenticated visitors before the AI_OS application loads.

## Target Public URL

`https://aios.algobots.trade`

## Intended Behavior

1. Visitor opens the AI_OS URL.
2. Cloudflare Access checks policy.
3. Unapproved visitors are stopped.
4. Approved visitors are sent to Microsoft Entra SSO.
5. Only approved identity reaches AI_OS.

## Not In This Stage

This document does not create live Cloudflare configuration.

No policy IDs, tokens, live routes, account changes, tunnels, or deployment settings are included.

## Trading Boundary

Cloudflare Access protects entry to AI_OS. It does not enable broker access, external route delivery, live orders, or live trading.

