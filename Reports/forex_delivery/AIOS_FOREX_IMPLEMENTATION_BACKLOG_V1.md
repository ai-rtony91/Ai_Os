# AIOS FOREX IMPLEMENTATION BACKLOG V1

## Scope
Repository-wide remaining engineering items needed before any future governed demo broker integration.

### Item 1: Connector Runtime Handoff Orchestrator
- Purpose: wire governance-ready states into a deterministic connector orchestration runner.
- Dependency: review chain outputs, boundary proofs, protected runtime plan.
- Estimated complexity: High
- Risk level: High
- Governance impact: introduces one new control surface that must remain one-shot, fail-closed, and approval-gated.

### Item 2: OANDA Runtime Connector Adapter
- Purpose: provide a controlled external adapter entrypoint matching OANDA handoff schema.
- Dependency: connection gate/probe/attempt contracts.
- Estimated complexity: High
- Risk level: High
- Governance impact: highest risk area; hard banrails for credentials/account/network/order capabilities.

### Item 3: Secret Injection Boundary (External-Only)
- Purpose: define approved operator-injected auth handoff path outside repo storage.
- Dependency: credential boundary and account boundary modules.
- Estimated complexity: Medium
- Risk level: Critical
- Governance impact: any deviation directly violates credential boundary policy.

### Item 4: Protected Demo Connector Approval Pipeline
- Purpose: create explicit approval handoff artifact from human owner review to runtime attempt packet.
- Dependency: no-order and review packets, kill-switch/rollback controls.
- Estimated complexity: Medium
- Risk level: Medium
- Governance impact: controls unauthorized direct execution and unauthorized retries.

### Item 5: Broker Evidence Hash Chain and Replay Ledger Extension
- Purpose: record immutable proof edges from intent -> approval -> attempt -> terminal evidence.
- Dependency: evidence_ledger and dashboard aggregation modules.
- Estimated complexity: Medium
- Risk level: Medium
- Governance impact: improves traceability and tamper detection for future execution packets.

### Item 6: Demo Read-Only Probe Runtime Probe Harness
- Purpose: provide deterministic, non-mutating runtime probe harness for endpoint and authentication checks.
- Dependency: connection gate/probe contracts and oanda read-only client tests.
- Estimated complexity: Medium
- Risk level: Medium
- Governance impact: must remain validate-only and sanitize all telemetry.

### Item 7: Reconciliation and Terminal State Normalization for Protected Demo Attempts
- Purpose: standardize terminal result schema and post-result rollbacks for all future attempts.
- Dependency: existing reconciliation/rollback contracts in runtime review and protected plan.
- Estimated complexity: Medium
- Risk level: Medium
- Governance impact: prevents silent partial execution and unresolved terminal states.

### Item 8: Dashboard State Projection for Protected Demo Readiness
- Purpose: add explicit visibility for connector readiness, proof gaps, and blocked capabilities.
- Dependency: dashboard contract, evidence aggregator, readiness modules.
- Estimated complexity: Low
- Risk level: Low
- Governance impact: improves operator governance oversight and reduces blind paths.

### Item 9: Schema Package and Validation Parity for Demo Path
- Purpose: consolidate schema objects for order intent, connector contracts, evidence payloads, and approval traces.
- Dependency: schema_contracts and existing protocol modules.
- Estimated complexity: Medium
- Risk level: Medium
- Governance impact: reduces drift between docs and runtime contract checks.

### Item 10: Future Micro-Order Execution Packet Staging (Plan Only)
- Purpose: define exact packet that transitions from intent to protected micro-order execution after all gates.
- Dependency: protected review packet, runtime handoff, kill-switch and rollback controls.
- Estimated complexity: High
- Risk level: Very High
- Governance impact: must be gated by all no-retry/no-autonomous-reentry/no-live constraints and explicit disarm.

## Priority Bands
- P0: 2, 3, 10
- P1: 1, 4, 5, 7
- P2: 6, 8, 9

## Measurable Completion Criteria
- No remaining `PASS` gaps in assessment-only guard tests for governance modules.
- New execution packet is only approved after this backlog sequence is closed with evidence.
