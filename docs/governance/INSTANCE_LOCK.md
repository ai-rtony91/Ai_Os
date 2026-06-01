# AI_OS Instance Lock

## Purpose

`automation/orchestration/lock/Test-AiOsInstanceLock.ps1` provides a local single-instance guard for the AI_OS supervisor loop. It prevents two supervisor loops from running at the same time on one machine.

The lock is local only. It does not register scheduled tasks, create services, kill processes, restart processes, access secrets, or touch broker/OANDA/live trading paths.

## Lock File

Default path:

```text
control/cycle/supervisor.lock
```

Schema:

```json
{
  "pid": 24180,
  "host": "ANTHONY-PC",
  "started_at_utc": "2026-05-31T21:14:07Z"
}
```

The script resolves this path from the repository root, not from the caller's current working directory.

## Actions

Every action returns an object with at least:

```text
ok      bool
reason  string
```

`Acquire` writes the lock when no valid live lock exists. If another live, fresh lock exists, it returns `ok=false` and `reason=SUPERVISOR_ALREADY_RUNNING`. If the lock is stale, dead, corrupt, or empty, it is reclaimable and returns `ok=true` with `reason=RECLAIMED_STALE` when acquired.

`Release` removes the lock only when the current process owns it. If the lock is absent or owned by another process, it returns `ok=true` with `reason=NOT_OWNER_OR_ABSENT` and leaves the file unchanged.

`Status` reports whether a lock exists, the holder pid when present, and the lock age in minutes when available.

## Stale Rule

`Acquire` treats a lock as actively held only when both conditions are true:

- the recorded pid is alive.
- the lock age is less than `StaleMinutes`.

If either condition is false, the lock is reclaimable. This avoids permanent refusal after reboot because Windows can reuse process ids.

## Dry Run

Without `-Apply`, the script returns the same decision object but does not write or remove the lock file. Dry run may include `would_write=true` or `would_remove=true` to show the action that would occur under `-Apply`.

## Fail-Closed Contract

The script never throws to callers. Unexpected errors return:

```text
ok=false
reason=LOCK_ERROR:<message>
```

Callers must refuse to start a second supervisor instance when `.ok` is false.

## P16 Consumption

P16 owns the integration in `Invoke-AiOsNightCycle.ps1`. It wraps the supervisor loop by acquiring before the `do/while -Watch` cycle and releasing in `finally`:

```powershell
$lk = & .\automation\orchestration\lock\Test-AiOsInstanceLock.ps1 -Action Acquire -Apply
if (-not $lk.ok) { exit 0 }
try {
    # do/while -Watch supervisor loop
} finally {
    & .\automation\orchestration\lock\Test-AiOsInstanceLock.ps1 -Action Release -Apply
}
```

This packet only provides the script and this document. It does not edit the supervisor loop.
