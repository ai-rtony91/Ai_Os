# Forex and OANDA Boundary

## Purpose

This document clarifies the current Forex and OANDA boundary for AI_OS.

Forex paper/sandbox engine code exists in this repository under `automation/forex_engine/`. That code is for local paper research, local sandbox modeling, deterministic validation, and non-live evidence only. It is not live trading, not broker connectivity, and not OANDA integration.

OANDA/live broker execution is BLOCKED.

Forex paper/sandbox evidence is allowed only when it remains local, non-live, non-broker, and non-order-routing.

## Current allowed state

The current allowed Forex state is limited to:

- read-only review of Forex and OANDA boundaries;
- documentation and planning;
- local paper/sandbox model validation;
- local fake, fixture, or synthetic data tests;
- local paper-only readiness checks;
- local sandbox-only broker-shape modeling with network disabled;
- validation that proves execution remains blocked.

Allowed paper/sandbox evidence must not require network broker calls, live account connectivity, broker credentials, OANDA credentials, account identifiers, webhook delivery, real order routing, runtime mutation, worker launch, scheduler launch, queue mutation, or approval mutation.

## Current forbidden state

The following remain forbidden:

- OANDA API calls;
- broker API calls;
- broker credentials;
- OANDA credentials;
- tokens, account IDs, passwords, private keys, or recovery keys;
- `.env` consumption for broker or OANDA access;
- webhook paths that route real orders;
- live order placement;
- order modification or cancellation against a real broker;
- real money trading;
- live market data fetches for execution;
- runtime, worker, scheduler, daemon, or queue mutation for trading execution;
- dashboard controls that trigger trading execution;
- telemetry or Reports output that becomes execution authority.

No AI_OS document, dashboard panel, telemetry record, validator result, packet, worker, script, or recommendation may treat Forex/OANDA planning as approval for broker execution.

## Relationship to Trading Lab

Trading Lab remains paper-only. PR #648 completed the Trading Lab paper boundary review state.

That completion only allows a Forex/OANDA documentation-boundary review. It does not authorize live broker integration. It does not authorize OANDA implementation. It does not authorize broker credentials, webhooks, real orders, live account connectivity, runtime launch, worker launch, scheduler launch, queue mutation, or approval mutation.

Trading Lab paper evidence may support future review of Forex paper/sandbox evidence, but it must not become a bridge into live broker execution.

## Relationship to telemetry

PR #647 completed the telemetry contract review state.

Telemetry may later support paper/sandbox evidence, replayable validation evidence, and audit trails if a separate approved packet authorizes that work. Telemetry must not become an execution path. Telemetry must not approve broker access, OANDA access, webhook delivery, real orders, runtime launch, worker launch, scheduler launch, queue mutation, approval mutation, or live trading.

## Relationship to active Forex implementation

The active Forex implementation under `automation/forex_engine/` is paper/sandbox scoped.

Current evidence shows the active Forex surfaces use patterns such as:

- `PAPER_ONLY` mode;
- local fixture or synthetic data;
- `execution_allowed = false`;
- blocked actions for broker calls, OANDA calls, real order submission, webhooks, secrets, live market data, workers, and schedulers;
- sandbox-model-only broker shaping with network disabled and credentials not loaded;
- tests that reject live mode, credential-like metadata, and external network behavior.

Those surfaces are allowed only as local paper/sandbox evidence. They do not create broker authority. They do not create OANDA authority. They do not create live trading readiness.

## Future path

A future registry-only packet may advance `STAGE-FOREX-DOCS-BOUNDARY` if this boundary is reviewed and accepted. That future packet must be limited to registry or review bookkeeping and must not implement Forex, OANDA, broker, webhook, order, runtime, worker, scheduler, queue, telemetry, Reports, dashboard, secret, or `.env` behavior.

Any future implementation packet must be separate, explicit, and safety-gated.

Any future OANDA or live broker work requires separate Human Owner approval, an approved secrets policy, an approved broker boundary, paper validation, fail-closed tests, rollback planning, and audit evidence. Until those gates exist and are explicitly approved, OANDA/live broker execution remains blocked.

## Non-goals

This document does not:

- mutate the campaign registry;
- create a READY stage;
- reopen a completed stage;
- implement Forex changes;
- implement OANDA changes;
- implement broker code;
- create webhooks;
- create order paths;
- read or write secrets;
- read or write `.env`;
- launch runtime, workers, schedulers, queues, daemons, dashboards, telemetry, or Reports;
- approve APPLY, commit, push, PR, merge, or live trading.
