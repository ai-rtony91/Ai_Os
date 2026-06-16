# AIOS Forex Builder Broker-Paper Dry-Run Replay Evidence Gate

This packet adds a local evidence gate for the broker-paper dry-run replay harness. The gate reads an in-memory replay result from the existing harness and checks whether the already-merged safety stack produced enough deterministic proof to support a future adapter planning approval gate.

This is not broker integration. It does not import a broker SDK, open a network path, read credentials, read `.env`, register webhooks, start a scheduler, start a daemon, place broker-paper orders, or place live orders.

## What The Gate Proves

The replay harness already sends fake local intents through the broker-paper stub, records the dry-run ledger, and evaluates the ledger with the dry-run risk governor. The evidence gate verifies that the replay result contains:

- at least two replayed records
- at least one accepted and one rejected stub result
- at least one accepted and one rejected risk decision
- aggregate max loss no higher than the daily cap
- an armed kill switch
- false unsafe flags for order placement, broker requests, network, credentials, broker-paper orders, and live readiness

Accepted and rejected records matter because a safety stack that only accepts happy-path examples is not enough. The evidence gate requires both allowed local dry-run flow and rejected unsafe or invalid flow before advancing.

## Safety Boundary

The gate stores evidence in memory only. File writes and Reports writes are blocked. Broker SDKs, credentials, network/API, webhooks, schedulers, daemons, broker-paper orders, and live orders remain blocked.

The only allowed classifications are `FAIL`, `WATCHLIST`, and `DRYRUN_REPLAY_EVIDENCE_READY`. It must never emit `LIVE_READY`, `BROKER_READY`, or `ORDER_READY`.

## EOM Alignment

This supports the end-of-month milestone by proving deterministic broker-paper dry-run replay through the existing safety stack. It prepares evidence for future broker-paper planning without enabling a broker connection or order execution.

The next safe packet after a passing evidence gate is:

```text
PKT-AIOS-BROKER-PAPER-ADAPTER-PLAN-APPROVAL-GATE-V1
```

That is a planning and approval gate, not broker SDK activation.
