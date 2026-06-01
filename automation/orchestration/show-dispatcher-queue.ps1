Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$orchestrationRoot = $PSScriptRoot
$queuePath = Join-Path $orchestrationRoot "work_packets"
$locksPath = Join-Path $orchestrationRoot "assignment_locks.example.json"

function Read-JsonFile {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "Required file was not found: $Path"
    }

    Get-Content -Raw -LiteralPath $Path | ConvertFrom-Json
}

$locks = Read-JsonFile -Path $locksPath
$lockItems = @($locks.locks)

Write-Host "AI_OS Dispatcher Queue Display"
Write-Host ""
Write-Host "Safety: display-only. No files are modified. No locks are created. No workers are launched."
Write-Host ""

if (Test-Path -LiteralPath $queuePath -PathType Container) {
    $activePackets = @(Get-ChildItem -LiteralPath (Join-Path $queuePath "active") -Filter "*.json" -File -ErrorAction SilentlyContinue)
    $blockedPackets = @(Get-ChildItem -LiteralPath (Join-Path $queuePath "blocked") -Filter "*.json" -File -ErrorAction SilentlyContinue)
    $completePackets = @(Get-ChildItem -LiteralPath (Join-Path $queuePath "complete") -Filter "*.json" -File -ErrorAction SilentlyContinue)

    Write-Host "Mode: FOLDER_STATE"
    Write-Host "Queue: canonical work_packets folder"
    Write-Host "Purpose: display packet folder state counts."
    Write-Host ""
    Write-Host "Packet summary:"
    Write-Host "  Source: automation/orchestration/work_packets/"
    Write-Host "  Active packets: $($activePackets.Count)"
    Write-Host "  Blocked packets: $($blockedPackets.Count)"
    Write-Host "  Complete packets: $($completePackets.Count)"
    Write-Host "  Legacy packet_queue.example.json fallback: not used; canonical source controls display."
    Write-Host ""
    Write-Host "Available packet files:"
    $packetFiles = @($activePackets) + @($blockedPackets) + @($completePackets)
    foreach ($packetFile in @($packetFiles | Select-Object -First 10)) {
        Write-Host "  - $($packetFile.Directory.Name)/$($packetFile.Name)"
    }
    if ($packetFiles.Count -eq 0) {
        Write-Host "  None"
    }
    Write-Host ""
    Write-Host "Next safe action: review canonical work packet folder state."
    exit 0
}

Write-Host "Mode: UNKNOWN"
Write-Host "Queue: unavailable"
Write-Host "Purpose: display packet folder state counts."
Write-Host ""
Write-Host "Packet summary:"
Write-Host "  Canonical source missing: automation/orchestration/work_packets/"
Write-Host "  Legacy packet_queue.example.json fallback is disabled for canonical display."
Write-Host ""
Write-Host "Next safe action: restore or create the canonical work_packets folder through an approved workflow."
