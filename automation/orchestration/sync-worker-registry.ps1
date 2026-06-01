Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$orchestrationRoot = $PSScriptRoot
$canonicalQueuePath = Join-Path $orchestrationRoot "work_packets"
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

function Read-OptionalJsonFile {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return $null
    }

    Get-Content -Raw -LiteralPath $Path | ConvertFrom-Json
}

function Get-NormalizedWorkPackets {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    if (-not (Test-Path -LiteralPath $Path -PathType Container)) {
        return @()
    }

    $packets = @()
    foreach ($state in @("active", "blocked", "complete")) {
        $statePath = Join-Path $Path $state
        if (-not (Test-Path -LiteralPath $statePath -PathType Container)) {
            continue
        }

        foreach ($file in @(Get-ChildItem -LiteralPath $statePath -Filter "*.json" -File -ErrorAction SilentlyContinue)) {
            $packet = Read-OptionalJsonFile -Path $file.FullName
            if ($null -eq $packet) {
                continue
            }

            $assignedWorker = Get-JsonValue -Object $packet -Name "assigned_worker_id" -Default (Get-JsonValue -Object $packet -Name "assigned_worker")
            $packetName = Get-JsonValue -Object $packet -Name "packet_name" -Default (Get-JsonValue -Object $packet -Name "title" -Default $file.BaseName)
            $packets += [pscustomobject]@{
                packet_id = Get-JsonValue -Object $packet -Name "packet_id" -Default $file.BaseName
                packet_name = $packetName
                status = Get-JsonValue -Object $packet -Name "status" -Default $state
                assigned_worker_id = $assignedWorker
                source_file = $file.FullName
            }
        }
    }

    return $packets
}

function Is-BlankAssignment {
    param($Value)

    return ($null -eq $Value -or [string]::IsNullOrWhiteSpace([string]$Value) -or [string]$Value -eq "UNASSIGNED")
}

function Get-JsonValue {
    param(
        [AllowNull()]$Object,
        [Parameter(Mandatory = $true)][string]$Name,
        [string]$Default = ""
    )

    if ($null -eq $Object) { return $Default }
    if ($Object.PSObject.Properties.Name -contains $Name) {
        $value = $Object.$Name
        if ($null -ne $value -and -not [string]::IsNullOrWhiteSpace([string]$value)) {
            return $value
        }
    }
    return $Default
}

$locks = Read-JsonFile -Path $locksPath
$registry = if (Test-Path -LiteralPath $registryPath -PathType Leaf) { Read-JsonFile -Path $registryPath } else { $null }

$queue = $null
$queueSource = "none"
$packets = @()
if (Test-Path -LiteralPath $canonicalQueuePath -PathType Container) {
    $packets = @(Get-NormalizedWorkPackets -Path $canonicalQueuePath)
    $queueSource = "automation/orchestration/work_packets/"
}
$lockItems = @($locks.locks)
$workers = if ($null -eq $registry) { @() } else { @($registry.workers) }

Write-Host "AI_OS Worker Registry Sync Display"
Write-Host "Queue source: $queueSource"
if (Test-Path -LiteralPath $canonicalQueuePath -PathType Container) {
    Write-Host "Canonical queue folder: automation/orchestration/work_packets/"
    Write-Host "Legacy packet_queue.example.json fallback: not used; canonical source controls display."
} else {
    Write-Host "Queue detail: unavailable"
    Write-Host "Canonical work_packets folder missing; legacy packet_queue.example.json fallback is disabled."
}
Write-Host "Locks: $($locks.lock_name)"
Write-Host "Registry: $(if ($null -eq $registry) { 'MISSING' } else { Get-JsonValue -Object $registry -Name 'registry_name' -Default (Get-JsonValue -Object $registry -Name 'registry_id' -Default 'UNKNOWN') })"
Write-Host "Mode: $(if ($null -eq $registry) { 'UNKNOWN' } else { Get-JsonValue -Object $registry -Name 'mode' -Default 'canonical registry' })"
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
            $missingWorkerRecords += "Packet $($lock.packet_id) is locked by worker '$workerId', but that worker is missing from the selected worker registry source."
        }
    }

    if ($lock.claim_status -ne "claimed" -or (Is-BlankAssignment $workerId)) {
        $unclaimedOwnership += "Packet $($lock.packet_id) is not claimed. Lock status: $($lock.claim_status). Worker ID: $workerId."
    }

    if ($null -eq $packet) {
        $staleOwnership += "Lock references packet $($lock.packet_id), but that packet is missing from the selected packet source."
    }

    $workerAssignedPacketId = Get-JsonValue -Object $worker -Name "assigned_packet_id"
    if ($null -ne $worker -and -not (Is-BlankAssignment $workerAssignedPacketId) -and $workerAssignedPacketId -ne $lock.packet_id) {
        $staleOwnership += "Worker $($worker.worker_id) is locked to packet $($lock.packet_id), but registry says assigned packet is $workerAssignedPacketId."
    }
}

foreach ($packet in $packets) {
    $packetWorkerId = $packet.assigned_worker_id
    $packetLock = $lockItems | Where-Object { $_.packet_id -eq $packet.packet_id } | Select-Object -First 1

    if (-not (Is-BlankAssignment $packetWorkerId)) {
        $packetWorker = $workers | Where-Object { $_.worker_id -eq $packetWorkerId } | Select-Object -First 1
        if ($null -eq $packetWorker) {
            $missingWorkerRecords += "Packet $($packet.packet_id) is assigned to worker '$packetWorkerId', but that worker is missing from the selected worker registry source."
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
    $workerAssignedPacketId = Get-JsonValue -Object $worker -Name "assigned_packet_id"
    if (-not (Is-BlankAssignment $workerAssignedPacketId)) {
        $workerPacket = $packets | Where-Object { $_.packet_id -eq $workerAssignedPacketId } | Select-Object -First 1
        $workerLock = $lockItems | Where-Object { $_.packet_id -eq $workerAssignedPacketId -and $_.worker_id -eq $worker.worker_id } | Select-Object -First 1

        if ($null -eq $workerPacket) {
            $staleOwnership += "Worker $($worker.worker_id) is assigned to missing packet $workerAssignedPacketId."
        }

        if ($null -eq $workerLock) {
            $staleOwnership += "Worker $($worker.worker_id) is assigned to packet $workerAssignedPacketId, but no matching lock confirms that ownership."
        }
    }
}

Write-Host "Worker-to-packet status:"
foreach ($worker in $workers) {
    $workerAssignedPacketId = Get-JsonValue -Object $worker -Name "assigned_packet_id"
    $assignedPacket = if (Is-BlankAssignment $workerAssignedPacketId) { "none" } else { $workerAssignedPacketId }
    $matchingPacket = if ($assignedPacket -eq "none") { $null } else { $packets | Where-Object { $_.packet_id -eq $assignedPacket } | Select-Object -First 1 }
    $matchingLock = if ($assignedPacket -eq "none") { $null } else { $lockItems | Where-Object { $_.packet_id -eq $assignedPacket -and $_.worker_id -eq $worker.worker_id } | Select-Object -First 1 }
    $packetStatus = if ($null -eq $matchingPacket) { "none" } else { $matchingPacket.status }
    $lockStatus = if ($null -eq $matchingLock) { "none" } else { $matchingLock.claim_status }

    Write-Host "  Worker: $($worker.worker_id)"
    Write-Host "    Name: $(Get-JsonValue -Object $worker -Name 'worker_name' -Default $worker.worker_id)"
    Write-Host "    Status: $(Get-JsonValue -Object $worker -Name 'status' -Default 'canonical')"
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
