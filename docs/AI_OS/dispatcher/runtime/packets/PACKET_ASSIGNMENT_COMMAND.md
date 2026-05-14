# Packet Assignment Command

## Purpose

`Assign-AIOSPacket.ps1` performs the first manual-safe packet assignment for AI_OS.

It assigns one queued packet to one idle worker after validating live packet state and live worker heartbeat state.

## Command

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File automation/dispatcher/runtime/packets/Assign-AIOSPacket.ps1 -PacketId PACKET-LIVE-QUEUE-001 -WorkerId AIOS-01 -AssignedBy "AIOS Operator"
```

## Files Read

- `Reports/dispatcher/runtime/packets/packet_queue.json`
- `Reports/dispatcher/runtime/packets/packet_runtime_table.json`
- `Reports/dispatcher/runtime/packets/packet_assignment_ledger.json`
- `Reports/dispatcher/runtime/packets/packet_status_history.json`
- `Reports/dispatcher/runtime/workers/active_worker_table.json`
- `Reports/dispatcher/runtime/workers/worker_heartbeat_table.json`

## Files Updated

- `Reports/dispatcher/runtime/packets/packet_queue.json`
- `Reports/dispatcher/runtime/packets/packet_runtime_table.json`
- `Reports/dispatcher/runtime/packets/packet_assignment_ledger.json`
- `Reports/dispatcher/runtime/packets/packet_status_history.json`

## Safety Rules

The command refuses assignment unless:

- the packet status is `QUEUED`
- the packet mode is `DRY_RUN`
- `approval_required` is `true`
- `apply_allowed` is `false`
- the packet is not already assigned
- the worker state is `IDLE`
- the worker has no assigned packet
- the worker heartbeat state is `IDLE`
- the worker heartbeat status is `CURRENT`
- the worker heartbeat is not stale

## Boundaries

The command does not:

- launch workers
- claim locks
- approve APPLY
- run APPLY
- stage files
- commit
- push
- create startup tasks
- create scheduled tasks
- touch broker, OANDA, API key, webhook, or live trading systems

## Successful Assignment

On success, the command:

- sets packet status to `ASSIGNED`
- sets `worker_id`
- sets `assigned_worker_id`
- records an `assignment_id`
- appends `packet_assignment_ledger.json`
- appends `packet_status_history.json`
- preserves `DRY_RUN`
- preserves `approval_required: true`
- preserves `apply_allowed: false`

## Next Safe Action

After assignment, the assigned worker may start DRY_RUN only. APPLY, lock claiming, staging, commit, and push remain blocked until explicitly approved.
