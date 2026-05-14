# Recovery Resume Validator Rules

## Purpose

This validator protects AI_OS when work stopped in the middle of a packet, worker session, lock claim, or APPLY review.

It is docs-only in this phase. It does not resume work, reassign packets, release locks, stage files, commit, or push.

## Inputs

Future validator inputs:

- packet runtime table
- worker heartbeat table
- lock runtime table
- approval runtime status
- dirty repo validator result
- latest validator result for the packet
- interrupted APPLY evidence, if any

## PASS Logic

Return `PASS` when:

- the packet has one clear owner
- the worker heartbeat is current, or human review approved reassignment
- active locks match the packet owner and approved paths
- dirty repo state is reviewed
- interrupted APPLY evidence is complete
- the next safe action is clear and non-destructive

## FAIL Logic

Return `FAIL` when:

- required runtime JSON cannot be parsed
- packet, lock, or heartbeat records are malformed
- packet status cannot be reconciled with validator evidence

## BLOCKED Logic

Return `BLOCKED` when:

- APPLY was interrupted and changed files are unknown
- an orphan packet has no valid worker owner
- a stale lock still claims the packet paths
- a blocked path or protected root file appears in the recovery set
- resume would require commit, push, delete, move, rename, or credential changes

## REVIEW_REQUIRED Logic

Return `REVIEW_REQUIRED` when:

- the worker heartbeat is stale
- the packet is assigned but no active worker is confirmed
- the packet is complete but the lock is still active
- untracked files exist during recovery review
- the recovery action requires human approval

## Interrupted APPLY Example

```text
packet_id: PACKET-VALIDATOR-001
status: APPLY_STARTED
worker_id: AIOS-03-VALIDATOR
latest_validator_stage: pre_apply
changed_files: UNKNOWN
```

Result:

`BLOCKED`

Reason:

The validator cannot prove which files changed after APPLY started.

Next safe action:

`Stop. Review git status and packet evidence before resuming APPLY.`

## Orphan Packet Example

```text
packet_id: PACKET-DOCS-009
status: ASSIGNED
worker_id: AIOS-06-DOCS
heartbeat_status: MISSING
lock_status: ACTIVE
```

Result:

`REVIEW_REQUIRED`

Reason:

The packet has an assigned worker but no current heartbeat.

Next safe action:

`Review worker ownership before reassigning the packet or releasing the lock.`

## Human Control Rule

`REVIEW_REQUIRED` cannot self-resolve. A human must approve resume, reassignment, stale lock override, or commit packaging.
