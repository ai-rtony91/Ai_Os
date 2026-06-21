# AIOS FOREX CONNECTOR RUNTIME HANDOFF ORCHESTRATION DESIGN V1

## 1) Current Governance Chain

- Demo Validation Supervisor
- Demo Validation Contract
- End-to-End Journey
- One-Shot Exception Assembler
- Live Review Readiness Certificate
- Review Chain Orchestrator
- Live Review Connector Contract
- Broker Demo Runtime Connector Skeleton
- Broker Demo Runtime Review
- Protected Broker Demo Connector Gate
- Broker Demo Connector Approval Workflow
- Protected Broker Demo Runtime Plan
- Broker Demo Connector Dry Run
- Broker Demo Dry-Run Orchestrator
- Credential Boundary
- Account Boundary
- Endpoint Mode Proof
- No-Order Connector Design
- Read-Only Probe Plan
- Order Intent Dry Run
- Protected Demo Micro Order Review

Current chain is deterministic and fail-closed, with readiness blockers and safety-only outputs (`broker_connection_allowed=False`, `credentials_allowed=False`, `order_execution_enabled=False`, `live_ready=False`).

## 2) Future Handoff Chain

1. Intent envelope is produced by dry-run review.
2. Intent review and protected review status are required.
3. Readiness bundle is built from:
   - boundary proofs
   - kill-switch proof
   - replay proof
   - rollback proof
   - reconciliation proof
   - final disarm proof
4. Connector runtime handoff request is formed only when all readiness gates are met.
5. Handoff is passed to an external, operator-controlled runtime environment.
6. Attempt remains "attempt-ready" state until execution approval is explicitly present.
7. Post-handoff artifacts are persisted as immutable evidence edges:
   - preflight evidence
   - blocked attempt evidence
   - attempt result evidence
8. No transition can occur directly to execution without explicit operator approval packet and all halts cleared.

## 3) Source Artifacts Consumed

- `AIOS_FOREX_BROKER_DEMO_IMPLEMENTATION_PLAN_V1`
- `AIOS_FOREX_BROKER_DEMO_CREDENTIAL_BOUNDARY_V1_REPORT`
- `AIOS_FOREX_BROKER_DEMO_ACCOUNT_BOUNDARY_V1_REPORT`
- `AIOS_FOREX_BROKER_DEMO_ENDPOINT_MODE_PROOF_V1`
- `AIOS_FOREX_BROKER_DEMO_NO_ORDER_CONNECTOR_IMPLEMENTATION_V1`
- `AIOS_FOREX_BROKER_DEMO_READ_ONLY_PROBE_PLAN_V1`
- `AIOS_FOREX_BROKER_DEMO_ORDER_INTENT_DRY_RUN_V1`
- `AIOS_FOREX_PROTECTED_DEMO_MICRO_ORDER_REVIEW_V1`
- `AIOS_FOREX_PROTECTED_DEMO_MICRO_ORDER_EXECUTION_PACKET_V1`
- `AIOS_FOREX_IMPLEMENTATION_BACKLOG_V1`

## 4) Required Approvals

Before handoff state transition:
- Credential boundary review complete
- Account boundary review complete
- Connector approval workflow review packet approved
- Protected connector gate approved
- Runtime plan approved
- One-shot + kill-switch + rollback + reconciliation + final disarm evidence ready
- Endpoint mode proof indicates demo/practice mode

## 5) Required Evidence

- Preflight evidence record
- Intent record (correlation id, strategy id, candidate id, risk summary)
- Review record (decision, blocker list)
- Approval record (operator + scope + timestamp)
- Readiness record (status family, freshness, replay proof, kill-switch proof)
- Handoff transfer log (source hash, destination id, schema version)
- Attempt result (if executed in a future packet; not in this phase)

## 6) Readiness Gates

- Missing upstream required status -> `BLOCKED`
- Missing approval signatures -> `BLOCKED`
- Missing freshness/timeout -> `EXPIRED`
- Any unsafe flag detected (credential exposure, account id evidence, order routing, network auth, live mode, execution authority) -> `BLOCKED`
- Replay trace mismatch -> `BLOCKED`
- Any unknown transition -> `BLOCKED`

## 7) Kill-Switch Checkpoints

- Preflight: verify kill-switch required and armed
- Pre-handoff: if kill-switch active, deny handoff and emit blocked attempt evidence
- Handoff acceptance: record kill-switch state in evidence
- Intra-handoff: halt propagation if kill-switch transitions active
- Post-attempt: require final disarm signal before terminalization

## 8) Replay Requirements

- Deterministic correlation IDs and canonical timestamps per step
- Idempotency: repeated identical packets should produce duplicate-safe blocked/replay status and same decision
- Replay inputs include upstream status hashes + proof references
- Replay output must include:
  - blockers
  - decision
  - next-safe-action
  - evidence references

## 9) Denied Transitions

- Intent directly to attempt without review
- Review approved false -> attempt request
- Intent status expired -> attempt
- Replay or freshness proof missing -> attempt
- Live endpoint selected -> attempt
- Any account-id or credential payload path -> attempt
- Any order operation path requested -> attempt
- Unapproved execution authority -> attempt
- Missing final disarm -> terminalization

## 10) Failure Containment

- Fail-closed at every transition
- Do not mutate state that cannot be reconciled
- Record deterministic blocked-attempt evidence for every hard deny
- Preserve audit immutability before retry policy can be considered
- Keep all future execution attempts outside this phase and outside repo scope
