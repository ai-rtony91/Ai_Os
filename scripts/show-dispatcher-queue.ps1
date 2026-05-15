$QueuePath = ".\automation\orchestration\queue\DISPATCHER_QUEUE.json"

if (!(Test-Path $QueuePath)) {
    Write-Host "Dispatcher queue not found." -ForegroundColor Red
    exit 1
}

$Queue = Get-Content $QueuePath | ConvertFrom-Json

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host " AI_OS DISPATCHER QUEUE VIEWER" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

$Queue.items | ForEach-Object {
    Write-Host "PACKET:   $($_.packet_id)" -ForegroundColor Green
    Write-Host "TITLE:    $($_.title)"
    Write-Host "LANE:     $($_.lane)"
    Write-Host "PRIORITY: $($_.priority)"
    Write-Host "STATUS:   $($_.status)" -ForegroundColor Yellow
    Write-Host "WORKER:   $($_.assigned_worker)"
    Write-Host ""
}
