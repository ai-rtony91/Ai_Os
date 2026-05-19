# Dead Letter Queue (DLQ)

AI_OS isolates repeatedly failing or unsafe packets into a dead letter queue.

## Purpose

The DLQ protects dispatcher stability by preventing infinite retry loops and isolating poison packets.

## Packet Categories

### Retryable Packets

Retryable packets may safely retry within retry limits.

### Poison Packets

Poison packets exceed retry limits or are marked unsafe.

These require explicit operator review.

## DLQ Fields

- `packetId`
- `reason`
- `failureCount`
- `lastFailedAt`
- `retryable`
- `source`

## Retry Rules

- Retryable packets may re-enter scheduling
- Retry budgets prevent infinite loops
- Poison packets remain isolated
- Approval gating remains enforced

## Recovery Goals

The DLQ supports:

- failure isolation
- autonomous retries
- poison packet containment
- recovery workflows
- operator investigation

## Safety Rules

- DLQ packets must not auto-apply
- Poison packets require manual review
- Retry limits must remain bounded
- Retry actions must preserve approval state

## Future Extensions

- retry backoff policies
- automatic quarantine
- packet diagnostics
- replay-assisted recovery
- scheduler retry orchestration
