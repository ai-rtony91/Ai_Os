# AIOS FOREX Broker Demo Order Intent Dry-Run V1

## Purpose
Define how AIOS represents and governs trading intent before any broker-facing action exists.

## Intent Lifecycle
- `INTENT_DRAFT`: intent fields assembled, not yet reviewed.
- `INTENT_UNDER_REVIEW`: mandatory review packet has started.
- `INTENT_APPROVED`: all review gates pass, still dry-run only.
- `INTENT_REJECTED`: validation or governance failed.
- `INTENT_EXPIRED`: time window elapsed or context stale.
- `INTENT_REVOKED`: approval withdrawn before execution path.

## Intent Creation
- Intent is created only from planning inputs.
- No broker call, no credentials, no account identifier, no network side effects.
- Fields are sanitized and non-sensitive.
- Candidate metadata is static and explicitly replayable.

## Intent Review
- Review consumes plan-bound evidence (strategy, risk, governance, readiness).
- Reviewer checks consistency across strategy identifier, candidate identifier, and policy envelope.
- No live/demo execution action is invoked in review.

## Intent Approval
- Approval status may only move to `approved`, `approved_with_conditions`, `rejected`, or `deferred`.
- Approval requires explicit operator path and documented lane authority.
- Expired or revoked approvals cannot be interpreted as valid.

## Intent Rejection
- Rejection reasons are explicit and persisted as replayable evidence.
- Rejection blocks downstream execution-path review progression.

## Intent Expiration
- Timestamp and review-window are enforced.
- Expired intent returns to draft or terminal rejection state.
- Expired/revoked state cannot be auto-recovered without manual re-creation and review.

## Intent Replay
- Every intent record includes a deterministic replay token:
  - packet id
  - strategy identifier
  - candidate identifier
  - evidence hash (policy and validation references)
  - status transition history
- Replay only validates evidence and governance history; no external calls are made.

## Intent Auditability
- Audit records include:
  - timestamp
  - strategy identifier
  - candidate identifier
  - governance status
  - approval status
  - rejection / expiration reason when present
- Logs are planning-only and contain no account ids or credentials.

## Required Intent Fields
- `timestamp`
- `strategy_identifier`
- `candidate_identifier`
- `risk_assessment`
- `position_sizing_summary`
- `stop_loss_summary`
- `take_profit_summary`
- `governance_status`
- `approval_status`

## Prohibited in this packet
- broker connectivity
- account identifiers
- credentials
- order placement
- order modification
- order cancellation

## Failure Cases
- **stale intent**: elapsed expiry window or timestamp mismatch -> `INTENT_EXPIRED`
- **duplicate intent**: same strategy/candidate in active state -> deduplicated block, no duplicate progression
- **conflicting intent**: conflicting candidate/time/risk envelope -> review halt
- **revoked approval**: prior approval invalidated -> `INTENT_REVOKED`
- **expired review**: review window expired before decision -> `INTENT_EXPIRED`
