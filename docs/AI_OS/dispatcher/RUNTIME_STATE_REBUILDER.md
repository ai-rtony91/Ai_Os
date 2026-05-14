# Runtime State Rebuilder

AI_OS rebuilds dispatcher awareness from replayed telemetry state.

## Purpose

The Runtime State Rebuilder converts replayed telemetry into active runtime structures.

This allows AI_OS to recover queue state after:

- restart
- crash
- interrupted apply
- operator reconnect
- runtime recovery

## Inputs

The rebuilder consumes replayed telemetry state:

- packets
- approvals
- blocked packet registry
- applied packet registry
- event counts

## Rebuilt Runtime Structures

The rebuilder reconstructs:

- queued packets
- waiting approval packets
- approved packets
- blocked packets
- applied packets
- pending approvals

## Recovery Rules

- Replay restores awareness only
- Recovery must not auto-apply packets
- Blocked packets remain blocked
- Pending approvals remain pending
- Approved packets require explicit apply step
- Applied packets are treated as completed

## Recovery Flow

1. Replay telemetry ledger
2. Rebuild runtime state
3. Restore dispatcher awareness
4. Restore approval awareness
5. Detect interrupted flows
6. Resume safe operations

## Future Extensions

- worker lease rebuilding
- scheduler reconstruction
- dead-letter restoration
- stale worker cleanup
- replay checkpoints
