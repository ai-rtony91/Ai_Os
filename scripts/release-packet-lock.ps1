param(
    [string]$PacketId = "telemetry-validator"
)

$Root = "C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN"
$LockDir = Join-Path $Root "automation\orchestration\locks"

$LockPath = Join-Path $LockDir "$PacketId.lock.json"

if (!(Test-Path $LockPath)) {

    Write-Host ""
    Write-Host "LOCK NOT FOUND" -ForegroundColor Red
    Write-Host ""
    exit
}

$Data = Get-Content $LockPath | ConvertFrom-Json

$Data.status = "RELEASED"
$Data.released_at = (Get-Date).ToString("s")

$Data | ConvertTo-Json -Depth 5 |
Set-Content -Path $LockPath -Encoding UTF8

Write-Host ""
Write-Host "PACKET RELEASED" -ForegroundColor Yellow
Write-Host "Packet: $PacketId"
Write-Host ""
