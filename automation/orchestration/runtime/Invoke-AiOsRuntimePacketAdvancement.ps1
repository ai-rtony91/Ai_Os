param(
    [switch]$Apply
)

$ErrorActionPreference = 'Stop'

$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..\..')).Path
$activePacketDir = Join-Path $repoRoot 'automation\orchestration\work_packets\active'
$packetStateMover = Join-Path $repoRoot 'automation\orchestration\work_packets\Move-AiOsPacketState.ps1'

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

if (-not (Test-Path -LiteralPath $packetStateMover -PathType Leaf)) {
    Write-Host ''
    Write-Host "BLOCKED: packet state mover not found: $packetStateMover" -ForegroundColor Red
    exit 1
}

powershell -ExecutionPolicy Bypass -File checkpoints/verify_success.ps1

if ($LASTEXITCODE -ne 0) {
    Write-Host ''
    Write-Host 'BLOCKED: proof verification failed' -ForegroundColor Red
    exit 1
}

& powershell -NoProfile -ExecutionPolicy Bypass -File $packetStateMover -PacketPath $packetFile.FullName -TargetState $nextStatus -Worker "runtime_packet_advancement" -Apply

if ($LASTEXITCODE -ne 0) {
    Write-Host ''
    Write-Host 'BLOCKED: packet state mover rejected the transition' -ForegroundColor Red
    exit 1
}

Write-Host 'Mode: APPLY'
Write-Host 'Packet update delegated: YES'
Write-Host 'Commit performed: NO'
Write-Host 'Push performed: NO'
