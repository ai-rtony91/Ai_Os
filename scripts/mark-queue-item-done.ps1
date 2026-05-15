param(
    [string]$PacketId = "dispatcher-queue-core"
)

$QueuePath = ".\automation\orchestration\queue\DISPATCHER_QUEUE.json"

$Queue = Get-Content $QueuePath | ConvertFrom-Json
$Item = $Queue.items | Where-Object { $_.packet_id -eq $PacketId } | Select-Object -First 1

if ($null -eq $Item) {
    Write-Host "Packet not found: $PacketId" -ForegroundColor Red
    exit 1
}

$Item.status = "DONE"
$Item.completed_at = (Get-Date).ToString("s")

$Queue | ConvertTo-Json -Depth 10 |
Set-Content -Path $QueuePath -Encoding UTF8

Write-Host "QUEUE ITEM DONE" -ForegroundColor Green
Write-Host "Packet: $PacketId"
