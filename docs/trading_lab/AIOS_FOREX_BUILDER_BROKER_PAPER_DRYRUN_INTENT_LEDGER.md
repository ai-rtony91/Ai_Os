# AIOS Forex Builder Broker-Paper Dry-Run Intent Ledger

## Purpose

The dry-run intent ledger is a local, in-memory audit contract for fake broker-paper intents and stub simulation results. It records what the future broker-paper path would have inspected, accepted for local simulation, or rejected before any broker adapter exists.

This is not broker integration. It does not read credentials, use network/API calls, place paper orders, place live orders, write Reports, or enable scheduler/daemon behavior.

## Why This Gate Exists

The adapter stub contract proves that a fake local intent can be normalized and simulated without broker side effects. The dry-run intent ledger adds the next control: every fake intent and every stub decision must become an auditable record before any risk governor or future adapter work is considered.

The ledger separates three things:

- the fake local intent supplied to AIOS.
- the stub simulation decision.
- the safety audit record that proves no broker request or order happened.

## No Credentials, Network, Or Orders

This gate keeps these capabilities blocked:

- broker SDK imports or activation.
- credentials or `.env` reads.
- network/API/socket/HTTP calls.
- webhook registration.
- scheduler or daemon activation.
- broker-paper order placement.
- live order placement.
- Reports writes.

Every record forces `would_place_order`, `order_placed`, `broker_request_sent`, `network_used`, `credentials_used`, `live_ready`, and `broker_paper_orders_allowed` to `false`.

## How Fake Intents Become Audit Records

A fake dry-run intent is first passed through the local adapter stub contract. If the stub accepts it, the ledger records a simulated audit record. If the stub rejects it, the ledger records the rejection reasons.

Both outcomes are useful:

- accepted records prove the local schema can carry a valid fake intent through the stub safely.
- rejected records prove invalid or unsafe inputs are blocked before broker/API/order boundaries.

Rejected intents are not hidden. They are part of the safety audit trail.

## Why In-Memory Is Enough Here

This packet is a contract gate, not a persistence gate. In-memory storage is enough to prove the schema, counters, safety flags, and replay behavior. Durable storage belongs in a later packet only after explicit approval for where audit records may live.

## Preserved Safety Requirements

The ledger contract preserves:

- manual approval requirement.
- presecurity gate requirement.
- adapter stub contract requirement.
- kill switch requirement.
- max loss guard requirement.
- daily stop requirement.
- audit log requirement.
- deterministic record requirement.

These are contract requirements only. They do not authorize broker SDKs, credentials, network calls, paper orders, live orders, schedulers, daemons, or webhooks.

## Honest Status Reading

`DRYRUN_LEDGER_READY` means the local in-memory ledger can record accepted and rejected fake dry-run intents safely.

It does not mean broker ready.
It does not mean credentials allowed.
It does not mean network allowed.
It does not mean paper orders allowed.
It does not mean live trading.

The next safe packet is:

```text
PKT-AIOS-BROKER-PAPER-DRYRUN-RISK-GOVERNOR-V1
```

That next packet should govern dry-run risk constraints before any future broker SDK, credential, network, or execution work is considered.
