$QueuePath = ".\automation\orchestration\queue\DISPATCHER_QUEUE.json"
$CardDir = ".\automation\orchestration\task_cards"

New-Item -ItemType Directory -Force -Path $CardDir | Out-Null

$Queue = Get-Content $QueuePath | ConvertFrom-Json

$Queue.items |
Where-Object { $_.status -eq "ASSIGNED" } |
ForEach-Object {
    $CardPath = Join-Path $CardDir "$($_.assigned_worker)-TASK.md"

    @"
# AI_OS Worker Task Card

Worker: $($_.assigned_worker)
Packet: $($_.packet_id)
Title: $($_.title)
Lane: $($_.lane)
Priority: $($_.priority)
Status: $($_.status)

## Operator Rule

Only work this packet in the assigned worker lane.

## Next Safe Action

Review packet assignment and wait for explicit DRY_RUN/APPLY instruction.
"@ | Set-Content -Path $CardPath -Encoding UTF8

    Write-Host "Wrote task card: $CardPath" -ForegroundColor Green
}
