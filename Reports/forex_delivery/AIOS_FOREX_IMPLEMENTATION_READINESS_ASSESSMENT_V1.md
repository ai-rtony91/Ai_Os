# AIOS FOREX IMPLEMENTATION READINESS ASSESSMENT V1

## Executive Summary
AIOS has already built a substantial broker-demo governance layer but has not yet implemented a production-capable broker execution path. Existing work is dominated by safety-first evaluators, contract checks, evidence artifacts, and replay-safe dry-run workflows.

## 1) Existing Components

Strategy Framework
- `automation/forex_engine/strategy_candidates.py`
- `automation/forex_engine/strategy_comparison.py`
- `automation/forex_engine/strategy_evaluation_harness.py`
- `automation/forex_engine/strategy_portfolio_ranking_engine.py`
- `automation/forex_engine/strategy_portfolio_competition_runner.py`
- `automation/forex_engine/strategy_campaign_supervisor.py`

Validation Framework
- `automation/forex_engine/demo_validation_supervisor.py`
- `automation/forex_engine/demo_validation_contract.py`
- `automation/forex_engine/demo_validation_orchestrator.py`
- `automation/forex_engine/demo_validation_result_aggregator.py`
- `automation/forex_engine/demo_validation_scorecard.py`
- `automation/forex_engine/demo_review_readiness_engine.py`
- `automation/forex_engine/demo_candidate_lifecycle_manager.py`
- `automation/forex_engine/demo_phase_risk_escalation_engine.py`
- `automation/forex_engine/demo_phase_operator_review_packet.py`
- `automation/forex_engine/demo_phase_evidence_tracker.py`

Evidence Framework
- `automation/forex_engine/evidence_aggregator.py`
- `automation/forex_engine/evidence_ledger.py`
- `automation/forex_engine/campaign_evidence_accumulator.py`
- `automation/forex_engine/portfolio_evidence_accumulation_runner.py`
- `automation/forex_engine/evidence_bundle_runner.py`
- `automation/forex_engine/demo_rehearsal_evidence_bundle.py`
- `automation/forex_engine/run_evidence_bundle_demo.py`

Review & Readiness Framework
- `automation/forex_engine/review_chain_orchestrator.py`
- `automation/forex_engine/broker_demo_runtime_review.py`
- `automation/forex_engine/protected_broker_demo_connector_gate.py`
- `automation/forex_engine/protected_broker_demo_runtime_plan.py`
- `automation/forex_engine/broker_demo_connector_dry_run.py`
- `automation/forex_engine/broker_demo_connector_approval_workflow.py`
- `automation/forex_engine/live_review_connector_contract.py`
- `automation/forex_engine/live_review_readiness_certificate.py`
- `automation/forex_engine/live_candidate_readiness_spine.py`

Orchestration and Governance Runtime
- `automation/forex_engine/broker_demo_dry_run_orchestrator.py`
- `automation/forex_engine/broker_demo_runtime_connector_skeleton.py`
- `automation/forex_engine/paper_demo_broker_adapter.py`
- `automation/forex_engine/broker_paper_dryrun_replay_evidence_gate.py`
- `automation/forex_engine/broker_paper_dryrun_risk_governor.py`
- `automation/forex_engine/run_broker_paper_dryrun_replay_evidence_gate_demo.py`

Broker Demo Boundary Stack
- `automation/forex_engine/broker_demo_credential_boundary.py`
- `automation/forex_engine/broker_demo_account_boundary.py`
- `automation/forex_engine/oanda_demo_connection_gate.py`
- `automation/forex_engine/oanda_demo_connection_probe.py`
- `automation/forex_engine/oanda_demo_protected_connection_attempt.py`
- `automation/forex_engine/oanda_demo_runtime_handoff.py`
- `automation/forex_engine/oanda_demo_runtime_handoff_intake.py`
- `automation/forex_engine/oanda_demo_auth_handoff.py`
- `automation/forex_engine/oanda_read_only_client.py`

Dashboard / Readiness Projections
- `automation/forex_engine/forex_dashboard_contract.py`
- `automation/forex_engine/readiness.py`
- `automation/forex_engine/paper_risk_governor.py`
- `automation/forex_engine/portfolio_optimization.py`

## 2) Existing Broker-Facing Interfaces

