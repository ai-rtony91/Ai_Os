Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$orchestrationRoot = $PSScriptRoot
$registryPath = Join-Path $orchestrationRoot "worker_registry.v1.example.json"
$queuePath = Join-Path $orchestrationRoot "packet_queue_ledger.v1.example.json"
$locksPath = Join-Path $orchestrationRoot "assignment_locks.v1.example.json"

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

function Is-BlankAssignment {
    param($Value)

    return ($null -eq $Value -or [string]::IsNullOrWhiteSpace([string]$Value) -or [string]$Value -eq "UNASSIGNED")
}

function Write-PathList {
    param(
        [object[]]$Paths
    )

    if ($Paths.Count -eq 0) {
        Write-Host "      - None"
        return
    }

    foreach ($path in $Paths) {
        Write-Host "      - $path"
    }
}

$registry = Read-JsonFile -Path $registryPath
$queue = Read-JsonFile -Path $queuePath
$locks = Read-JsonFile -Path $locksPath
$workers = @($registry.workers)
$packets = @($queue.packets)
$lockItems = @($locks.locks)

Write-Host "AI_OS Worker Registry v1 Display"
Write-Host "Mode: $($registry.mode)"
Write-Host "Registry: $($registry.registry_name)"
Write-Host "Purpose: $($registry.purpose)"
Write-Host ""
Write-Host "Safety: display-only. No worker records are modified. No assignments are changed. No workers are launched."
Write-Host ""

if ($workers.Count -eq 0) {
    Write-Host "Workers: none found in worker_registry.v1.example.json"
    exit 0
}

$standbyWorkers = @($workers | Where-Object { $_.status -eq "standby" })
$assignedWorkers = @($workers | Where-Object { -not (Is-BlankAssignment $_.assigned_packet_id) })
$offlineWorkers = @($workers | Where-Object { $_.status -match "offline" })
$missingPacketAssignments = @()
$staleLockAssignments = @()

foreach ($worker in $workers) {
    if (-not (Is-BlankAssignment $worker.assigned_packet_id)) {
        $matchingPacket = $packets | Where-Object { $_.packet_id -eq $worker.assigned_packet_id } | Select-Object -First 1
        $matchingLock = $lockItems | Where-Object { $_.packet_id -eq $worker.assigned_packet_id -and $_.worker_id -eq $worker.worker_id } | Select-Object -First 1

        if ($null -eq $matchingPacket) {
            $missingPacketAssignments += "Worker $($worker.worker_id) points to missing packet $($worker.assigned_packet_id)."
        }

        if ($null -eq $matchingLock) {
            $staleLockAssignments += "Worker $($worker.worker_id) has assigned packet $($worker.assigned_packet_id), but no matching lock confirms it."
        }
    }
}

Write-Host "Worker summary:"
Write-Host "  Total workers: $($workers.Count)"
Write-Host "  Standby workers: $($standbyWorkers.Count)"
Write-Host "  Assigned workers: $($assignedWorkers.Count)"
Write-Host "  Offline example workers: $($offlineWorkers.Count)"
Write-Host "  Missing packet assignments: $($missingPacketAssignments.Count)"
Write-Host "  Stale lock assignments: $($staleLockAssignments.Count)"
Write-Host ""

foreach ($worker in ($workers | Sort-Object worker_id)) {
    $assignedPacket = if (Is-BlankAssignment $worker.assigned_packet_id) { "none" } else { $worker.assigned_packet_id }
    $matchingPacket = if ($assignedPacket -eq "none") { $null } else { $packets | Where-Object { $_.packet_id -eq $assignedPacket } | Select-Object -First 1 }
    $matchingLock = if ($assignedPacket -eq "none") { $null } else { $lockItems | Where-Object { $_.packet_id -eq $assignedPacket -and $_.worker_id -eq $worker.worker_id } | Select-Object -First 1 }
    $packetStatus = if ($null -eq $matchingPacket) { "none" } else { $matchingPacket.status }
    $lockStatus = if ($null -eq $matchingLock) { "none" } else { $matchingLock.claim_status }
    $lastSeen = if ([string]::IsNullOrWhiteSpace([string]$worker.last_seen)) { "UNKNOWN" } else { $worker.last_seen }

    Write-Host "Worker: $($worker.worker_id)"
    Write-Host "  Name: $($worker.worker_name)"
    Write-Host "  Status: $($worker.status)"
    Write-Host "  Assigned packet: $assignedPacket"
    Write-Host "  Packet status: $packetStatus"
    Write-Host "  Matching lock status: $lockStatus"
    Write-Host "  Last seen: $lastSeen"
    Write-Host "  Allowed paths:"
    Write-PathList -Paths @($worker.allowed_paths)
    Write-Host "  Blocked paths:"
    Write-PathList -Paths @($worker.blocked_paths)
    Write-Host "  Safety notes:"
    Write-PathList -Paths @($worker.safety_notes)
    Write-Host ""
}

Write-Host "Missing packet assignments:"
if ($missingPacketAssignments.Count -eq 0) {
    Write-Host "  None"
} else {
    foreach ($item in $missingPacketAssignments) {
        Write-Host "  - $item"
    }
}
Write-Host ""

Write-Host "Stale lock assignments:"
if ($staleLockAssignments.Count -eq 0) {
    Write-Host "  None"
} else {
    foreach ($item in $staleLockAssignments) {
        Write-Host "  - $item"
    }
}
Write-Host ""

Write-Host "Next safe action: review worker registry status only; use a separate approved APPLY workflow before launching workers or changing assignments."
