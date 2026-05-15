param(
    [string]$WorkerId = "WORKER-1"
)

$QueuePath = ".\automation\orchestration\queue\DISPATCHER_QUEUE.json"

if (!(Test-Path $QueuePath)) {
    Write-Host "Dispatcher queue not found." -ForegroundColor Red
    exit 1
}

$Queue = Get-Content $QueuePath | ConvertFrom-Json
$ReadyItem = $Queue.items | Where-Object { $_.status -eq "READY" } | Select-Object -First 1

if ($null -eq $ReadyItem) {
    Write-Host "No READY queue item found." -ForegroundColor Yellow
    exit 0
}

$ReadyItem.status = "ASSIGNED"
$ReadyItem.assigned_worker = $WorkerId
$ReadyItem.assigned_at = (Get-Date).ToString("s")

$Queue | ConvertTo-Json -Depth 10 |
Set-Content -Path $QueuePath -Encoding UTF8

Write-Host "QUEUE ITEM ASSIGNED" -ForegroundColor Green
Write-Host "Packet: $($ReadyItem.packet_id)"
Write-Host "Worker: $WorkerId"
