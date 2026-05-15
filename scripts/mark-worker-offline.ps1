param(
    [string]$WorkerId = "WORKER-1"
)

$Root = "C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN"
$WorkerDir = Join-Path $Root "automation\orchestration\workers"
$HeartbeatPath = Join-Path $WorkerDir "$WorkerId-heartbeat.json"

if (Test-Path $HeartbeatPath) {
    $Data = Get-Content $HeartbeatPath | ConvertFrom-Json
    $Data.status = "OFFLINE"
    $Data.last_heartbeat = (Get-Date).ToString("s")

    $Data | ConvertTo-Json -Depth 5 |
    Set-Content -Path $HeartbeatPath -Encoding UTF8

    Write-Host "$WorkerId marked OFFLINE" -ForegroundColor Yellow
} else {
    Write-Host "Heartbeat file not found for $WorkerId" -ForegroundColor Red
}
