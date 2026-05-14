# Stale Worker Validator

## Purpose

This validator identifies worker sessions that may no longer be active.

It does not reassign work. Stale worker reassignment requires human approval.

## Inputs

Future validator inputs:

- worker id
- worker window name
- last heartbeat time
- current time
- owned files
- active lock list
- dirty repo state

## PASS Logic

Return `PASS` when:

- the worker heartbeat is current
- the worker owns no stale lock
- the worker has no unknown dirty work

## FAIL Logic

Return `FAIL` when:

- worker status cannot be read
- heartbeat time cannot be parsed
- worker ownership data is malformed

## BLOCKED Logic

Return `BLOCKED` when:

- the worker is stale and owns locks
- the worker is stale and owns uncommitted work
- another worker attempts to take over without approval
- stale worker recovery would touch blocked paths

## REVIEW_REQUIRED Logic

Return `REVIEW_REQUIRED` when:

- heartbeat is stale but ownership is unclear
- heartbeat is stale and the worker owns files in the current package
- worker status conflicts with git status
- recovery may be safe but needs a human decision

## Example

Worker:

`WINDOW 04 - VALIDATOR ROUTING`

Finding:

`last_heartbeat_age_minutes` is `95`

Owned files:

- `docs/AI_OS/dispatcher/runtime/validators/DIRTY_REPO_VALIDATOR.md`

Result:

`REVIEW_REQUIRED`

Reason:

The worker may own current package files, so reassignment needs human review.

## Next Safe Action Examples

- `Review worker ownership before reassignment.`
- `Do not replace stale worker while it owns locks.`
- `Mark recovery as blocked until the operator approves reassignment.`

