[CmdletBinding()]
param(
    [switch]$Apply,
    [string]$RepoRoot,
    [string]$MarkerPath,
    [string]$QueueIndexPath,
    [string]$LockStatusPath,
    [string]$HeartbeatPath,
    [string]$OutputPath,
    [int]$RestartMarkerMaxAgeSeconds = 172800
)

$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrWhiteSpace($RepoRoot)) {
    $RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
}

if (-not $PSBoundParameters.ContainsKey('MarkerPath')) {
    $MarkerPath = Join-Path $RepoRoot 'control\cycle\last_marker.json'
}

if (-not $PSBoundParameters.ContainsKey('QueueIndexPath')) {
    $QueueIndexPath = Join-Path $RepoRoot 'telemetry\coordination_spine\UNIFIED_QUEUE_INDEX.json'
}

if (-not $PSBoundParameters.ContainsKey('LockStatusPath')) {
    $LockStatusPath = Join-Path $RepoRoot 'telemetry\coordination_spine\UNIFIED_LOCK_STATUS.json'
}

if (-not $PSBoundParameters.ContainsKey('HeartbeatPath')) {
    $HeartbeatPath = Join-Path $RepoRoot 'telemetry\runtime\runtime_heartbeat.json'
}

if (-not $PSBoundParameters.ContainsKey('OutputPath')) {
    $OutputPath = Join-Path $RepoRoot 'telemetry\coordination_spine\RECOVERY_BOOTSTRAP_VIEW.json'
}

function Resolve-AiOsPath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    if ([System.IO.Path]::IsPathRooted($Path)) {
        return [System.IO.Path]::GetFullPath($Path)
    }

    return [System.IO.Path]::GetFullPath((Join-Path $RepoRoot $Path))
}

function Read-AiOsJsonDocument {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    if (-not (Test-Path -LiteralPath $Path)) {
        return $null
    }

    try {
        $raw = Get-Content -LiteralPath $Path -Raw
        if ([string]::IsNullOrWhiteSpace($raw)) {
            return $null
        }

        return $raw | ConvertFrom-Json
    }
    catch {
        return $null
    }
}

function Get-AiOsTextProperty {
    param(
        [object]$InputObject,
        [string[]]$Names
    )

    foreach ($name in $Names) {
        if ($null -ne $InputObject -and $InputObject.PSObject.Properties.Name -contains $name) {
            $value = $InputObject.$name
            if ($null -ne $value -and -not [string]::IsNullOrWhiteSpace([string]$value)) {
                return [string]$value
            }
        }
    }

    return $null
}

function Get-AiOsNormalizedQueueCounts {
    param(
        [object]$QueueDocument
    )

    $counts = [ordered]@{
        QUEUED = 0
        RUNNING = 0
        BLOCKED = 0
        WAITING_APPROVAL = 0
        COMPLETE = 0
        FAILED = 0
        ARCHIVED = 0
    }

    if ($null -eq $QueueDocument) {
        return $counts
    }

    if ($QueueDocument.PSObject.Properties.Name -contains 'normalized_state_counts') {
        foreach ($state in @($counts.Keys)) {
            $value = $QueueDocument.normalized_state_counts.$state
            if ($null -ne $value) {
                $counts[$state] = [int]$value
            }
        }
        return $counts
    }

    return $counts
}

function Get-AiOsMarkerFreshness {
    param(
        [object]$MarkerDocument,
        [int]$MaxAgeSeconds
    )

    if ($null -eq $MarkerDocument) {
        return [pscustomobject]@{
            status = 'MISSING'
            age_seconds = $null
        }
    }

    $timestampText = Get-AiOsTextProperty -InputObject $MarkerDocument -Names @('updated_at_utc', 'updated_at', 'timestamp_utc', 'timestamp')
    if ([string]::IsNullOrWhiteSpace($timestampText)) {
        return [pscustomobject]@{
            status = 'UNKNOWN'
            age_seconds = $null
        }
    }

    try {
        $stamp = [DateTimeOffset]::Parse($timestampText)
        $age = [math]::Floor(((Get-Date).ToUniversalTime() - $stamp.UtcDateTime).TotalSeconds)
        $freshness = if ($age -le $MaxAgeSeconds) { 'FRESH' } else { 'STALE' }
        return [pscustomobject]@{
            status = $freshness
            age_seconds = [int]$age
        }
    }
    catch {
        return [pscustomobject]@{
            status = 'INVALID'
            age_seconds = $null
        }
    }
}

