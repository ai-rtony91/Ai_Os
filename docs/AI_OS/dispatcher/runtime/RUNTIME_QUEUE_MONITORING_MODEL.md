# Runtime Queue Monitoring Model

Queue monitoring tells the operator whether work can start, continue, pause, or needs review.

The queue monitor does not replace packet, worker, lock, or heartbeat source-of-truth files.

## Inputs

The queue monitor reads:

- packet runtime table
- active worker table
- lock runtime table
- worker heartbeat table
- approval runtime status
- validator runtime status
- recovery runtime status
- git status summary

## Output

Recommended summary:

`Reports/dispatcher/runtime/queue_monitoring/queue_health_summary.json`

This file is summary only.

## Queue Health States

Use simple states:

- `READY`
- `BUSY`
- `WAITING_FOR_APPROVAL`
- `VALIDATION_REQUIRED`
- `REVIEW_REQUIRED`
- `BLOCKED`

## Duplicate Concept Control

Packet queue means work waiting to be assigned.

Packet runtime table means packet truth after creation or assignment.

Active worker table means current worker ownership.

Queue health summary means operator-readable condition.

These should not be merged into one oversized file.

## Stale Queue Handling

If a queued packet points to a missing worker, invalid path, stale lock, or missing approval, the queue health must become `REVIEW_REQUIRED`.

