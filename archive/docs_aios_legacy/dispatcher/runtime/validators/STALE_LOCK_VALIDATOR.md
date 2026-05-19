# Stale Lock Validator

## Purpose

This validator identifies locks that may be old, orphaned, or unsafe to override.

It does not override locks. Lock override requires human approval.

## Inputs

Future validator inputs:

- lock id
- lock owner
- locked paths
- lock created time
- last heartbeat time
- active worker list
- current package allowed paths

## PASS Logic

Return `PASS` when:

- the lock is current
- the lock owner is active
- the lock does not overlap another worker package

## FAIL Logic

Return `FAIL` when:

- lock status cannot be read
- lock time cannot be parsed
- locked path data is malformed

## BLOCKED Logic

Return `BLOCKED` when:

- a stale lock overlaps the current package
- the lock owner is stale and owns uncommitted work
- the lock protects blocked or protected paths
- override approval is missing

## REVIEW_REQUIRED Logic

Return `REVIEW_REQUIRED` when:

- the lock is stale but ownership is unclear
- the lock is old but the owner may still be active
- locked paths overlap allowed paths
- recovery requires operator judgment

## Example

Lock:

`runtime-validator-docs-lock`

Locked paths:

- `docs/AI_OS/dispatcher/runtime/validators/`
- `Reports/dispatcher/runtime/validators/`

Finding:

`last_heartbeat_age_minutes` is `120`

Result:

`REVIEW_REQUIRED`

Reason:

The lock overlaps this package and must not be overridden automatically.

## Next Safe Action Examples

- `Review lock owner before override.`
- `Do not override stale lock without human approval.`
- `Stop package routing until overlapping lock is resolved.`

