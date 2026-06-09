[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string] $PacketRoot = "automation/orchestration/work_packets",

    [Parameter(Mandatory = $false)]
    [switch] $Apply,

    [Parameter(Mandatory = $false)]
    [switch] $OutputJson
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptName = Split-Path -Leaf $PSCommandPath
$repoRoot = (Get-Location).Path
$telemetryPath = Join-Path $repoRoot "telemetry/coordination_spine/UNIFIED_QUEUE_INDEX.json"
$normalizedStateOrder = @("QUEUED", "RUNNING", "BLOCKED", "WAITING_APPROVAL", "COMPLETE", "FAILED", "ARCHIVED")

$stateMap = @{
    "ACTIVE" = "QUEUED"
    "ASSIGNED" = "RUNNING"
    "AWAITING_APPROVAL" = "WAITING_APPROVAL"
    "APPROVAL_NEEDED" = "WAITING_APPROVAL"
    "ARCHIVED" = "ARCHIVED"
    "BLOCKED" = "BLOCKED"
    "COMPLETE" = "COMPLETE"
    "COMPLETED" = "COMPLETE"
    "DONE" = "COMPLETE"
    "ERROR" = "FAILED"
    "EXPIRED" = "ARCHIVED"
    "FAILED" = "FAILED"
    "FAIL" = "FAILED"
    "PENDING" = "QUEUED"
    "PENDING_APPROVAL" = "WAITING_APPROVAL"
    "PROPOSED" = "QUEUED"
    "QUEUED" = "QUEUED"
    "RUNNING" = "RUNNING"
    "STALE" = "BLOCKED"
    "VALIDATING" = "RUNNING"
    "WAITING_APPROVAL" = "WAITING_APPROVAL"
    "WAITING_REVIEW" = "WAITING_APPROVAL"
    "NEEDS_APPROVAL" = "WAITING_APPROVAL"
    "APPROVAL_REQUIRED" = "WAITING_APPROVAL"
}

function Resolve-AiOsPath {
    param(
        [Parameter(Mandatory = $true)]
        [string] $Path
    )

    if ([System.IO.Path]::IsPathRooted($Path)) {
        return [System.IO.Path]::GetFullPath($Path)
    }

    return [System.IO.Path]::GetFullPath((Join-Path $repoRoot $Path))
}

function Normalize-AiOsStateToken {
    param(
        [Parameter(Mandatory = $true)]
        [string] $State
    )

    $token = ($State.Trim() -replace "[^A-Za-z0-9]+", "_").Trim("_").ToUpperInvariant()
    if ([string]::IsNullOrWhiteSpace($token)) {
        return $null
    }

    return $token
}

function Resolve-AiOsUnifiedQueueState {
    param(
        [Parameter(Mandatory = $false)]
        [string] $State
    )

    if ([string]::IsNullOrWhiteSpace($State)) {
        return $null
    }

    $token = Normalize-AiOsStateToken -State $State
    if ($null -eq $token) {
        return $null
    }

    if ($stateMap.ContainsKey($token)) {
        return [pscustomobject]@{
            source_state_token = $token
            normalized_state = $stateMap[$token]
        }
    }

    return [pscustomobject]@{
        source_state_token = $token
        normalized_state = $null
    }
}

function Read-AiOsPacketRecord {
    param(
        [Parameter(Mandatory = $true)]
        [System.IO.FileInfo] $File,

        [Parameter(Mandatory = $true)]
        [string] $FolderState
    )

    $packet = Get-Content -LiteralPath $File.FullName -Raw | ConvertFrom-Json
    $packetStatus = if ($packet.PSObject.Properties.Name -contains "status") { [string] $packet.status } else { "" }
    $sourceState = if (-not [string]::IsNullOrWhiteSpace($packetStatus)) { $packetStatus } else { $FolderState }
    $resolved = Resolve-AiOsUnifiedQueueState -State $sourceState
    $packetId = if ($packet.PSObject.Properties.Name -contains "packet_id") { [string] $packet.packet_id } else { "" }
    $title = if ($packet.PSObject.Properties.Name -contains "title") { [string] $packet.title } else { "" }
    $ownerLane = if ($packet.PSObject.Properties.Name -contains "owner_lane") { [string] $packet.owner_lane } else { "" }
    $assignedWorker = if ($packet.PSObject.Properties.Name -contains "assigned_worker") { [string] $packet.assigned_worker } else { "" }
    $sourceReason = if ($resolved.source_state_token -eq "STALE") { "STALE" } else { "" }

    return [pscustomobject]@{
        packet_id = $packetId
        title = $title
        owner_lane = $ownerLane
        assigned_worker = $assignedWorker
        folder_state = $FolderState
        packet_status = $packetStatus
        source_state = $sourceState
        source_state_token = $resolved.source_state_token
        normalized_state = $resolved.normalized_state
        source_reason = $sourceReason
        source_state_origin = if (-not [string]::IsNullOrWhiteSpace($packetStatus)) { "packet.status" } else { "folder_state" }
        source_file = $File.FullName
    }
}

