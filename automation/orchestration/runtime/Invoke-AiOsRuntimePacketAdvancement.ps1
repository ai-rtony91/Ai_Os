param(
    [switch]$Apply
)

$ErrorActionPreference = 'Stop'

$repoRoot = 'C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN'
$activePacketDir = Join-Path $repoRoot 'automation\orchestration\work_packets\active'

$statusMoves = @{
    'active' = 'routed'
    'routed' = 'dry_run_done'
    'dry_run_done' = 'awaiting_approval'
    'approved' = 'applying'
    'applying' = 'validated'
    'validated' = 'complete'
}

if (-not (Test-Path -LiteralPath $activePacketDir)) {
    Write-Host 'No active packet found'
    exit 0
}

$packetFile = Get-ChildItem -LiteralPath $activePacketDir -Filter '*.json' -File |
    Sort-Object LastWriteTimeUtc, Name -Descending |
    Select-Object -First 1

if (-not $packetFile) {
    Write-Host 'No active packet found'
    exit 0
}

$packet = Get-Content -LiteralPath $packetFile.FullName -Raw | ConvertFrom-Json
$currentStatus = [string]$packet.status

if (-not $statusMoves.ContainsKey($currentStatus)) {
    Write-Host "Packet: $($packetFile.FullName)"
    Write-Host "Current status: $currentStatus"
    Write-Host 'Next status: NONE'
    Write-Host 'Result: BLOCKED - no legal status move exists.'
    exit 1
}

$nextStatus = $statusMoves[$currentStatus]

Write-Host "Packet: $($packetFile.FullName)"
Write-Host "Current status: $currentStatus"
Write-Host "Next status: $nextStatus"

if (-not $Apply) {
    Write-Host 'Mode: DRY_RUN'
    Write-Host 'Packet updated: NO'
    exit 0
}


powershell -ExecutionPolicy Bypass -File checkpoints/verify_success.ps1

if ($LASTEXITCODE -ne 0) {
    Write-Host ''
    Write-Host 'BLOCKED: proof verification failed' -ForegroundColor Red
    exit 1
}


$packet.status = $nextStatus
$packet.updated_utc = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')

$note = 'Advanced by runtime packet advancement.'
if ($null -eq $packet.notes) {
    $packet.notes = @($note)
} elseif ($packet.notes -is [System.Array]) {
    $packet.notes = @($packet.notes) + $note
} else {
    $packet.notes = @([string]$packet.notes, $note)
}

$packet |
    ConvertTo-Json -Depth 20 |
    Set-Content -LiteralPath $packetFile.FullName -Encoding UTF8

Write-Host 'Mode: APPLY'
Write-Host 'Packet updated: YES'
Write-Host 'Commit performed: NO'
Write-Host 'Push performed: NO'
