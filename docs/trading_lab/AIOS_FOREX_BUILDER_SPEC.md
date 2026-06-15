# AIOS Forex Builder Canonical Product Spec

Packet: `PKT-AIOS-FOREX-BUILDER-CANONICAL-SPEC`
Lane: `forex-builder-spec`
Status: canonical non-live product spec

## Product Mission

AIOS builds an industrial-grade forex bot builder through safe staged development. The first proof target is a local, deterministic, non-live forex builder that can define strategies, validate fixture data, run repeatable backtests, apply risk gates, and report blockers before any execution capability is considered.

This spec defines the product contract only. It does not authorize broker integration, paper execution, live execution, credentials, background workers, network automation, or account mutation.

## Non-Live Boundary

The forex builder is non-live only until a separate future protected approval explicitly expands scope.

Forbidden boundaries:

- No broker integration.
- No OANDA/live exchange integration.
- No live orders.
- No paper orders unless separately approved later.
- No credentials, secrets, or env reads or writes.
- No webhooks.
- No scheduler or daemon execution.
- No real-money trading.
- No account mutation.
- No network market automation.

Any packet, module, dashboard control, report, or test that crosses these boundaries must be blocked and reported as an SOS condition.

## Development Phases

Phase 0: canonical spec.

- Establish this canonical product spec, forbidden boundaries, staged roadmap, dashboard contract, and acceptance criteria.
- Output: `docs/trading_lab/AIOS_FOREX_BUILDER_SPEC.md`.

Phase 1: local data schemas.

- Define local market-data fixture schemas, strategy configuration schemas, signal result schemas, backtest result schemas, and paper ledger simulator schemas.
- Data remains local fixture data only.

Phase 2: deterministic local backtest harness.

- Build a deterministic backtest harness that consumes local fixtures and strategy definitions.
- Backtests must be repeatable, offline, and testable with fixed expected outputs.

Phase 3: risk gate contract.

- Define the risk gate contract for rejecting unsafe strategy settings, position sizing assumptions, drawdown limits, incomplete fixtures, and missing approvals.
- Risk gate output must be explicit, structured, and dashboard-readable.

Phase 4: dashboard/reporting contract.

- Define dashboard status fields, reporting outputs, current blocker handling, SOS requirements, and next safe action language.
- Dashboard output is status and evidence only.

Phase 5: paper-trading simulator only after separate approval.

- A local paper ledger simulator may be designed only after separate approval.
- It must remain a simulator and must not place paper orders through a broker, exchange, webhook, scheduler, daemon, or network process.

Phase 6: broker integration only after separate future protected approval.

- Broker integration is out of scope for this proof packet.
- Any future broker work requires a new protected packet, explicit approval authority, validator chain, secret handling plan, rollback/stop condition, and live-trading blocker review.

## Core Modules

Strategy definition:

- Captures strategy name, market pair assumptions, indicator parameters, entry and exit rules, and risk settings.
- Produces structured local configuration only.

Market-data fixture schema:

- Defines local fixture files for candles, timestamps, symbols, spreads, and test metadata.
- Requires deterministic fixture versioning and validation.

Signal engine:

- Converts a strategy definition and local fixture data into deterministic signal outputs.
- Emits signals as evidence for backtesting, not executable orders.

Backtest engine:

- Replays local fixtures through the signal engine and computes deterministic performance outputs.
- Must run without network access, broker calls, credentials, webhooks, schedulers, or daemons.

Risk gate:

- Reviews strategy settings, data completeness, backtest output, drawdown assumptions, and approval state.
- Blocks unsafe or incomplete candidates before any simulator or execution stage.

Paper ledger simulator:

- Models a local ledger for hypothetical fills, balances, realized/unrealized profit and loss, and drawdown.
- It is not paper order execution and must not connect to a broker or exchange.

Dashboard status:

- Surfaces phase, strategy, fixture, backtest, risk, permission, blocker, SOS, and next-action fields.
- Must make non-live status visible.

SOS blocker reporting:

- Reports any forbidden boundary request, missing approval, unsafe risk state, invalid fixture, nondeterministic test result, or blocked escalation.
- Must preserve operator approval authority for protected actions.

## Quality Gates

- Deterministic tests are required for every implementation phase.
- No network access.
- No secrets, credentials, or env reads or writes.
- No broker integration.
- No OANDA/live exchange integration.
- No live orders.
- No paper orders unless separately approved later.
- No webhooks.
- No scheduler or daemon execution.
- Explicit human approval is required before every protected escalation.
- Tests must fail if a roadmap candidate allows broker, live trading, credentials, orders, webhooks, scheduler, daemon, or network access.
- Any implementation packet must name allowed paths, forbidden paths, validator chain, stop point, and final report format.

## Dashboard Fields

- `current_phase`
- `selected_strategy`
- `data_fixture_status`
- `backtest_status`
- `risk_gate_status`
- `paper_live_permission_state`
- `current_blocker`
- `sos_required`
- `next_safe_action`

## Acceptance Criteria

- This spec exists at `docs/trading_lab/AIOS_FOREX_BUILDER_SPEC.md`.
- The spec names every forbidden boundary in the non-live boundary section.
- The spec lists the staged roadmap from Phase 0 through Phase 6.
- The spec preserves non-live-only status.
- The roadmap tests validate that the next candidate remains `PKT-AIOS-FOREX-BUILDER-CANONICAL-SPEC`.
- The roadmap tests validate that the canonical spec candidate points to this spec path.
- The roadmap tests validate that broker integration, OANDA/live exchange integration, live orders, credentials/secrets/env reads/writes, webhooks, scheduler/daemon execution, real-money trading, account mutation, and network market automation remain forbidden.
- The roadmap tests validate that every roadmap candidate remains non-live only and denies broker, live trading, credentials, orders, webhooks, scheduler, daemon, and network access.
