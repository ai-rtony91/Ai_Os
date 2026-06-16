# AIOS Forex Builder Broker-Paper Dry-Run Replay Harness

## Purpose

The broker-paper dry-run replay harness proves that fake local intents can move deterministically through the existing broker-paper safety stack:

1. Broker-paper presecurity gate.
2. Broker-paper adapter stub contract.
3. In-memory dry-run intent ledger.
4. Dry-run risk governor.

This is not broker integration. It does not import broker SDKs, read credentials, call network APIs, place paper orders, place live orders, register webhooks, start schedulers, or start daemons.

## Boundary

The replay harness is local and in-memory only.

- Replay storage: `IN_MEMORY_ONLY`.
- File writes: blocked.
- Reports writes: blocked.
- Broker SDK: blocked.
- Credentials and env secret reads: blocked.
- Network/API: blocked.
- Webhooks: blocked.
- Scheduler/daemon activation: blocked.
- Broker-paper orders: blocked.
- Live orders: blocked.

The only allowed input is a fake/local dry-run intent batch. The default batch includes one accepted fake dry-run intent and one rejected fake dry-run intent so the replay can prove both safe acceptance and safe rejection without execution.

## Flow

Each fake intent is submitted to the existing adapter stub contract. The stub either accepts it for local simulation or rejects it before any broker request. The harness then records the stub result into the existing in-memory dry-run ledger. Finally, the existing dry-run risk governor evaluates the ledger records against max-loss, daily-stop, kill-switch, symbol, quantity, stop-loss, and execution-flag rules.

Accepted records prove that safe fake intents can reach risk accounting. Rejected records prove that unsafe fake intents stay rejected while `would_place_order`, `order_placed`, `broker_request_sent`, `network_used`, `credentials_used`, and `live_ready` remain false.

## EOM Alignment

This supports the end-of-month milestone by proving deterministic broker-paper dry-run replay through the already merged safety stack from PRs #754 through #757. It advances evidence quality without enabling broker-paper trading.

The next safe packet is:

```text
PKT-AIOS-BROKER-PAPER-DRYRUN-REPLAY-EVIDENCE-GATE-V1
```

The next packet is not broker SDK integration, credentials, network/API setup, broker-paper order execution, scheduler work, daemon work, webhook execution, or live trading.
