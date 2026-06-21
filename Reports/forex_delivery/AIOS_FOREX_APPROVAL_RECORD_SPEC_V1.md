# AIOS FOREX APPROVAL RECORD SPEC V1

## Purpose

Define a non-executable approval record structure for controlled progression through governance.

## Record Identity

- `record_type`: `AIOS_FOREX_APPROVAL_RECORD_V1`
- `record_id`: deterministic unique identifier
- `correlation_id`: must match upstream intent correlation.

## Required Fields

- `timestamp` (UTC ISO-8601)
- `correlation_id`
- `strategy_id`
- `candidate_id`
- `governance_status`
- `risk_summary`
- `approval_status`
- `endpoint_mode`
- `kill_switch_state`
- `evidence_references`
- `replay_references`
- `approval_scope`
- `approval_window_expires_at`
- `manual_arming_required`
- `timeout_seconds`

## Optional Fields

- `approval_approver` (non-sensitive operator marker, no secrets)
- `approval_notes`
- `approval_conditions`
- `review_reference`
- `readiness_reference`
- `operator_risk_comment`
- `upstream_packet_id`

## Approval States

- `PENDING`
- `APPROVED`
- `APPROVED_WITH_CONDITIONS`
- `DEFERRED`
- `REJECTED`

## Expiration Rules

- `approval_window_expires_at` is required when `approval_status=APPROVED`.
- Expired approvals are invalid and must force blocked/delayed execution consideration.
- `timeout_seconds` caps the operator window for deterministic replay.
- Expired record transitions to `BLOCKED_REVIEW` and cannot be used as proof of readiness.

## Revocation Rules

- `APPROVED` records with `manual_arming_required=True` must additionally require explicit re-arming.
- Any revocation event must create a new approval revision record and mark prior record as superseded.
- Revoked approvals are hard blockers until re-issued.

## Replay Requirements

- `evidence_references` must be immutable and include replay-able proofs.
- `replay_references` must include the chain of review and readiness proofs.
- Replay of approvals must preserve:
  - decision timestamp
  - window expiry
  - revocation state

## Audit Requirements

- Every approval record must include a reasoned decision and immutable operator marker.
- All approvals must include proof of operator presence and kill-switch state consistency.
- Any unsafe flag false/true state must be explicit.
- Audit consumers shall be able to reconstruct:
  - who approved (non-PII token),
  - why approved,
  - whether approval is still valid at replay time.
