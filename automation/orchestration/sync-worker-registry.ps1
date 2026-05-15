Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$orchestrationRoot = $PSScriptRoot
$queuePath = Join-Path $orchestrationRoot "packet_queue.example.json"
$locksPath = Join-Path $orchestrationRoot "assignment_locks.example.json"
$registryPath = Join-Path $orchestrationRoot "worker_registry.example.json"

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

$queue = Read-JsonFile -Path $queuePath
$locks = Read-JsonFile -Path $locksPath
$registry = Read-JsonFile -Path $registryPath

$packets = @($queue.packets)
$lockItems = @($locks.locks)
$workers = @($registry.workers)

Write-Host "AI_OS Worker Registry Sync Display"
Write-Host "Queue: $($queue.queue_name)"
Write-Host "Locks: $($locks.lock_name)"
Write-Host "Registry: $($registry.registry_name)"
Write-Host "Mode: $($registry.mode)"
Write-Host ""
Write-Host "Safety: display-only. No files are modified. No locks are created. No workers are launched."
Write-Host ""

Write-Host "Sync summary:"
Write-Host "  Packets: $($packets.Count)"
Write-Host "  Locks: $($lockItems.Count)"
Write-Host "  Worker records: $($workers.Count)"
Write-Host ""

$missingWorkerRecords = @()
$staleOwnership = @()
$unclaimedOwnership = @()

foreach ($lock in $lockItems) {
    $packet = $packets | Where-Object { $_.packet_id -eq $lock.packet_id } | Select-Object -First 1
    $workerId = $lock.worker_id
    $worker = $null

    if (-not (Is-BlankAssignment $workerId)) {
        $worker = $workers | Where-Object { $_.worker_id -eq $workerId } | Select-Object -First 1
        if ($null -eq $worker) {
            $missingWorkerRecords += "Packet $($lock.packet_id) is locked by worker '$workerId', but that worker is missing from worker_registry.example.json."
        }
    }

    if ($lock.claim_status -ne "claimed" -or (Is-BlankAssignment $workerId)) {
        $unclaimedOwnership += "Packet $($lock.packet_id) is not claimed. Lock status: $($lock.claim_status). Worker ID: $workerId."
    }

    if ($null -eq $packet) {
        $staleOwnership += "Lock references packet $($lock.packet_id), but that packet is missing from packet_queue.example.json."
    }

    if ($null -ne $worker -and -not (Is-BlankAssignment $worker.assigned_packet_id) -and $worker.assigned_packet_id -ne $lock.packet_id) {
        $staleOwnership += "Worker $($worker.worker_id) is locked to packet $($lock.packet_id), but registry says assigned packet is $($worker.assigned_packet_id)."
    }
}

foreach ($packet in $packets) {
    $packetWorkerId = $packet.assigned_worker_id
    $packetLock = $lockItems | Where-Object { $_.packet_id -eq $packet.packet_id } | Select-Object -First 1

    if (-not (Is-BlankAssignment $packetWorkerId)) {
        $packetWorker = $workers | Where-Object { $_.worker_id -eq $packetWorkerId } | Select-Object -First 1
        if ($null -eq $packetWorker) {
            $missingWorkerRecords += "Packet $($packet.packet_id) is assigned to worker '$packetWorkerId', but that worker is missing from worker_registry.example.json."
        }

        if ($null -eq $packetLock) {
            $staleOwnership += "Packet $($packet.packet_id) names worker $packetWorkerId, but no matching lock exists."
        }
    }

    if ($null -eq $packetLock -and (Is-BlankAssignment $packetWorkerId)) {
        $unclaimedOwnership += "Packet $($packet.packet_id) has no assigned worker and no matching lock."
    }
}

foreach ($worker in $workers) {
    if (-not (Is-BlankAssignment $worker.assigned_packet_id)) {
        $workerPacket = $packets | Where-Object { $_.packet_id -eq $worker.assigned_packet_id } | Select-Object -First 1
        $workerLock = $lockItems | Where-Object { $_.packet_id -eq $worker.assigned_packet_id -and $_.worker_id -eq $worker.worker_id } | Select-Object -First 1

        if ($null -eq $workerPacket) {
            $staleOwnership += "Worker $($worker.worker_id) is assigned to missing packet $($worker.assigned_packet_id)."
        }

        if ($null -eq $workerLock) {
            $staleOwnership += "Worker $($worker.worker_id) is assigned to packet $($worker.assigned_packet_id), but no matching lock confirms that ownership."
        }
    }
}

Write-Host "Worker-to-packet status:"
foreach ($worker in $workers) {
    $assignedPacket = if (Is-BlankAssignment $worker.assigned_packet_id) { "none" } else { $worker.assigned_packet_id }
    $matchingPacket = if ($assignedPacket -eq "none") { $null } else { $packets | Where-Object { $_.packet_id -eq $assignedPacket } | Select-Object -First 1 }
    $matchingLock = if ($assignedPacket -eq "none") { $null } else { $lockItems | Where-Object { $_.packet_id -eq $assignedPacket -and $_.worker_id -eq $worker.worker_id } | Select-Object -First 1 }
    $packetStatus = if ($null -eq $matchingPacket) { "none" } else { $matchingPacket.status }
    $lockStatus = if ($null -eq $matchingLock) { "none" } else { $matchingLock.claim_status }

    Write-Host "  Worker: $($worker.worker_id)"
    Write-Host "    Name: $($worker.worker_name)"
    Write-Host "    Status: $($worker.status)"
    Write-Host "    Assigned packet: $assignedPacket"
    Write-Host "    Packet status: $packetStatus"
    Write-Host "    Matching lock status: $lockStatus"
}
Write-Host ""

Write-Host "Missing worker records:"
if ($missingWorkerRecords.Count -eq 0) {
    Write-Host "  None found."
} else {
    foreach ($item in $missingWorkerRecords) {
        Write-Host "  - $item"
    }
}
Write-Host ""

Write-Host "Stale ownership warnings:"
if ($staleOwnership.Count -eq 0) {
    Write-Host "  None found."
} else {
    foreach ($item in $staleOwnership) {
        Write-Host "  - $item"
    }
}
Write-Host ""

Write-Host "Unclaimed packet ownership:"
if ($unclaimedOwnership.Count -eq 0) {
    Write-Host "  None found."
} else {
    foreach ($item in $unclaimedOwnership) {
        Write-Host "  - $item"
    }
}
Write-Host ""

Write-Host "Next safe action: review sync status only; use a separate approved APPLY workflow before creating real worker claims."
