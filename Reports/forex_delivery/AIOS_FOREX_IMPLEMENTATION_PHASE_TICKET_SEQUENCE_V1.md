# AIOS FOREX IMPLEMENTATION PHASE TICKET SEQUENCE V1

## Scope

Convert the implementation backlog into ordered engineering tickets while keeping no-broker/connectivity/credentials/account/order constraints for this phase.

## Ticket 1 — Evidence Schema Implementation
- Objective: define formal evidence schemas for intent→review→approval→readiness→attempt flow.
- Files likely affected: `automation/forex_engine` (schema layer), `Reports/forex_delivery`
- Dependencies: readiness assessment artifacts
- Safety gates: no credential/account fields, no network fields, no execution authority
- Validation command: `python -m pytest tests/forex_engine/test_schema_contracts.py -q`
- Expected artifact: versioned schema plan and validator hooks in next non-document packet
- No-broker/no-live constraint: strict
- Estimated complexity: Medium
- Implementation risk: Medium

## Ticket 2 — No-Order Connector Interfaces
- Objective: define interface boundaries and datatypes for no-order runtime connector envelope.
- Files likely affected: `automation/forex_engine` (new interface plan module), tests (deferred)
- Dependencies: Ticket 1
- Safety gates: all order operations forbidden, no execution flags
- Validation command: `python -m pytest tests/forex_engine/test_broker_demo_connector_dry_run.py -q`
- Expected artifact: interface contract module skeleton and no-order test plan
- No-broker/no-live constraint: strict
- Estimated complexity: Medium
- Implementation risk: Medium

## Ticket 3 — Endpoint Mode Verifier
- Objective: add deterministic endpoint mode verification module for demo-only routing.
- Files likely affected: broker-demo orchestration modules
- Dependencies: Ticket 2
- Safety gates: block live endpoint, unsupported endpoint class, missing environment classification
- Validation command: `python -m pytest tests/forex_engine/test_oanda_demo_connection_gate.py -q`
- Expected artifact: explicit endpoint mode verifier evidence output
- No-broker/no-live constraint: strict
- Estimated complexity: Low
- Implementation risk: Low

## Ticket 4 — Credential Provider Boundary
- Objective: formalize external-only credential boundary contract and proof expectations.
- Files likely affected: boundary evaluator interfaces
- Dependencies: Ticket 1, 3
- Safety gates: no credential values, hashes, lengths, prefixes, suffixes in repo evidence
- Validation command: `python -m pytest tests/forex_engine/test_broker_demo_credential_boundary.py -q`
- Expected artifact: boundary proof contract plan and rejection list
- No-broker/no-live constraint: strict
- Estimated complexity: Medium
- Implementation risk: High

## Ticket 5 — Account Metadata Sanitizer
- Objective: define account metadata sanitizer contract for external-only account handling.
- Files likely affected: boundary-related modules and proof utilities
- Dependencies: Ticket 4
- Safety gates: no account id values or account persistence
- Validation command: `python -m pytest tests/forex_engine/test_broker_demo_account_boundary.py -q`
- Expected artifact: account redaction contract and sanitizer checklist
- No-broker/no-live constraint: strict
- Estimated complexity: Medium
- Implementation risk: Medium

## Ticket 6 — Read-Only Probe Skeleton
- Objective: design a read-only probe workflow that cannot mutate or execute orders.
- Files likely affected: read-only probe planning docs and future interface modules
- Dependencies: Ticket 2, 3, 5
- Safety gates: validate-only mode enforced, one-shot only
- Validation command: `python -m pytest tests/forex_engine/test_oanda_demo_connection_probe.py -q`
- Expected artifact: probe interface contract and evidence schema
- No-broker/no-live constraint: strict
- Estimated complexity: Medium
- Implementation risk: Medium

## Ticket 7 — Connector Runtime Handoff Orchestrator
- Objective: orchestrate readiness -> evidence -> gated handoff without runtime execution.
- Files likely affected: orchestration modules + handoff artifacts
- Dependencies: Tickets 2, 3, 4, 5, 6
- Safety gates: kill-switch, replay, rollback, reconciliation, final disarm required
- Validation command: `python -m pytest tests/forex_engine/test_broker_demo_runtime_connector_skeleton.py -q`
- Expected artifact: orchestrator state machine design and deterministic blockers
- No-broker/no-live constraint: strict
- Estimated complexity: High
- Implementation risk: High

## Ticket 8 — Dashboard Read-Model Projection
- Objective: expose handoff/readiness evidence and halt states in dashboard output.
- Files likely affected: `automation/forex_engine/forex_dashboard_contract.py` and reports
- Dependencies: Ticket 7
- Safety gates: do not expose secrets, IDs, or live capability
- Validation command: `python -m pytest tests/forex_engine/test_forex_dashboard_contract.py -q`
- Expected artifact: read-model additions for blocked-attempt and readiness fields
- No-broker/no-live constraint: strict
- Estimated complexity: Low
- Implementation risk: Low

## Ticket 9 — Replay Ledger Binding
- Objective: bind replay references across intent-review-approval-readiness-attempt evidence chain.
- Files likely affected: evidence ledger/bundle modules
- Dependencies: Ticket 1, 7
- Safety gates: replay hash required, duplicate-safe handling
- Validation command: `python -m pytest tests/forex_engine/test_session_replay.py -q`
- Expected artifact: deterministic replay reference propagation
- No-broker/no-live constraint: strict
- Estimated complexity: Medium
- Implementation risk: Medium

## Ticket 10 — Broker Bridge Validator
- Objective: validate all handoff transitions and denied transitions before future attempts.
- Files likely affected: connector/gate/runtimereview modules
- Dependencies: Tickets 3–9
- Safety gates: denied transition matrix enforced
- Validation command: `python -m pytest tests/forex_engine/test_review_chain_orchestrator.py -q`
- Expected artifact: denied transition test matrix and final blocker map
- No-broker/no-live constraint: strict
- Estimated complexity: High
- Implementation risk: High

## Ticket 11 — Protected Demo Attempt Dry-Run
- Objective: document and later implement a dry-run-only protected attempt packet.
- Files likely affected: broker demo attempt planning modules
- Dependencies: Ticket 10
- Safety gates: no actual order execution, no endpoint call
- Validation command: `python -m pytest tests/forex_engine/test_broker_demo_dry_run_orchestrator.py -q`
- Expected artifact: attempt envelope + blocked/rejected result records
- No-broker/no-live constraint: strict
- Estimated complexity: Medium
- Implementation risk: Medium

## Ticket 12 — Final Demo-Readiness Review Packet
- Objective: consolidate all prior tickets into final engineering-readiness package.
- Files likely affected: documentation/report and release gating modules
- Dependencies: Tickets 1–11
- Safety gates: explicit no-network/no-credentials/no-account-id/no-exec assertions
- Validation command: `python -m pytest tests/forex_engine/test_broker_demo_* -q`
- Expected artifact: final readiness packet with measurable criteria
- No-broker/no-live constraint: strict
- Estimated complexity: Low
- Implementation risk: Medium
