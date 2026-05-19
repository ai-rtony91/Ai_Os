# Autonomous Scheduler Engine

AI_OS can generate runtime scheduling plans using replay, recovery, DLQ, and worker lease intelligence.

## Purpose

The scheduler coordinates:

- resumable packets
- retryable packets
- approval waits
- reclaimable packets
- poison packets

into a unified orchestration plan.

## Scheduler Inputs

The scheduler consumes:

- replay recovery plans
- dead letter queue state
- worker lease state
- concurrency limits

## Action Types

- `dispatch`
- `wait_for_approval`
- `resume_dry_run`
- `retry`
- `manual_review`

## Priority Rules

Highest priority:

```text
manual_review
```

Lowest priority:

```text
dispatch
```

## Scheduler Goals

The scheduler attempts to:

- prevent duplicate work
- avoid unsafe auto-apply behavior
- reclaim abandoned packets
- retry safe failures
- isolate poison packets
- preserve approval safety
- maximize runtime continuity

## Concurrency Control

The scheduler respects:

```text
maxConcurrentPackets
```

This limits simultaneous packet operations.

## Recovery Awareness

The scheduler integrates with:

- telemetry replay
- runtime rebuilding
- packet resume plans
- worker lease recovery
- DLQ retry logic

## Future Extensions

- weighted scheduling
- priority aging
- runtime backpressure
- distributed worker pools
- adaptive retry budgets
- autonomous recovery loops
