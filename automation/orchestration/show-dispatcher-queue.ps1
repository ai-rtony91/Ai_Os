Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$orchestrationRoot = $PSScriptRoot
$queuePath = Join-Path $orchestrationRoot "packet_queue.example.json"
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

$queue = Read-JsonFile -Path $queuePath
$locks = Read-JsonFile -Path $locksPath
$packets = @($queue.packets)
$lockItems = @($locks.locks)

Write-Host "AI_OS Dispatcher Queue Display"
Write-Host "Mode: $($queue.mode)"
Write-Host "Queue: $($queue.queue_name)"
Write-Host "Purpose: $($queue.purpose)"
Write-Host ""
Write-Host "Safety: display-only. No files are modified. No locks are created. No workers are launched."
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