- OANDA connection gate/probe/attempt functions and contracts in `oanda_demo_connection_gate.py`, `oanda_demo_connection_probe.py`, `oanda_demo_protected_connection_attempt.py`.
- Oanda runtime handoff intake and routing contracts in `oanda_demo_runtime_handoff.py` and `oanda_demo_runtime_handoff_intake.py`.
- Generic broker-demo orchestration entry points in `broker_demo_*` evaluator modules.
- No completed production broker call adapter exists yet in the runtime path reviewed.

## 3) Existing Runtime Contracts

- Broker demo chain contracts:
  - `BROKER_DEMO_DRY_RUN_*`
  - `BROKER_DEMO_RUNTIME_REVIEW_*`
  - `BROKER_DEMO_RUNTIME_PLAN_*`
  - `PROTECTED_CONNECTOR_GATE_*`
  - `PROTECTED_RUNTIME_PLAN_*`
  - `BROKER_DEMO_CREDENTIAL_BOUNDARY_*`
  - `BROKER_DEMO_ACCOUNT_BOUNDARY_*`
- OANDA contracts:
  - `OANDA_DEMO_CONNECTION_GATE_*`
  - `OANDA_DEMO_CONNECTION_PROBE_*`
  - `OANDA_DEMO_PROTECTED_CONNECTION_ATTEMPT_*`
- Readiness contracts:
  - `LIVE_REVIEW_CONNECTOR_CONTRACT_*`
  - `LIVE_REVIEW_READINESS_CERTIFICATE_*`

## 4) Existing Schemas

- Core simulation/result schemas in `automation/forex_engine/schema_contracts.py`:
  - `Candle`, `MarketDataFixture`, `StrategySignal`, `OrderIntent`
  - `BacktestTrade`, `BacktestResult`, `WalkForwardWindow`, `WalkForwardSummary`
  - `RiskGateResult`, `PaperLedgerEntry`, `DashboardState`, `DailyEdgeReport`
- Enforced validators:
  - mode restrictions (`PAPER_ONLY`, `LOCAL_ONLY`)
  - `assert_no_live_permissions` checks at schema level
- OANDA boundary/evidence schemas with explicit forbidden field rules and safe-capability fields.

## 5) Existing Governance

- Mandatory fail-closed defaults.
- Aliased status and field handling.
- Explicit proof requirements (`approval`, `replay`, `kill_switch`, `rollback`, `reconciliation`, `final_disarm`).
- Operator ownership and manual arming requirements in many evaluators.
- Hard-blocked capabilities:
  - network
  - broker SDK/runtime execution
  - credentials/logging
  - account identifier persistence
  - order routing/modification/cancel
  - live trading

## 6) Implementation Gaps

- Missing production connector runtime implementation for governed broker calls.
- Missing end-to-end handoff from governance-ready state to approved runtime execution boundary.
- No approved secret/credential bootstrap path implemented in the demo runtime lane.
- No account metadata access in runtime path (except boundary-only metadata proofs).
- No replayable operational state machine for protected micro-order execution.

## 7) Dependency Map
- Strategy and validation outputs feed demo validators and readiness engines.
- Demo validation/review outputs feed connector gate, runtime plan, and dry-run orchestration.
- Dry-run and boundary evaluators now feed OANDA gate/probe/attempt preflight contracts.
- OANDA preflight contracts currently stop before account state, market data, and execution actions.
- Dashboard and evidence ledgers consume paper-ready state; live/trade state remains blocked.

## 8) Blockers Before Read-Only Demo Probe
- No sanctioned broker transport is implemented for runtime probe execution.
- No external auth boundary has been connected through a production-safe, human-reviewed runtime connector.
- No evidence-handoff orchestration contract for probe request scheduling and response ingestion.
- No API sandbox contract binding with deterministic replay hash chain.

## 9) Blockers Before No-Order Connector
- No protected no-order connector class that consumes all boundary proofs and emits only immutable no-order telemetry.
- No integration of review-chain outputs into runtime connector skeleton in a productionized manner.
- No cross-module dependency contract proving replayable operator approval + kill-switch + rollback for connector operation.

## 10) Blockers Before Protected Demo Order Path
- No runtime executor for order intent that is already constrained by kill-switch/replay/reconciliation/final disarm.
- No deterministic candidate-to-intent-to-connector bridge in code with policy and evidence locks.
- No approved micro-order envelope transport, replayability trace, and immutable terminal reconciliation handoff.