function Get-AiOsHeartbeatStatus {
    param(
        [object]$HeartbeatDocument
    )

    if ($null -eq $HeartbeatDocument) {
        return 'UNAVAILABLE'
    }

    $statusText = Get-AiOsTextProperty -InputObject $HeartbeatDocument -Names @('status', 'supervisor_status', 'mode')
    if ([string]::IsNullOrWhiteSpace($statusText)) {
        return 'UNKNOWN'
    }

    return $statusText.ToUpperInvariant()
}

function Write-AiOsAtomicJson {
    param(
        [Parameter(Mandatory = $true)]
        [string]$DestinationPath,

        [Parameter(Mandatory = $true)]
        [object]$Payload
    )

    $destinationFull = Resolve-AiOsPath -Path $DestinationPath
    $destinationDir = Split-Path -Parent $destinationFull
    if (-not (Test-Path -LiteralPath $destinationDir -PathType Container)) {
        New-Item -ItemType Directory -Path $destinationDir -Force | Out-Null
    }

    $tempPath = Join-Path $destinationDir ('.{0}.tmp' -f [System.IO.Path]::GetRandomFileName())
    try {
        $json = $Payload | ConvertTo-Json -Depth 16
        [System.IO.File]::WriteAllText($tempPath, $json, (New-Object System.Text.UTF8Encoding($false)))
        Move-Item -LiteralPath $tempPath -Destination $destinationFull -Force
    }
    catch {
        if (Test-Path -LiteralPath $tempPath) {
            Remove-Item -LiteralPath $tempPath -Force -ErrorAction SilentlyContinue
        }
        throw
    }
}

$markerDocument = Read-AiOsJsonDocument -Path (Resolve-AiOsPath -Path $MarkerPath)
$queueDocument = Read-AiOsJsonDocument -Path (Resolve-AiOsPath -Path $QueueIndexPath)
$lockDocument = Read-AiOsJsonDocument -Path (Resolve-AiOsPath -Path $LockStatusPath)
$heartbeatDocument = Read-AiOsJsonDocument -Path (Resolve-AiOsPath -Path $HeartbeatPath)

$markerFreshness = Get-AiOsMarkerFreshness -MarkerDocument $markerDocument -MaxAgeSeconds $RestartMarkerMaxAgeSeconds
$queueCounts = Get-AiOsNormalizedQueueCounts -QueueDocument $queueDocument
$heartbeatStatus = Get-AiOsHeartbeatStatus -HeartbeatDocument $heartbeatDocument

$markerPresent = $null -ne $markerDocument
$queueIndexPresent = $null -ne $queueDocument
$lockStatusPresent = $null -ne $lockDocument

$heldLocksCount = 0
$staleLocksCount = 0
$collisionCount = 0
if ($lockStatusPresent) {
    if ($lockDocument.PSObject.Properties.Name -contains 'held_locks_count') {
        $heldLocksCount = [int]$lockDocument.held_locks_count
    }
    if ($lockDocument.PSObject.Properties.Name -contains 'stale_locks_count') {
        $staleLocksCount = [int]$lockDocument.stale_locks_count
    }
    if ($lockDocument.PSObject.Properties.Name -contains 'collision_count') {
        $collisionCount = [int]$lockDocument.collision_count
    }
}

$activePacketCount = [int]$queueCounts.RUNNING
$blockedPacketCount = [int]$queueCounts.BLOCKED

