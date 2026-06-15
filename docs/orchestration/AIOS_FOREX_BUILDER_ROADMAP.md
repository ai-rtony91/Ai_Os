# AIOS Forex Builder Roadmap Candidate Source

Schema: `AIOS_FOREX_BUILDER_ROADMAP_CANDIDATE_SOURCE.v1`

This contract emits safe, local candidate packet evidence for the AIOS self-building loop after completed-packet memory suppresses already-landed infrastructure packets.

Today goal alignment:

`AIOS self-building machine -> first proof target: industrial-grade forex trading bot builder -> specs, schemas, simulation, backtesting, risk policy, and dashboard/reporting scaffolds only`

## Contract Fields

- `schema`
- `roadmap_status`
- `today_goal_alignment`
- `roadmap_candidates`
- `candidate_packets`
- `candidates`
- `forbidden_lanes`
- `next_recommended_candidate`
- `commands_executed`
- `files_written`
- `workers_dispatched`
- `queues_mutated`
- `approvals_mutated`
- `safety`
- `next_safe_action`

`candidate_packets` and `candidates` intentionally mirror `roadmap_candidates` so the output can be passed directly to the candidate evidence adapter or packet queue planner.

## Ordered Candidates

1. `PKT-AIOS-FOREX-BUILDER-CANONICAL-SPEC`
   - Lane: `forex-builder-spec`
   - Purpose: define the canonical product requirements, safety boundaries, non-live phases, and quality gates.

2. `PKT-AIOS-FOREX-BUILDER-DATA-SCHEMAS`
   - Lane: `forex-builder-data-schemas`
   - Purpose: define local fixture schemas for market data, signals, orders-as-intent, backtest outputs, and paper ledger records.

3. `PKT-AIOS-FOREX-BUILDER-BACKTEST-HARNESS`
   - Lane: `forex-builder-backtest`
   - Purpose: create a deterministic backtest harness scaffold using local fixtures only.

4. `PKT-AIOS-FOREX-BUILDER-RISK-CONTRACT`
   - Lane: `forex-builder-risk-policy`
   - Purpose: define risk gates before any paper or live execution work.

5. `PKT-AIOS-FOREX-BUILDER-DASHBOARD-CONTRACT`
   - Lane: `forex-builder-dashboard`
   - Purpose: define dashboard fields for strategy status, backtest result, risk gate, paper state, and SOS blockers.

The default `next_recommended_candidate` is `PKT-AIOS-FOREX-BUILDER-CANONICAL-SPEC`.

## Forbidden Lanes

The roadmap source blocks these boundaries:

- broker integration
- OANDA/live exchange integration
- live orders
- paper orders unless separately approved
- credentials/secrets/env reads/writes
- webhooks
- scheduler/daemon execution
- real-money trading
- account mutation
- network market automation

## Safety

This module is evidence-only. It does not write files, execute commands, launch Codex, dispatch workers, mutate queues, mutate approvals, use network access, touch credentials, place orders, call webhooks, start schedulers, or start daemons.

Validation:

```powershell
python -m pytest -p no:cacheprovider tests/orchestration/test_aios_forex_builder_roadmap.py -q
```
