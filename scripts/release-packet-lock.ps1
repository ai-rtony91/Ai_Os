param(
    [string]$PacketId = "telemetry-validator"
)

$Root = "C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN"
$LockDir = Join-Path $Root "automation\orchestration\locks"
$LockPath = Join-Path $LockDir "$PacketId.lock.json"

if (!(Test-Path $LockPath)) {
    Write-Host "LOCK NOT FOUND" -ForegroundColor Red
    exit
}

$Data = Get-Content $LockPath | ConvertFrom-Json

$Data | Add-Member -NotePropertyName "status" -NotePropertyValue "RELEASED" -Force
$Data | Add-Member -NotePropertyName "released_at" -NotePropertyValue (Get-Date).ToString("s") -Force

$Data | ConvertTo-Json -Depth 5 |
Set-Content -Path $LockPath -Encoding UTF8

Write-Host "PACKET RELEASED" -ForegroundColor Yellow
Write-Host "Packet: $PacketId"
