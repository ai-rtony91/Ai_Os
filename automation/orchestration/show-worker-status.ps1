Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$orchestrationRoot = $PSScriptRoot
$queuePath = Join-Path $orchestrationRoot "work_packets"
$legacyQueuePath = Join-Path $orchestrationRoot "packet_queue.example.json"
$locksPath = Join-Path $orchestrationRoot "assignment_locks.example.json"
$registryPath = Join-Path $orchestrationRoot "workers\AIOS_WORKER_REGISTRY.json"

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
$registry = if (Test-Path -LiteralPath $registryPath -PathType Leaf) { Read-JsonFile -Path $registryPath } else { $null }

Write-Host "AI_OS Worker Status Display"
Write-Host "Mode: $($locks.mode)"
Write-Host "Lock file: $($locks.lock_name)"
Write-Host "Purpose: $($locks.purpose)"
Write-Host ""
Write-Host "Safety: display-only. No files are modified. No locks are created. No workers are launched."
Write-Host ""

if ($null -ne $registry) {
    $workers = @($registry.workers)
    Write-Host "Canonical worker registry:"
    Write-Host "  Source: automation/orchestration/workers/AIOS_WORKER_REGISTRY.json"
    Write-Host "  Workers: $($workers.Count)"
    foreach ($worker in $workers) {
        Write-Host "  - $($worker.worker_id): $($worker.type) - $($worker.purpose)"
    }
    Write-Host ""
}

$packets = @()
if (Test-Path -LiteralPath $queuePath -PathType Container) {
    $activePackets = @(Get-ChildItem -LiteralPath (Join-Path $queuePath "active") -Filter "*.json" -File -ErrorAction SilentlyContinue)
    $blockedPackets = @(Get-ChildItem -LiteralPath (Join-Path $queuePath "blocked") -Filter "*.json" -File -ErrorAction SilentlyContinue)
    $completePackets = @(Get-ChildItem -LiteralPath (Join-Path $queuePath "complete") -Filter "*.json" -File -ErrorAction SilentlyContinue)
    Write-Host "Canonical packet source: automation/orchestration/work_packets/"
    Write-Host "  Active packets: $($activePackets.Count)"
    Write-Host "  Blocked packets: $($blockedPackets.Count)"
    Write-Host "  Complete packets: $($completePackets.Count)"
    if (Test-Path -LiteralPath $legacyQueuePath -PathType Leaf) {
        Write-Host "Legacy packet detail fallback: packet_queue.example.json available"
    } else {
        Write-Host "Legacy fallback not found; canonical source used."
    }
    Write-Host ""
} elseif (Test-Path -LiteralPath $legacyQueuePath -PathType Leaf) {
    $queue = Read-JsonFile -Path $legacyQueuePath
    $packets = @($queue.packets)
    Write-Host "Fallback packet source: packet_queue.example.json"
    Write-Host ""
} else {
    Write-Host "Packet source: unavailable"
    Write-Host "Legacy fallback not found; worker lock and registry status only."
    Write-Host ""
}

if ($lockItems.Count -eq 0) {
    Write-Host "Worker locks: none found in assignment_locks.example.json"
    exit 0
}

$claimedCount = @($lockItems | Where-Object { $_.claim_status -eq "claimed" }).Count
$unclaimedCount = @($lockItems | Where-Object { $_.claim_status -ne "claimed" }).Count
$collisionCount = @($lockItems | Where-Object { $_.collision_status -and $_.collision_status -ne "none" }).Count

Write-Host "Worker summary:"
Write-Host "  Total lock examples: $($lockItems.Count)"
Write-Host "  Claimed packets: $claimedCount"
Write-Host "  Unclaimed packets: $unclaimedCount"
Write-Host "  Collision warnings: $collisionCount"
Write-Host ""

foreach ($lock in $lockItems) {
    $matchingPacket = $packets | Where-Object { $_.packet_id -eq $lock.packet_id } | Select-Object -First 1
    $packetName = if ($null -eq $matchingPacket) { "UNKNOWN" } else { $matchingPacket.packet_name }
    $packetStatus = if ($null -eq $matchingPacket) { "UNKNOWN" } else { $matchingPacket.status }
    $claimedAt = if ([string]::IsNullOrWhiteSpace([string]$lock.claimed_at)) { "not claimed" } else { $lock.claimed_at }

    Write-Host "Worker record for packet: $($lock.packet_id)"
    Write-Host "  Packet name: $packetName"
    Write-Host "  Packet status: $packetStatus"
    Write-Host "  Worker ID: $($lock.worker_id)"
    Write-Host "  Claim status: $($lock.claim_status)"
    Write-Host "  Claimed at: $claimedAt"
    Write-Host "  Collision status: $($lock.collision_status)"
    Write-Host "  Approval required: $($lock.approval_required)"
    Write-Host "  Validator required: $($lock.validator_required)"
    Write-Host "  Allowed paths:"
    foreach ($path in @($lock.allowed_paths)) {
        Write-Host "    - $path"
    }
    Write-Host "  Blocked paths:"
    foreach ($path in @($lock.blocked_paths)) {
        Write-Host "    - $path"
    }
    Write-Host ""
}

Write-Host "Next safe action: review worker status only; use a separate approved APPLY workflow before creating real locks."
