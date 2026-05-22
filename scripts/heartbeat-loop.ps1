param(
    [string]$WorkerId = "WORKER-1",
    [string]$Role = "Shell",
    [string]$Packet = "none",
    [int]$IntervalSeconds = 15
)

$Root = "C:\Dev\Ai.Os"
$WorkerDir = Join-Path $Root "automation\orchestration\workers"

New-Item -ItemType Directory -Force -Path $WorkerDir | Out-Null

$HeartbeatPath = Join-Path $WorkerDir "$WorkerId-heartbeat.json"

Write-Host ""
Write-Host "AI_OS HEARTBEAT LOOP STARTED" -ForegroundColor Green
Write-Host "Worker: $WorkerId" -ForegroundColor Cyan
Write-Host ""

while ($true) {

    $Heartbeat = @{
        worker_id = $WorkerId
        role = $Role
        packet = $Packet
        status = "ACTIVE"
        host = $env:COMPUTERNAME
        last_heartbeat = (Get-Date).ToString("s")
    }

    $Heartbeat | ConvertTo-Json -Depth 5 |
    Set-Content -Path $HeartbeatPath -Encoding UTF8

    Write-Host "Heartbeat updated: $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor DarkGray

    Start-Sleep -Seconds $IntervalSeconds
}
