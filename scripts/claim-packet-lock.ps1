param(
    [string]$PacketId = "dispatcher-runtime",
    [string]$WorkerId = "WORKER-1"
)

$Root = "C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN"
$LockDir = Join-Path $Root "automation\orchestration\locks"

New-Item -ItemType Directory -Force -Path $LockDir | Out-Null

$LockPath = Join-Path $LockDir "$PacketId.lock.json"

if (Test-Path $LockPath) {

    Write-Host ""
    Write-Host "LOCK EXISTS:" -ForegroundColor Red
    Write-Host $LockPath -ForegroundColor Yellow
    Write-Host ""
    exit
}

$LockData = @{
    packet_id = $PacketId
    worker_id = $WorkerId
    claimed_at = (Get-Date).ToString("s")
    status = "CLAIMED"
    host = $env:COMPUTERNAME
}

$LockData | ConvertTo-Json -Depth 5 |
Set-Content -Path $LockPath -Encoding UTF8

Write-Host ""
Write-Host "PACKET CLAIMED" -ForegroundColor Green
Write-Host "Packet: $PacketId"
Write-Host "Worker: $WorkerId"
Write-Host ""