function New-AiOsUnifiedQueueIndexPayload {
    param(
        [Parameter(Mandatory = $true)]
        [string] $ResolvedPacketRoot
    )

    $folders = @("active", "blocked", "complete")
    $records = @()

    foreach ($folder in $folders) {
        $folderPath = Join-Path $ResolvedPacketRoot $folder
        if (-not (Test-Path -LiteralPath $folderPath -PathType Container)) {
            continue
        }

        Get-ChildItem -LiteralPath $folderPath -Filter "*.json" -File | Sort-Object Name | ForEach-Object {
            $records += @(Read-AiOsPacketRecord -File $_ -FolderState $folder)
        }
    }

    $sourceStateCounts = [ordered]@{}
    foreach ($record in $records) {
        $token = $record.source_state_token
        if ([string]::IsNullOrWhiteSpace($token)) {
            continue
        }

        if (-not $sourceStateCounts.Contains($token)) {
            $sourceStateCounts[$token] = 0
        }

        $sourceStateCounts[$token] = [int] $sourceStateCounts[$token] + 1
    }

    $normalizedStateCounts = [ordered]@{}
    foreach ($state in $normalizedStateOrder) {
        $normalizedStateCounts[$state] = @($records | Where-Object { $_.normalized_state -eq $state }).Count
    }

    $unmappedStates = @(
        $records |
            Where-Object { [string]::IsNullOrWhiteSpace($_.normalized_state) -and -not [string]::IsNullOrWhiteSpace($_.source_state_token) } |
            Select-Object -ExpandProperty source_state_token -Unique |
            Sort-Object
    )

    return [pscustomobject]@{
        schema = "AIOS_UNIFIED_QUEUE_INDEX.v1"
        system = "AI_OS"
        mode = "DRY_RUN"
        generated_at_utc = (Get-Date).ToUniversalTime().ToString("o")
        repo_root = $repoRoot
        packet_root = $ResolvedPacketRoot
        scanned_folders = $folders
        packet_count = $records.Count
        normalized_state_order = $normalizedStateOrder
        normalized_state_counts = $normalizedStateCounts
        source_state_counts = $sourceStateCounts
        mapping_table = [ordered]@{
            ACTIVE = "QUEUED"
            ASSIGNED = "RUNNING"
            AWAITING_APPROVAL = "WAITING_APPROVAL"
            APPROVAL_NEEDED = "WAITING_APPROVAL"
            ARCHIVED = "ARCHIVED"
            BLOCKED = "BLOCKED"
            COMPLETE = "COMPLETE"
            COMPLETED = "COMPLETE"
            DONE = "COMPLETE"
            ERROR = "FAILED"
            EXPIRED = "ARCHIVED"
            FAILED = "FAILED"
            FAIL = "FAILED"
            PENDING = "QUEUED"
            PENDING_APPROVAL = "WAITING_APPROVAL"
            PROPOSED = "QUEUED"
            QUEUED = "QUEUED"
            RUNNING = "RUNNING"
            STALE = "BLOCKED"
            VALIDATING = "RUNNING"
            WAITING_APPROVAL = "WAITING_APPROVAL"
            WAITING_REVIEW = "WAITING_APPROVAL"
            NEEDS_APPROVAL = "WAITING_APPROVAL"
        }
        unmapped_states = $unmappedStates
        records = @($records)
    }
}

function Write-AiOsAtomicJson {
    param(
        [Parameter(Mandatory = $true)]
        [string] $DestinationPath,

        [Parameter(Mandatory = $true)]
        [object] $Payload
    )

    $destinationFull = Resolve-AiOsPath -Path $DestinationPath
    $destinationDir = Split-Path -Parent $destinationFull
    if (-not (Test-Path -LiteralPath $destinationDir -PathType Container)) {
        New-Item -ItemType Directory -Path $destinationDir -Force | Out-Null
    }

    $tempPath = Join-Path $destinationDir (".{0}.tmp" -f [System.IO.Path]::GetRandomFileName())
    try {
        $json = $Payload | ConvertTo-Json -Depth 12
        [System.IO.File]::WriteAllText($tempPath, $json, (New-Object System.Text.UTF8Encoding($false)))
        Move-Item -LiteralPath $tempPath -Destination $destinationFull -Force
    } catch {
        if (Test-Path -LiteralPath $tempPath) {
            Remove-Item -LiteralPath $tempPath -Force -ErrorAction SilentlyContinue
        }
        throw
    }
}

$resolvedPacketRoot = Resolve-AiOsPath -Path $PacketRoot
$payload = New-AiOsUnifiedQueueIndexPayload -ResolvedPacketRoot $resolvedPacketRoot

if ($Apply) {
    Write-AiOsAtomicJson -DestinationPath $telemetryPath -Payload $payload
}

if ($OutputJson) {
    $payload | ConvertTo-Json -Depth 12
} else {
    Write-Host "AI_OS Unified Queue Index" -ForegroundColor Cyan
    Write-Host "Mode: DRY_RUN"
    Write-Host "Source root: $resolvedPacketRoot"
    Write-Host "Packets scanned: $($payload.packet_count)"
    Write-Host "Normalized counts:"
    foreach ($state in $normalizedStateOrder) {
        Write-Host ("  {0}: {1}" -f $state, $payload.normalized_state_counts[$state])
    }
    if ($payload.unmapped_states.Count -gt 0) {
        Write-Host "Unmapped states: $(@($payload.unmapped_states) -join ', ')"
    } else {
        Write-Host "Unmapped states: NONE"
    }
    Write-Host "Commit performed: NO"
    Write-Host "Push performed: NO"
}
