# AI_OS Crash Recovery

## Purpose

AI_OS crash recovery has two separate recovery layers:

- `automation/recovery/Resume-AiOsCycle.ps1` resumes the cycle from the last recorded phase in `control/cycle/last_marker.json`.
- `automation/orchestration/recovery/Reclaim-AiOsOrphans.ps1` reclaims stranded relay task packets from `relay/running/`.

The phase resume layer restarts the cycle. The orphan reclaim layer prevents the packet that was in flight during a crash from being silently lost.

## Orphan Lifecycle

The relay worker moves a task through this lifecycle:

```text
relay/inbox/ -> relay/running/ -> relay/done/
relay/inbox/ -> relay/running/ -> relay/error/
```

If the worker or machine dies while a task is in `relay/running/`, the task can remain there indefinitely. `Reclaim-AiOsOrphans.ps1` scans `relay/running/` for `*.task.json` files older than `OrphanMinutes`.

Decision table:

```text
fresh task                                leave in relay/running/
aged task with reclaim_count < MaxRetries move to relay/inbox/
aged task with reclaim_count >= MaxRetries move to relay/error/
corrupt or unreadable task                move to relay/error/
empty running folder                      NO_ORPHANS, success
```

## Retry Cap

`MaxRetries` defaults to `3`. Each reclaim to `relay/inbox/` increments `reclaim_count` and stamps `reclaimed_at_utc`. Once a task reaches the retry cap, it moves to `relay/error/` with:

```text
reclaim_reason = ORPHAN_MAX_RETRIES
```

This prevents infinite auto-retry loops while preserving the task for inspection.

## Corrupt Tasks

If a task file cannot be parsed as JSON, reclaim wraps the raw content in a JSON error record and moves it to `relay/error/` with:

```text
reclaim_reason = ORPHAN_UNREADABLE
```

The sweep continues after a corrupt file. One bad task must not block recovery of other stranded tasks.

## Never Delete Rule

Crash recovery relocates task content only. It never drops a task silently and never executes a task. The script writes updated content to the destination first, then removes the original path from `relay/running/` after the destination move succeeds.

## Startup Wiring

P16 owns cycle startup wiring. The intended startup pattern is:

```powershell
if (Test-Path .\automation\orchestration\recovery\Reclaim-AiOsOrphans.ps1) {
    & .\automation\orchestration\recovery\Reclaim-AiOsOrphans.ps1 -Apply
}
```

This runs before normal relay work so stranded tasks return to the queue or move to error before the next cycle proceeds.

## Tuning

`OrphanMinutes` must be longer than the normal per-packet worker timeout. If it is too short, reclaim could move a task that a live worker still owns. The default is `30` minutes.
