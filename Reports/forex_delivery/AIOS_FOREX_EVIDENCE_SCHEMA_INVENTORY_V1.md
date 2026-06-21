# AIOS FOREX EVIDENCE SCHEMA INVENTORY V1

## Scope

This inventory documents current evidence and replay assets relevant to the broker governance bridge before schema implementation begins.

## Existing Evidence Structures

- `automation/forex_engine/schema_contracts.py`
  - Dataclass schemas: `Candle`, `MarketDataFixture`, `StrategySignal`, `OrderIntent`, `BacktestTrade`, `BacktestResult`, `WalkForwardWindow`, `WalkForwardSummary`, `RiskGateResult`, `PaperLedgerEntry`, `DashboardState`, `DailyEdgeReport`.
  - Validation helpers enforce local/paper modes, direction/classification constraints, and no-live assertions.
- `automation/forex_engine/evidence_ledger.py`
  - Event schema with `build_ledger_event`, in-memory list ledger model, deterministic event IDs, parent-chain validation, safety envelope.
- `automation/forex_engine/session_replay.py`
  - Replay schema for paper session summaries including candidate/risk/trade/balance reconciliation checks.
- `automation/forex_engine/paper_session_replay.py`
  - Alternate paper replay summary with event counters and closed-trade PnL aggregates.
- `automation/forex_engine/paper_evidence_ledger.py`
  - Deterministic paper ledger with typed events (`candidate_created`, `risk_approved`, `paper_trade_closed`, etc.).
- `automation/forex_engine/broker_paper_dryrun_intent_ledger.py`
  - Dry-run intent ledger contracts, records, summaries, and blockers.
- `automation/forex_engine/broker_paper_dryrun_replay_harness.py`
  - Replay batch contract/result/summarization for fake local intents and risk outcomes.
- `automation/forex_engine/broker_paper_dryrun_replay_evidence_gate.py`
  - Evidence-gate result schema with thresholds and safety blockers.
- `automation/forex_engine/evidence_bundle_runner.py`, `automation/forex_engine/run_evidence_bundle_demo.py`
  - Evidence bundle composition for local paper evidence.
- `automation/forex_engine/demo_rehearsal_evidence_bundle.py`
  - Deterministic rehearsal bundle with proof fields and pass/fail safety metadata.

## Existing Evidence Files

- Evidence builders/runners: `evidence_aggregator.py`, `demo_phase_evidence_tracker.py`, `campaign_evidence_accumulator.py`, `paper_evidence_ledger.py`, `paper_forward_runner.py`, `portfolio_evidence_accumulation_runner.py`.
- Replay gate/probe scripts and demos: `run_broker_paper_dryrun_replay_harness_demo.py`, `run_broker_paper_dryrun_replay_evidence_gate_demo.py`, `run_broker_paper_adapter_plan_approval_gate_demo.py`.

## Existing Evidence Contracts

- Contract-style outputs:
  - `schema_contracts.py` global schema registry and validator functions.
  - `..._contract.py` modules in broker-paper and demo readiness space:
    - `broker_paper_adapter_stub_contract.py`
    - `broker_paper_dryrun_intent_ledger.py`
    - `broker_paper_dryrun_replay_harness.py`
    - `broker_paper_dryrun_replay_evidence_gate.py`
  - `live_review_connector_contract.py`, `demo_review_readiness_engine.py`, `live_readiness_review.py`.
- Common enforced contracts:
  - `paper_only` / `local_only` modes only
  - in-memory storage or deterministic fixtures only
  - explicit `kill_switch` / safety flags required and set false for execution-capable controls.

## Existing Replay Structures

- Event-level replay
  - `evidence_ledger.py` → `replay_ledger`
  - `session_replay.py` → `build_session_replay`
- Deterministic ledger replay
  - `paper_session_replay.py` → `build_paper_session_replay`
  - `paper_evidence_ledger.py` → `reconstruct_session_from_events`
- Demo rehearsal replay
  - `demo_rehearsal_evidence_bundle.py` calls `replay_ledger` and carries warnings/blockers.
- Broker-paper dry-run replay chain
  - `broker_paper_dryrun_replay_harness.py` → `summarize_dryrun_replay_harness`
  - `broker_paper_dryrun_replay_evidence_gate.py` → `summarize_replay_evidence_gate`.

## Schema Ownership

- Base schema and validation ownership: `automation/forex_engine/schema_contracts.py`.
- Broker-demo evidence ownership: broker-paper dry-run modules in `automation/forex_engine`.
- Orchestration/review ownership: readiness/review modules such as `live_readiness_review.py`, `demo_review_readiness_engine.py`, and `demo_validation_contract.py`.

## Schema Consumers

- Readiness evaluators and gating modules in `automation/forex_engine` consume schema records for deterministic readiness decisions.
- Replay builders consume event streams and return validation summaries (`session_id`, event counts, blocker lists, safety).
- Dashboard builders consume evidence aggregates and convert them to display-ready state (`forex_dashboard_contract.py` references).

## Schema Producers

- Dry-run intent/replay producers: broker-paper modules generate deterministic records.
- Evidence accumulation producers: `evidence_aggregator.py`, `campaign_evidence_accumulation_runner.py`, `portfolio_evidence_accumulation_runner.py`.
- Demo bundle/rehearsal producers: `demo_rehearsal_evidence_bundle.py`, `run_evidence_bundle_demo.py`.

## Governance-Relevant Notes

- No module in current codebase introduces live broker connectivity or credentials into this evidence layer.
- Safety and boundary assertions are already present and can be reused as hard constraints for new schema implementations.
