# Phase 16 Trading Stack Control Room

## Purpose

Phase 16 defines the paper-only Trading Stack Control Room architecture.

The control room is a dashboard-ready summary of the local paper workflow:

1. Signal Queue
2. Validation Queue
3. Paper Bot Status
4. Safety Boundary
5. Runtime Workflow
6. Next Safe Action

## Boundary

This phase is local-only and paper-only.

- live_execution_status: BLOCKED
- broker_status: BLOCKED
- oanda_status: BLOCKED
- api_key_status: BLOCKED
- secrets_status: BLOCKED
- real_webhook_status: BLOCKED
- real_order_status: BLOCKED

## Current Control Room Status

Status: CONTROL_ROOM_REVIEW

Reason:
- The paper bot runner exists.
- The strategy ranking is blocked for replay review.
- Clock skew remains unresolved.
- Readiness is not approved for any live path.

## Sections

### Signal Queue

Shows local fixture signal intake status.

### Validation Queue

Shows validator readiness and replay review status.

### Paper Bot Status

Shows the latest paper runner decision and scorecard state.

### Safety Boundary

Shows that live execution, brokers, credentials, webhooks, and real orders remain blocked.

### Runtime Workflow

Shows the local queue path from intake through validation and review.

### Next Safe Action

Shows the next paper-only step for the user.

## Next Safe Action

Review the timestamp mismatch from the replay result, then rerun paper-only validation before expanding dashboard UI wiring.
