# Queue Canonicalization Record

Date: 2026-06-01
Packet: AIOS-P21
Mode: APPLY

## Decision

The canonical active work queue is:

automation/orchestration/work_packets/active/

Future queue readers, reviewers, and worker-routing logic should treat this folder as the source for live work packets.

## Canonical Readers

- Python: services/python_supervisor/queue_scanner.py
- PowerShell: automation/orchestration/work_packets/Get-AiOsWorkPacketState.ps1

## Historical Or Stale Queues

automation/orchestration/queue/DISPATCHER_QUEUE.json is historical Phase 16 dispatcher assignment state. Do not write new items there. Read it only for historical audit context.

automation/orchestration/command_queue/AIOS_COMMAND_QUEUE.json is stale command-queue state. Its queued command is not the canonical work path. P21 verification found automation/session/Start-AiOsSession.ps1 exists, so the stale classification is based on queue canonicalization, not a missing target file.

## Packet Lifecycle Commands

- Packet creation: automation/orchestration/work_packets/New-AiOsWorkPacket.ps1
- Packet state advancement: automation/orchestration/work_packets/Move-AiOsPacketState.ps1

## Safety Boundary

P21 did not delete queue items, move active packets, edit active packet JSON, invoke workers, run queue runners, commit, push, or touch broker/OANDA/live trading paths.
