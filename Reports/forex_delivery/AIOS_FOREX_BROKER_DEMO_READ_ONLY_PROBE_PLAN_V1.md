# AIOS FOREX Broker Demo Read-Only Probe Plan V1

## Purpose
Define a future read-only probe packet that observes sandboxed state only, with no trading or account mutation.

## Probe Characteristics
- No trading action.
- No order activity.
- No account modification.
- No risk parameter mutation.
- No credential access.
- No network execution in this packet layer.

## Governance
- Probe can exist only after:
  - Credential Boundary
  - Account Boundary
  - Endpoint Mode Proof (DEMO only)
- Probe must be review-only and dry-run constrained.
- Probe requires explicit operator review and manual arming.
- Probe inherits kill-switch and final-disarm requirements from upstream chain.

## Approval Path
1. Submit as planning packet in governed lane.
2. Reviewer validates read-only scope and blocked trading actions.
3. Evidence reviewer checks replay + audit linkage.
4. Runtime behavior remains unchanged (no behavior introduced).

## Observability
- Endpoint selection trace
- Probe boundary proof checklist
- Replay artifact (fixed order of observations)
- Deny/allow decision log
- Time-window and owner metadata

## Replay Requirements
- Probe outputs must be reproducible from packet inputs only.
- Replay token includes versioned packet identifiers and evidence references.
- Replay failure requires forced re-approval before re-run.

## Evidence Requirements
- Proof that endpoint mode is DEMO.
- Proof that no credentials/accounts/orders are accessed.
- Proof that no API/network calls are represented.
- Proof that kill-switch/final-disarm controls remain active.
- Proof of no order/risk/account mutation.

## Kill-Switch Interaction
- Kill-switch stays armed during planning and evidence composition.
- Any deviation to mutable behaviors triggers kill-switch escalation and packet block.
- Probe must include explicit post-failure rollback plan referencing previous approved packet state.

## Rollback Procedures
- On policy drift, move packet to `BLOCKED` and require redesign under same plan-only constraints.
- On evidence deficiency, require `PLAN_EVIDENCE_REPAIR` and do not advance chain.
- On governance mismatch, reset to `Read-Only Probe Plan` draft and rerun approval.
