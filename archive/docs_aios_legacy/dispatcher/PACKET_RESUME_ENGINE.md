# Packet Resume Engine

AI_OS can safely resume interrupted packet flows after runtime recovery.

## Purpose

The Packet Resume Engine determines how interrupted packets should continue after replay and runtime rebuilding.

## Resume Categories

### Waiting Approval

Packets waiting approval return to:

```text
wait_for_approval
```

No automatic apply occurs.

### Queued Packets

Queued packets may safely return to dispatcher scheduling.

Recommended action:

```text
requeue
```

### Approved Packets

Approved packets may resume validation or dry-run execution.

Recommended action:

```text
resume_dry_run
```

### Blocked Packets

Blocked packets require explicit operator review.

Recommended action:

```text
manual_review
```

## Safety Rules

- Replay must not auto-apply packets
- Resume must not bypass approval
- Blocked packets stay blocked
- Duplicate apply attempts must be avoided
- Resume plans are recommendations, not execution

## Recovery Flow

1. Replay telemetry ledger
2. Rebuild runtime state
3. Generate resume plan
4. Review interrupted packets
5. Resume safe operations

## Future Extensions

- retry budgets
- dead-letter queues
- worker reassignment
- lease recovery
- automatic stale packet cleanup
