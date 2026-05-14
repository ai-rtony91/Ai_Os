# Worker Heartbeat Command

`Update-AIOSWorkerHeartbeat.ps1` manually registers one worker heartbeat into live worker runtime state.

This command is local-first and manual-safe. It does not launch workers, assign packets, approve APPLY, commit, push, create startup tasks, create scheduled tasks, or touch broker/OANDA/API/live trading systems.

## Command Path

`automation/dispatcher/runtime/workers/Update-AIOSWorkerHeartbeat.ps1`

## Runtime Files Updated

- `Reports/dispatcher/runtime/workers/active_worker_table.json`
- `Reports/dispatcher/runtime/workers/worker_heartbeat_table.json`
- `Reports/dispatcher/runtime/workers/worker_registration_status.json`
- `Reports/dispatcher/runtime/workers/worker_session_ledger.json`

## Required Parameters

`-WorkerId`

Allowed values are `AIOS-01` through `AIOS-10`.

`-CurrentState`

Allowed states:

- `IDLE`
- `ASSIGNED`
- `DRY_RUN_STARTED`
- `DRY_RUN_COMPLETE`
- `WAITING_APPROVAL`
- `APPLY_RUNNING`
- `VALIDATING`
- `VALIDATED`
- `STALE`
- `BLOCKED`
- `FAILED`
- `REVIEW_REQUIRED`
- `STOPPED`

## Optional Parameters

- `-AssignedRole`
- `-AssignedPacketId`
- `-LaunchSessionId`
- `-TerminalWindowName`
- `-NextSafeAction`

## Safety Rules

- The command updates exactly one worker ID.
- The command rejects worker IDs outside `AIOS-01` through `AIOS-10`.
- The command rejects states outside the approved state list.
- The command refreshes `heartbeat_time` using current UTC time.
- The command sets the matching heartbeat `stale_status` to `CURRENT`.
- The command preserves packet IDs, locks, and claimed paths unless an allowed optional parameter is passed.
- The command appends one heartbeat event to the session ledger.
- `APPLY_RUNNING` is blocked unless the worker already has an approved APPLY state.

## Example

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File automation/dispatcher/runtime/workers/Update-AIOSWorkerHeartbeat.ps1 -WorkerId AIOS-01 -CurrentState IDLE -AssignedRole "Orchestration Core" -TerminalWindowName "WINDOW 01 - Orchestration Core" -NextSafeAction "Worker heartbeat registered. Keep work DRY_RUN only until packet assignment is approved."
```

## Next Safe Action

After a heartbeat update, run the operator check before assigning packets, approving APPLY, staging, committing, or pushing.

