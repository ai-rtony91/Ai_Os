# AIOS Phase 2 Queue Dispatcher

Phase 2 adds a local work packet queue and a read-only dispatcher preview.

## Scope

- Queue schema: `work_packets/queue.schema.json`
- Example queue: `work_packets/queues/aios_phase2_queue.example.json`
- Dispatcher preview: `automation/operator/Invoke-AiOsPacketDispatcher.ps1`
- Validator: `automation/operator/Test-AiOsQueueDispatcher.DRY_RUN.ps1`

## Safety Rules

- DRY_RUN only.
- No Codex auto-launch.
- No commits.
- No pushes.
- No new branches.
- No live trading.
- No broker connection.
- No API keys, secrets, webhooks, or real orders.
- No queue mutation during dispatcher preview.

## Dispatcher Behavior

The dispatcher reads the Phase 2 queue, confirms the safety block is intact, selects the first `READY` item by `queue_rank`, confirms the packet exists, and prints a dispatch preview for manual operator handling.

It does not assign the item, edit JSON, start a worker, launch Codex, stage files, commit, push, or connect to any trading system.

## Validation

Run the validator from the repository root:

```powershell
powershell -ExecutionPolicy Bypass -File automation/operator/Test-AiOsQueueDispatcher.DRY_RUN.ps1
```

Run the dispatcher preview from the repository root:

```powershell
powershell -ExecutionPolicy Bypass -File automation/operator/Invoke-AiOsPacketDispatcher.ps1
```

Expected result: validation passes, dispatcher prints one DRY_RUN dispatch preview, and both commands report no commit and no push.
