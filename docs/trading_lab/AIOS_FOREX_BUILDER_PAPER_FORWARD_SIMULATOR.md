# AIOS Forex Builder Paper-Forward Simulator

Packet: `PKT-AIOS-FOREX-BUILDER-PAPER-FORWARD-SIMULATOR`

## Purpose

The paper-forward simulator is a local deterministic ledger scaffold. It converts `OrderIntent` records into `PaperLedgerEntry` records using local fixture prices.

This is not broker paper trading. It does not submit orders to a broker or exchange.

## Local API

- `simulate_order_intent(intent, fixture_or_price, ledger_state=None) -> PaperLedgerEntry`
- `run_paper_forward_simulation(intents, fixture) -> list[PaperLedgerEntry]`
- `paper_forward_summary(entries) -> dict`

## Rules

- `OrderIntent.status` must remain `INTENT_ONLY`.
- `PaperLedgerEntry.status` must remain `SIMULATED_ONLY`.
- `broker_order_id` must remain `None`.
- `live_order` must remain `false`.
- `execution_allowed` remains `false`; only local simulation is represented.
- No API, network, credentials, webhooks, scheduler, daemon, broker, or live execution path is allowed.

## Acceptance

`tests/forex_engine/test_paper_forward_simulator.py` proves simulated-only ledger entries, no broker order IDs, and no live orders.
