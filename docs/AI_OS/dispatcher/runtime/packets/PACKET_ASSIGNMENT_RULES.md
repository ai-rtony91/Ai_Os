# Packet Assignment Rules

## Purpose

Packet assignment rules help AI_OS choose the next safe packet without launching uncontrolled worker activity.

This is a planning scaffold only. It does not implement executable assignment logic.

## Assignment Preconditions

A packet can be assigned only when:

- status is `QUEUED`
- worker has no active packet
- `allowed_paths` are present
- `blocked_paths` are present
- no path conflict exists
- no stale lock blocks the packet
- repo state does not block the packet
- packet mode is `DRY_RUN`, or APPLY has explicit human approval

## One Packet Per Worker

Each worker receives one active packet at a time.

If a worker already has `ASSIGNED`, `DRY_RUN_STARTED`, `APPROVAL_REQUIRED`, `APPLY_RUNNING`, `BLOCKED`, or `REVIEW_REQUIRED` work, do not assign another packet.

## Selection Order

Recommended next packet selection:

1. Highest priority safe packet.
2. Oldest safe packet at that priority.
3. Packet matching an idle worker role.
4. Packet with no path conflicts.
5. Packet with validation steps available.

If no safe packet exists, queue state becomes `REVIEW_REQUIRED` or `BLOCKED`.

## Status Flow

Normal DRY_RUN flow:

1. `QUEUED`
2. `ASSIGNED`
3. `DRY_RUN_STARTED`
4. `DRY_RUN_COMPLETE`
5. `APPROVAL_REQUIRED`

Exception flow:

- `BLOCKED` when the issue is known and has a next action.
- `REVIEW_REQUIRED` when state is unknown, unsafe, stale, or conflicting.

## Manual Approval Boundary

Assignment may recommend work.

Assignment must not:

- approve APPLY
- run APPLY
- stage files
- commit
- push
- clean dirty files
- override stale locks
- resolve unknown state automatically

## Completion Reporting

Each worker completion report should include:

- packet ID
- worker ID
- final status
- files inspected
- files created
- files changed
- validations run
- errors
- unknowns
- approval needed
- next safe action

## Next Safe Action

If packet assignment is safe, assign exactly one packet to exactly one worker in DRY_RUN mode.
