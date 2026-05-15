$WorkerDir = ".\automation\orchestration\workers"

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host " AI_OS WORKER STATUS VIEWER" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

Get-ChildItem $WorkerDir -Filter "*heartbeat.json" |
ForEach-Object {
    $Data = Get-Content $_.FullName | ConvertFrom-Json

    Write-Host "WORKER: $($Data.worker_id)" -ForegroundColor Green
    Write-Host "ROLE:   $($Data.role)"
    Write-Host "PACKET: $($Data.packet)"
    Write-Host "STATUS: $($Data.status)"
    Write-Host "LAST:   $($Data.last_heartbeat)"
    Write-Host "HOST:   $($Data.host)"
    Write-Host ""
}
