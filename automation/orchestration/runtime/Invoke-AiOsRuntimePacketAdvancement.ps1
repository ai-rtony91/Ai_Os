param(
    [switch]$Apply
)

$ErrorActionPreference = 'Stop'

$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..\..')).Path
$activePacketDir = Join-Path $repoRoot 'automation\orchestration\work_packets\active'
$movePacketStateScript = Join-Path $repoRoot 'automation\orchestration\work_packets\Move-AiOsPacketState.ps1'

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

if (-not (Test-Path -LiteralPath $movePacketStateScript -PathType Leaf)) {
    throw "Canonical packet state script not found: $movePacketStateScript"
}

$moveArgs = @(
    '-ExecutionPolicy',
    'Bypass',
    '-File',
    $movePacketStateScript,
    '-PacketPath',
    $packetFile.FullName,
    '-AdvanceToNext',
    '-Worker',
    'runtime_packet_advancement'
)

if ($Apply) {
    $moveArgs += '-Apply'
}

powershell @moveArgs
exit $LASTEXITCODE
