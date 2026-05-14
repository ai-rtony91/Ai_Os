# Telemetry Replay Engine

AI_OS can reconstruct runtime state from the telemetry ledger.

## Purpose

The replay engine allows AI_OS to recover after restart, interruption, crash, or operator reconnect.

## Replay Inputs

Default ledger:

```text
telemetry/work_ledger.jsonl
```

Each line is parsed as one telemetry event.

## Reconstructed State

The replay engine rebuilds:

- packet state
- approval state
- blocked packet registry
- applied packet registry
- event counts
- invalid line counts

## Replay Flow

1. Read telemetry ledger
2. Parse JSON lines
3. Ignore blank lines
4. Count invalid lines
5. Replay events in order
6. Rebuild runtime state maps
7. Restore dispatcher awareness

## Recovery Goals

After replay, AI_OS should know:

- which packets are waiting approval
- which packets were blocked
- which packets already applied
- which approvals exist
- latest known packet state

## Safety Rules

- Replay must not auto-apply packets
- Replay restores awareness only
- Invalid ledger lines are counted but skipped
- Missing ledger file returns empty runtime state
- Replay order follows ledger order

## Future Extensions

- worker replay
- scheduler replay
- dead-letter replay
- approval expiration recovery
- lease recovery
