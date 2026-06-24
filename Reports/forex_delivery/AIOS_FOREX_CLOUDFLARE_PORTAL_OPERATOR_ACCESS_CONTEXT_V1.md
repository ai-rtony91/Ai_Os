# AIOS Forex Cloudflare Portal Operator Access Context V1

## Scope

Cloudflare login, portal, tunnel, and Access context belongs to operator access and security routing only. It is not broker execution authority.

## Secret Handling

Do not store any Cloudflare login, password, API token, tunnel secret, Access secret, Zero Trust secret, or related credential material in the repository.

Any portal or tunnel proof must be owner-run-only and sanitized before it is recorded.

## Execution Boundary

Cloudflare success does not authorize:

- OANDA broker execution;
- DEMO order placement;
- live order placement;
- broker mutation;
- credential persistence by itself;
- scheduler, daemon, webhook, or background execution.

## Required Remaining Gates

Broker execution still requires:

- broker permission proof;
- secure vault persistence proof;
- read-only broker preflight proof;
- risk gates;
- kill switch proof;
- audit logging;
- signed live exception before live-money use.

