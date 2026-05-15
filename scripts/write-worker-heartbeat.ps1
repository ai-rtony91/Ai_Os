param(
    [string]$WorkerId = "WORKER-1",
    [string]$Role = "Shell",
    [string]$Packet = "none"
)

$Root = "C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN"
$WorkerDir = Join-Path $Root "automation\orchestration\workers"

New-Item -ItemType Directory -Force -Path $WorkerDir | Out-Null

$Heartbeat = @{
    worker_id = $WorkerId
    role = $Role
    packet = $Packet
    started_at = (Get-Date).ToString("s")
    last_heartbeat = (Get-Date).ToString("s")
    status = "ACTIVE"
    host = $env:COMPUTERNAME
}

$HeartbeatPath = Join-Path $WorkerDir "$WorkerId-heartbeat.json"

$Heartbeat | ConvertTo-Json -Depth 5 |
Set-Content -Path $HeartbeatPath -Encoding UTF8

Write-Host ""
Write-Host "AI_OS WORKER HEARTBEAT WRITTEN" -ForegroundColor Green
Write-Host $HeartbeatPath -ForegroundColor Cyan
Write-Host ""
