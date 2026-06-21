# AIOS FOREX Protected Demo Micro-Order Review V1

## Purpose
Define the mandatory human-governed review process before any future protected demo micro-order execution could be attempted.

## Review Requirements

### Candidate Validation
- Verify strategy/candidate identifiers are explicit and non-duplicative.
- Verify deterministic context: timestamp, candidate metadata, and policy scope are complete.
- Validate candidate scope against read-only milestone constraints.

### Expectancy Validation
- Validate expected outcome envelope exists for the candidate.
- Confirm all assumptions are documented and bounded.
- Reject unverifiable expectancy claims without evidence.

### Drawdown Validation
- Verify risk summary includes bounded drawdown guardrails.
- Ensure no implicit risk amplification assumptions exist.

### Risk Validation
- Validate one-shot intent envelope and risk controls.
- Confirm no order routing fields are present in this stage.
- Confirm kill-switch and disarm constraints are attached.

### Governance Validation
- Validate governance readiness chain includes:
  - endpoint mode proof (DEMO-only)
  - no-order connector design constraints
  - read-only probe planning context
- Confirm no credential/account artifacts were introduced.

### Readiness Validation
- Confirm required reviewers and approvals are present.
- Confirm replay evidence references are present.
- Confirm no pending unsafe states remain.

## Approval Outcomes
- `approved`
- `approved_with_conditions`
- `rejected`
- `deferred`

## Required Evidence
- strategy evidence
- validation evidence
- review evidence
- approval evidence
- replay evidence

## Kill-Switch Requirements
- **review halt**: any failed validation triggers review-stop
- **execution halt**: execution cannot proceed from this packet stage
- **governance halt**: any governance violation blocks advancement
- **emergency halt**: immediate block if unsafe state or policy conflict appears

## Audit Requirements
- Persist review decision with:
  - reviewer identity
  - timestamp
  - status outcome
  - cited evidence IDs
  - escalation path if rejected/deferred
- Audit must include explicit proof of no broker connectivity, no credential usage, no account usage, and no execution behavior.

## Rollback Requirements
- Rejection or deferred outcome returns workflow to safe planning state.
- Revoked approvals require explicit re-authorization packet.
- Expired review evidence requires regenerated replay packet and renewed review.

## Escalation Requirements
- Escalate to `operator_review` when validation failures are policy-safe but recoverable.
- Escalate to `safety_pause` when any kill-switch or governance hard-stop condition appears.
- Escalate to `chain_block` when a hard constraint is violated (e.g., prohibited action attempted in scope).

## Replay Requirements
- Every review packet stores deterministic replay metadata:
  - strategy/candidate pair
  - decision path
  - evidence hashes
  - reviewer outcome rationale
- Replay must return same outcome under unchanged evidence set.
