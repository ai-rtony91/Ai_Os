# Telemetry Event Ledger

AI_OS uses telemetry events to make automation observable, reviewable, and auditable.

## Ledger

Default local ledger:

```text
telemetry/work_ledger.jsonl


telemetry/work_ledger.jsonl
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/telemetry/Write-AIOSTelemetryEvent.ps1 -EventType "packet_dispatched" -Source "dispatcher" -Summary "Packet sent to approval inbox" -PacketId "trading_lab_latency_001" -Status "waiting_approval" -Risk "medium"