$sourceReaders = @(
    [pscustomobject]@{
        source = 'last_marker.json'
        path = Resolve-AiOsPath -Path $MarkerPath
        exists = $markerPresent
        records_seen = if ($markerPresent) { 1 } else { 0 }
    },
    [pscustomobject]@{
        source = 'UNIFIED_QUEUE_INDEX.json'
        path = Resolve-AiOsPath -Path $QueueIndexPath
        exists = $queueIndexPresent
        records_seen = if ($queueIndexPresent -and $queueDocument.PSObject.Properties.Name -contains 'packet_count') { [int]$queueDocument.packet_count } else { 0 }
    },
    [pscustomobject]@{
        source = 'UNIFIED_LOCK_STATUS.json'
        path = Resolve-AiOsPath -Path $LockStatusPath
        exists = $lockStatusPresent
        records_seen = if ($lockStatusPresent) { $heldLocksCount + $staleLocksCount + $collisionCount } else { 0 }
    },
    [pscustomobject]@{
        source = 'runtime_heartbeat.json'
        path = Resolve-AiOsPath -Path $HeartbeatPath
        exists = ($null -ne $heartbeatDocument)
        records_seen = if ($null -ne $heartbeatDocument) { 1 } else { 0 }
    }
)

$warnings = [System.Collections.Generic.List[string]]::new()
$blockers = [System.Collections.Generic.List[string]]::new()

if (-not $markerPresent) {
    $warnings.Add('marker_missing') | Out-Null
}
elseif ($markerFreshness.status -eq 'UNKNOWN' -or $markerFreshness.status -eq 'INVALID') {
    $warnings.Add('marker_unreadable') | Out-Null
}
elseif ($markerFreshness.status -eq 'STALE') {
    $blockers.Add('marker_stale') | Out-Null
}

if (-not $queueIndexPresent) {
    $warnings.Add('queue_index_missing') | Out-Null
}

if (-not $lockStatusPresent) {
    $warnings.Add('lock_status_missing') | Out-Null
}
else {
    if ($heldLocksCount -gt 0) {
        $blockers.Add('held_locks_present') | Out-Null
    }
    if ($staleLocksCount -gt 0) {
        $warnings.Add('stale_locks_present') | Out-Null
    }
    if ($collisionCount -gt 0) {
        $blockers.Add('lock_collision_present') | Out-Null
    }
}

if ($heartbeatStatus -eq 'UNAVAILABLE') {
    $warnings.Add('heartbeat_unavailable') | Out-Null
}
elseif ($heartbeatStatus -in @('DEGRADED', 'WARNING', 'WARN', 'ERROR')) {
    $warnings.Add('heartbeat_degraded') | Out-Null
}

$recoveryReadiness = 'READY_KNOWN'
if ($blockers.Count -gt 0) {
    $recoveryReadiness = 'BLOCKED'
}
elseif ($warnings.Count -gt 0) {
    $recoveryReadiness = 'REVIEW_REQUIRED'
}

$payload = [ordered]@{
    schema = 'AIOS_RECOVERY_BOOTSTRAP_VIEW.v1'
    system = 'AI_OS'
    mode = 'DRY_RUN'
    generated_at = (Get-Date).ToUniversalTime().ToString('o')
    repo_root = $RepoRoot
    source_readers = $sourceReaders
    marker_present = $markerPresent
    marker_path = Resolve-AiOsPath -Path $MarkerPath
    marker_freshness_status = $markerFreshness.status
    marker_age_seconds = $markerFreshness.age_seconds
    queue_index_present = $queueIndexPresent
    queue_counts = $queueCounts
    lock_status_present = $lockStatusPresent
    held_locks_count = $heldLocksCount
    stale_locks_count = $staleLocksCount
    collision_count = $collisionCount
    active_packet_count = $activePacketCount
    blocked_packet_count = $blockedPacketCount
    heartbeat_status = $heartbeatStatus
    recovery_readiness = $recoveryReadiness
    blockers = @($blockers)
    warnings = @($warnings)
    write_behavior = 'telemetry_only'
}

$json = $payload | ConvertTo-Json -Depth 16

if ($Apply) {
    $defaultOutput = Resolve-AiOsPath -Path 'telemetry\coordination_spine\RECOVERY_BOOTSTRAP_VIEW.json'
    $resolvedOutput = Resolve-AiOsPath -Path $OutputPath
    if ($resolvedOutput -ne $defaultOutput) {
        throw 'Apply mode may only write telemetry\coordination_spine\RECOVERY_BOOTSTRAP_VIEW.json'
    }

    Write-AiOsAtomicJson -DestinationPath $defaultOutput -Payload $payload
}

$json
