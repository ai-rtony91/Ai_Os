# AIOS Forex Builder Broker-Paper Adapter Stub Contract

## Purpose

The broker-paper adapter stub is a local contract for the shape of future broker-paper adapter
work. It defines allowed fake intent fields, validation rules, audit expectations, and safety
invariants without connecting to a broker or preparing real order execution.

This is not broker integration. It does not import a broker SDK, read credentials, read `.env`,
use network/API calls, register webhooks, start schedulers or daemons, place broker-paper orders,
or place live orders.

## Intent Validation

The stub accepts only local fake fields:

- `symbol`
- `side`
- `quantity_units`
- `order_type`
- `stop_loss_pips`
- `take_profit_pips`
- `max_loss_usd`
- `dry_run`
- `approved_by_operator`

Validation requires `dry_run: true`, a fake allowlisted symbol, `buy` or `sell`, `market_stub` or
`limit_stub`, stop loss, max loss, and operator approval metadata. Approval metadata is recorded
for future execution discipline, but this packet still cannot execute anything.

## Safety Controls

The contract preserves the presecurity controls:

- manual approval required
- presecurity gate required
- kill switch required
- max loss guard required
- daily stop required
- audit log required

Every simulation returns `would_place_order: false`, `order_placed: false`,
`broker_request_sent: false`, `network_used: false`, `credentials_used: false`, and
`live_ready: false`.

## Next Packet

If the stub contract validates, the next safe packet is:

`PKT-AIOS-BROKER-PAPER-DRYRUN-INTENT-LEDGER-V1`

That packet should build a local dry-run ledger. It is not broker SDK integration, credentials
work, broker-paper order execution, live trading, webhook activation, scheduler activation, or
daemon activation.
