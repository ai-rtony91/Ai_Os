Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$orchestrationRoot = $PSScriptRoot
$queuePath = Join-Path $orchestrationRoot "work_packets"
$legacyQueuePath = Join-Path $orchestrationRoot "packet_queue.example.json"
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
    if (Test-Path -LiteralPath $legacyQueuePath -PathType Leaf) {
        Write-Host "  Legacy detail fallback: packet_queue.example.json available"
    } else {
        Write-Host "  Legacy fallback not found; canonical source used."
    }
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

if (-not (Test-Path -LiteralPath $legacyQueuePath -PathType Leaf)) {
    Write-Host "Mode: UNKNOWN"
    Write-Host "Queue: unavailable"
    Write-Host "Purpose: display packet folder state counts."
    Write-Host ""
    Write-Host "Packet summary:"
    Write-Host "  Canonical source missing: automation/orchestration/work_packets/"
    Write-Host "  Legacy fallback not found; no queue source available."
    Write-Host ""
    Write-Host "Next safe action: restore or create the canonical work_packets folder through an approved workflow."
    exit 0
}

$queue = Read-JsonFile -Path $legacyQueuePath
$packets = @($queue.packets)

Write-Host "Mode: $($queue.mode)"
Write-Host "Queue: $($queue.queue_name)"
Write-Host "Purpose: $($queue.purpose)"
Write-Host "Fallback: legacy packet_queue.example.json used because canonical work_packets folder was unavailable."
Write-Host ""

if ($packets.Count -eq 0) {
    Write-Host "Packets: none found in packet_queue.example.json"
    exit 0
}

$availableCount = @($packets | Where-Object { $_.status -eq "available" }).Count
$assignedCount = @($packets | Where-Object { $null -ne $_.assigned_worker_id }).Count

Write-Host "Packet summary:"
Write-Host "  Total packets: $($packets.Count)"
Write-Host "  Available packets: $availableCount"
Write-Host "  Assigned packets: $assignedCount"
Write-Host ""

foreach ($packet in $packets) {
    $matchingLock = $lockItems | Where-Object { $_.packet_id -eq $packet.packet_id } | Select-Object -First 1
    $assignedWorker = if ([string]::IsNullOrWhiteSpace([string]$packet.assigned_worker_id)) { "UNASSIGNED" } else { $packet.assigned_worker_id }
    $claimStatus = if ($null -eq $matchingLock) { "no matching lock example" } else { $matchingLock.claim_status }
    $collisionStatus = if ($null -eq $matchingLock) { "UNKNOWN" } else { $matchingLock.collision_status }

    Write-Host "Packet: $($packet.packet_id)"
    Write-Host "  Name: $($packet.packet_name)"
    Write-Host "  Status: $($packet.status)"
    Write-Host "  Assigned worker: $assignedWorker"
    Write-Host "  Lock claim status: $claimStatus"
    Write-Host "  Collision status: $collisionStatus"
    Write-Host "  Approval required: $($packet.approval_required)"
    Write-Host "  Validator required: $($packet.validator_required)"
    Write-Host "  Allowed paths:"
    foreach ($path in @($packet.allowed_paths)) {
        Write-Host "    - $path"
    }
    Write-Host "  Blocked paths:"
    foreach ($path in @($packet.blocked_paths)) {
        Write-Host "    - $path"
    }
    Write-Host ""
}

Write-Host "Next safe action: review the queue status, then run an approved validator before assigning real work."
