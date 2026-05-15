Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$orchestrationRoot = $PSScriptRoot
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

$queue = Read-JsonFile -Path $queuePath
$locks = Read-JsonFile -Path $locksPath
$packets = @($queue.packets)
$lockItems = @($locks.locks)

Write-Host "AI_OS Packet Queue Ledger Display"
Write-Host "Mode: $($queue.mode)"
Write-Host "Ledger: $($queue.ledger_name)"
Write-Host "Purpose: $($queue.purpose)"
Write-Host ""
Write-Host "Safety: display-only. No queue records are modified. No packets are claimed. No workers are launched."
Write-Host ""

if ($packets.Count -eq 0) {
    Write-Host "Packets: none found in packet_queue_ledger.v1.example.json"
    exit 0
}

$availablePackets = @($packets | Where-Object { $_.status -eq "available" })
$assignedPackets = @($packets | Where-Object { -not (Is-BlankAssignment $_.assigned_worker_id) })
$blockedPackets = @($packets | Where-Object { $_.status -eq "blocked" })
$validationRequiredPackets = @($packets | Where-Object { $_.validator_required -eq $true })

Write-Host "Queue summary:"
Write-Host "  Total packets: $($packets.Count)"
Write-Host "  Available packets: $($availablePackets.Count)"
Write-Host "  Assigned packets: $($assignedPackets.Count)"
Write-Host "  Blocked packets: $($blockedPackets.Count)"
Write-Host "  Validator-required packets: $($validationRequiredPackets.Count)"
Write-Host ""

foreach ($packet in ($packets | Sort-Object packet_id)) {
    $matchingLock = $lockItems | Where-Object { $_.packet_id -eq $packet.packet_id } | Select-Object -First 1
    $assignedWorker = if (Is-BlankAssignment $packet.assigned_worker_id) { "UNASSIGNED" } else { $packet.assigned_worker_id }
    $lockStatus = if ($null -eq $matchingLock) { "missing lock record" } else { $matchingLock.claim_status }
    $collisionStatus = if ($null -eq $matchingLock) { "UNKNOWN" } else { $matchingLock.collision_status }

    Write-Host "Packet: $($packet.packet_id)"
    Write-Host "  Name: $($packet.packet_name)"
    Write-Host "  Phase/stage: $($packet.phase) / $($packet.stage)"
    Write-Host "  Priority: $($packet.priority)"
    Write-Host "  Status: $($packet.status)"
    Write-Host "  Assigned worker: $assignedWorker"
    Write-Host "  Lock status: $lockStatus"
    Write-Host "  Collision status: $collisionStatus"
    Write-Host "  Approval required: $($packet.approval_required)"
    Write-Host "  Validator required: $($packet.validator_required)"
    Write-Host "  Allowed paths:"
    Write-PathList -Paths @($packet.allowed_paths)
    Write-Host "  Blocked paths:"
    Write-PathList -Paths @($packet.blocked_paths)
    Write-Host "  Notes: $($packet.notes)"
    Write-Host ""
}

Write-Host "Next safe action: review packet queue status only; use a separate approved APPLY workflow before changing assignments or locks."
