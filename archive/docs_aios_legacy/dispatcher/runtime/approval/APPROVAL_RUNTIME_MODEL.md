# Approval Runtime Model

The approval runtime keeps AI_OS APPLY work human-controlled.

Workers may inspect, plan, and report during DRY_RUN. Workers must not edit files until a human approves an APPLY request with exact scope.

## Runtime Flow

1. Worker completes DRY_RUN.
2. Worker submits approval evidence.
3. Approval request enters `REQUESTED`.
4. Operator reviews request and evidence.
5. Request moves to `APPROVED`, `BLOCKED`, `REJECTED`, `EXPIRED`, or `REVIEW_REQUIRED`.
6. APPLY may start only when approval is `APPROVED` and still matches the current packet, lock, validator, and file list.

## Human Approval Gates

Human approval is required before:

- APPLY
- commit packaging approval
- commit
- push
- override of stale approval, stale lock, or validator warning

## Blocking Conditions

APPLY is blocked when:

- approval is missing
- approval is stale
- approval does not bind to the current packet
- approval does not bind to the current worker
- files expected to change differ from files approved
- blocked paths appear in the request
- protected root files appear without explicit approval
- validator evidence is missing or failed
- lock evidence is missing, stale, or overlapping
- dirty repo state is unreviewed

## Status Meaning

- `REQUESTED`: worker submitted an approval request.
- `WAITING_REVIEW`: request is ready for human review.
- `APPROVED`: human approved exact APPLY scope.
- `BLOCKED`: request cannot proceed.
- `REJECTED`: human rejected the request.
- `EXPIRED`: request timed out or became stale.
- `REVIEW_REQUIRED`: human review is needed before any next step.

Every record must include `next_safe_action` so the operator knows the safest next command or review step.

