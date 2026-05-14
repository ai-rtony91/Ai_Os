# Runtime Worker Lifecycle Model

Workers do not free-roam.

Each worker follows one approved packet and one approved path list.

## Worker States

Recommended states:

- `UNASSIGNED`
- `ASSIGNED`
- `DRY_RUN_STARTED`
- `DRY_RUN_COMPLETE`
- `WAITING_FOR_APPROVAL`
- `APPLY_STARTED`
- `APPLY_COMPLETE`
- `VALIDATION_REQUIRED`
- `VALIDATED`
- `COMMIT_READY`
- `BLOCKED`
- `FAILED`
- `REVIEW_REQUIRED`

## Worker Lifecycle

1. Worker is listed in the active worker table.
2. Worker receives one packet.
3. Worker confirms allowed and blocked paths.
4. Worker claims locks before APPLY.
5. Worker sends heartbeat while active.
6. Worker completes DRY_RUN.
7. Worker waits for human approval.
8. Worker applies only approved changes.
9. Worker reports validation results.
10. Worker releases locks or marks them for review.

## Stale Worker Handling

A stale worker must not be automatically replaced if it owns locks or has uncommitted work.

The recovery reconciler should mark the worker, packet, and locks `REVIEW_REQUIRED`.

Human approval is required before reassignment.

## Worker Table Rule

Use one active worker table for current worker truth.

Use ledgers for history.

Do not create competing active worker tables.

