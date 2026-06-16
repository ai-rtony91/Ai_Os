# AIOS Forex Builder Broker-Paper Presecurity Gate

## Purpose

The pre-security gate comes before any broker-paper sandbox adapter work. AIOS is close enough
to broker-paper territory that security controls must exist before credentials, broker SDKs,
network calls, webhooks, order execution, schedulers, or daemons are allowed.

This gate is a contract-only checkpoint. It does not connect to a broker, read secrets, place
paper orders, place live orders, register webhooks, or start background automation.

## Credential And Secret Boundary

Credentials remain blocked. `.env` and secret reads remain blocked. The gate requires explicit
secret exclusion patterns:

- `.env`
- `*.env`
- `.env.*`
- `*.pem`
- `*.key`
- `id_rsa`
- `id_ed25519`
- `*.pfx`
- `*.p12`
- `*secret*`
- `*secrets*`

Broker-paper adapter work cannot begin until the credential boundary exists as an approved
contract. This packet does not create that credential implementation.

## Network And Broker Adapter Boundary

Network/API access is blocked until a future approval gate names the exact allowed adapter,
host boundary, request behavior, logging, and stop controls. Broker SDK activation is blocked.
Webhook registration and webhook execution are blocked.

## Execution Controls Required

Before any future adapter-stub can move toward broker-paper execution, AIOS must require:

- manual approval
- kill switch
- max loss guard
- daily stop
- audit log
- RustDesk/operator access hygiene
- no scheduler or daemon activation without separate approval

These are requirements only. They do not authorize order routing.

## Readiness Meaning

`PRESECURITY_READY` means the security contract requirements are present and validated. It does
not mean broker ready, credential ready, network ready, paper-order ready, or live ready.

If the gate is ready, the only safe next packet is:

`PKT-AIOS-BROKER-PAPER-SANDBOX-ADAPTER-STUB-CONTRACT`

That future packet must remain an adapter-stub contract unless separately approved. Live trading
and broker-paper order execution remain blocked.
