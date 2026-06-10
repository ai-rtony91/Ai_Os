[CmdletBinding()]
param(
    [string]$RepoRoot = (Get-Location).Path,
    [string]$QueueIndexPath = "telemetry/coordination_spine/UNIFIED_QUEUE_INDEX.json",
    [string]$LockStatusPath = "telemetry/coordination_spine/UNIFIED_LOCK_STATUS.json",
    [string]$RecoveryViewPath = "telemetry/coordination_spine/RECOVERY_BOOTSTRAP_VIEW.json",
    [string]$LeadDispatchViewPath = "telemetry/coordination_spine/LEAD_DISPATCH_VIEW.json",
    [string]$PacketFactoryViewPath = "telemetry/coordination_spine/PACKET_FACTORY_VIEW.json",
    [string]$Module5aCloseoutPath = "Reports/coordination_spine/module5a_scope_closeout.md",
    [string]$Module5bDesignPath = "Reports/coordination_spine/module5b_dry_run_design.md",
    [string]$SpineOrchestratorDesignPath = "Reports/coordination_spine/spine_orchestrator_dry_run_design.md",
    [string]$PhaseCloseoutPath = "Reports/coordination_spine/coordination_spine_phase_closeout.md",
    [string]$OutputPath = "telemetry/coordination_spine/COORDINATION_SPINE_VIEW.json",
    [switch]$Apply
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Resolve-AiOsPath {
    param([Parameter(Mandatory = $true)][string]$Path)

    if ([System.IO.Path]::IsPathRooted($Path)) {
        return [System.IO.Path]::GetFullPath($Path)
    }

    return [System.IO.Path]::GetFullPath((Join-Path $RepoRoot $Path))
}

function Get-AiOsFileFreshness {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [int]$MaxAgeHours = 48
    )

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return [pscustomobject]@{
            status = "MISSING"
            age_hours = $null
        }
    }

    try {
        $item = Get-Item -LiteralPath $Path
        $ageHours = [Math]::Round(((Get-Date).ToUniversalTime() - $item.LastWriteTimeUtc).TotalHours, 2)
        $status = if ($ageHours -gt $MaxAgeHours) { "STALE" } else { "FRESH" }

        return [pscustomobject]@{
            status = $status
            age_hours = $ageHours
        }
    }
    catch {
        return [pscustomobject]@{
            status = "UNREADABLE"
            age_hours = $null
        }
    }
}

function Read-AiOsJsonDocument {
    param([Parameter(Mandatory = $true)][string]$Path)

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return $null
    }

    $raw = Get-Content -LiteralPath $Path -Raw
    if ([string]::IsNullOrWhiteSpace($raw)) {
        return $null
    }

    return $raw | ConvertFrom-Json
}

function Read-AiOsTextDocument {
    param([Parameter(Mandatory = $true)][string]$Path)

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return $null
    }

    $raw = Get-Content -LiteralPath $Path -Raw
    if ([string]::IsNullOrWhiteSpace($raw)) {
        return $null
    }

    return $raw
}

function Get-AiOsSourceReader {
    param(
        [Parameter(Mandatory = $true)][string]$Source,
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Kind,
        [int]$RecordsSeen = 0,
        [string]$Status = "PRESENT",
        [string]$FreshnessStatus = "FRESH"
    )

    [pscustomobject]@{
        source = $Source
        path = $Path
        kind = $Kind
        present = ($Status -eq "PRESENT")
        freshness_status = $FreshnessStatus
        records_seen = $RecordsSeen
        status = $Status
    }
}

function Merge-AiOsStrings {
    param([object[]]$Items)

    $list = [System.Collections.Generic.List[string]]::new()
    foreach ($item in @($Items)) {
        if ($null -eq $item) {
            continue
        }

        foreach ($entry in @($item)) {
            $text = [string]$entry
            if ([string]::IsNullOrWhiteSpace($text)) {
                continue
            }

            [void]$list.Add($text)
        }
    }

    return @($list | Sort-Object -Unique)
}

function Get-AiOsWorstStatus {
    param([string[]]$Statuses)

    if ($Statuses -contains "BLOCKED") {
        return "BLOCKED"
    }

    if ($Statuses -contains "REVIEW_REQUIRED") {
        return "REVIEW_REQUIRED"
    }

    if ($Statuses -contains "READY_TO_DRAFT") {
        return "READY_TO_DRAFT"
    }

    return "SAFE_NO_WORK"
}

function Read-AiOsQueueSummary {
    param([Parameter(Mandatory = $true)][string]$Path)

    $fullPath = Resolve-AiOsPath -Path $Path
    $freshness = Get-AiOsFileFreshness -Path $fullPath
    if ($freshness.status -in @("MISSING", "UNREADABLE", "STALE")) {
        return [pscustomobject]@{
            source = "UNIFIED_QUEUE_INDEX.json"
            path = $fullPath
            present = $false
            freshness_status = $freshness.status
            freshness_age_hours = $freshness.age_hours
            packet_count = 0
            normalized_state_counts = @{}
            source_state_counts = @{}
            safety_status = "REVIEW_REQUIRED"
            blockers = @("queue_source_$($freshness.status.ToLowerInvariant())")
            warnings = @()
            write_behavior = "telemetry_only"
        }
    }

    try {
        $doc = Read-AiOsJsonDocument -Path $fullPath
        $counts = if ($doc.PSObject.Properties.Name -contains "normalized_state_counts") { $doc.normalized_state_counts } else { $null }
        $packetCount = if ($doc.PSObject.Properties.Name -contains "packet_count") { [int]$doc.packet_count } else { 0 }
        $blockedCount = if ($null -ne $counts -and $counts.PSObject.Properties.Name -contains "BLOCKED") { [int]$counts.BLOCKED } else { 0 }
        $waitingCount = if ($null -ne $counts -and $counts.PSObject.Properties.Name -contains "WAITING_APPROVAL") { [int]$counts.WAITING_APPROVAL } else { 0 }
        $sourceCounts = if ($doc.PSObject.Properties.Name -contains "source_state_counts") { $doc.source_state_counts } else { @{} }

        $status = if ($blockedCount -gt 0) { "BLOCKED" } elseif ($waitingCount -gt 0) { "REVIEW_REQUIRED" } elseif ($packetCount -eq 0) { "SAFE_NO_WORK" } else { "READY_TO_DRAFT" }
        $blockers = @()
        $warnings = @()
        if ($blockedCount -gt 0) { $blockers += "queue_blocked" }
        if ($waitingCount -gt 0) { $warnings += "queue_waiting_approval" }

        return [pscustomobject]@{
            source = "UNIFIED_QUEUE_INDEX.json"
            path = $fullPath
            present = $true
            freshness_status = $freshness.status
            freshness_age_hours = $freshness.age_hours
            packet_count = $packetCount
            normalized_state_counts = $counts
            source_state_counts = $sourceCounts
            safety_status = $status
            blockers = @($blockers)
            warnings = @($warnings)
            write_behavior = "telemetry_only"
        }
    }
    catch {
        return [pscustomobject]@{
            source = "UNIFIED_QUEUE_INDEX.json"
            path = $fullPath
            present = $false
            freshness_status = "UNREADABLE"
            freshness_age_hours = $null
            packet_count = 0
            normalized_state_counts = @{}
            source_state_counts = @{}
            safety_status = "REVIEW_REQUIRED"
            blockers = @("queue_source_unreadable")
            warnings = @()
            write_behavior = "telemetry_only"
        }
    }
}

function Read-AiOsLockSummary {
    param([Parameter(Mandatory = $true)][string]$Path)

    $fullPath = Resolve-AiOsPath -Path $Path
    $freshness = Get-AiOsFileFreshness -Path $fullPath
    if ($freshness.status -in @("MISSING", "UNREADABLE", "STALE")) {
        return [pscustomobject]@{
            source = "UNIFIED_LOCK_STATUS.json"
            path = $fullPath
            present = $false
            freshness_status = $freshness.status
            freshness_age_hours = $freshness.age_hours
            held_locks_count = 0
            stale_locks_count = 0
            collision_count = 0
            safety_status = "REVIEW_REQUIRED"
            blockers = @("lock_source_$($freshness.status.ToLowerInvariant())")
            warnings = @()
            write_behavior = "telemetry_only"
        }
    }

    try {
        $doc = Read-AiOsJsonDocument -Path $fullPath
        $held = if ($doc.PSObject.Properties.Name -contains "held_locks_count") { [int]$doc.held_locks_count } else { 0 }
        $stale = if ($doc.PSObject.Properties.Name -contains "stale_locks_count") { [int]$doc.stale_locks_count } else { 0 }
        $collision = if ($doc.PSObject.Properties.Name -contains "collision_count") { [int]$doc.collision_count } else { 0 }
        $status = if ($doc.PSObject.Properties.Name -contains "safety_status") { [string]$doc.safety_status } else { "UNKNOWN" }
        $blockers = @()
        $warnings = @()

        if ($held -gt 0) { $blockers += "held_locks_present" }
        if ($collision -gt 0) { $blockers += "lock_collision_present" }
        if ($stale -gt 0) { $warnings += "stale_locks_present" }
        if ($status -eq "UNKNOWN") { $warnings += "lock_safety_status_unknown" }

        if ($blockers.Count -gt 0) {
            $status = "BLOCKED"
        }
        elseif ($status -eq "PASS") {
            $status = if ($warnings.Count -gt 0) { "REVIEW_REQUIRED" } else { "SAFE_NO_WORK" }
        }
        elseif ($status -ne "REVIEW_REQUIRED" -and $status -ne "BLOCKED") {
            $status = "REVIEW_REQUIRED"
        }

        return [pscustomobject]@{
            source = "UNIFIED_LOCK_STATUS.json"
            path = $fullPath
            present = $true
            freshness_status = $freshness.status
            freshness_age_hours = $freshness.age_hours
            held_locks_count = $held
            stale_locks_count = $stale
            collision_count = $collision
            safety_status = $status
            blockers = @($blockers)
            warnings = @($warnings)
            write_behavior = "telemetry_only"
        }
    }
    catch {
        return [pscustomobject]@{
            source = "UNIFIED_LOCK_STATUS.json"
            path = $fullPath
            present = $false
            freshness_status = "UNREADABLE"
            freshness_age_hours = $null
            held_locks_count = 0
            stale_locks_count = 0
            collision_count = 0
            safety_status = "REVIEW_REQUIRED"
            blockers = @("lock_source_unreadable")
            warnings = @()
            write_behavior = "telemetry_only"
        }
    }
}

function Read-AiOsRecoverySummary {
    param([Parameter(Mandatory = $true)][string]$Path)

    $fullPath = Resolve-AiOsPath -Path $Path
    if (-not (Test-Path -LiteralPath $fullPath -PathType Leaf)) {
        return [pscustomobject]@{
            source = "RECOVERY_BOOTSTRAP_VIEW.json"
            path = $fullPath
            present = $false
            freshness_status = "MISSING"
            freshness_age_hours = $null
            recovery_readiness = "REVIEW_REQUIRED"
            blockers = @("recovery_source_missing")
            warnings = @()
            heartbeat_status = "UNKNOWN"
            write_behavior = "telemetry_only"
            safety_status = "REVIEW_REQUIRED"
        }
    }

    try {
        $raw = Get-Content -LiteralPath $fullPath -Raw
        if ([string]::IsNullOrWhiteSpace($raw)) {
            return [pscustomobject]@{
                source = "RECOVERY_BOOTSTRAP_VIEW.json"
                path = $fullPath
                present = $false
                freshness_status = "UNREADABLE"
                freshness_age_hours = $null
                recovery_readiness = "REVIEW_REQUIRED"
                blockers = @("recovery_source_unreadable")
                warnings = @()
                heartbeat_status = "UNKNOWN"
                write_behavior = "telemetry_only"
                safety_status = "REVIEW_REQUIRED"
            }
        }

        $ageHours = [Math]::Round(((Get-Date).ToUniversalTime() - [System.IO.File]::GetLastWriteTimeUtc($fullPath)).TotalHours, 2)
        $freshnessStatus = if ($ageHours -gt 48) { "STALE" } else { "FRESH" }
        if ($freshnessStatus -eq "STALE") {
            return [pscustomobject]@{
                source = "RECOVERY_BOOTSTRAP_VIEW.json"
                path = $fullPath
                present = $false
                freshness_status = $freshnessStatus
                freshness_age_hours = $ageHours
                recovery_readiness = "REVIEW_REQUIRED"
                blockers = @("recovery_source_stale")
                warnings = @()
                heartbeat_status = "UNKNOWN"
                write_behavior = "telemetry_only"
                safety_status = "REVIEW_REQUIRED"
            }
        }

        $doc = $raw | ConvertFrom-Json
        if ($null -eq $doc) {
            return [pscustomobject]@{
                source = "RECOVERY_BOOTSTRAP_VIEW.json"
                path = $fullPath
                present = $false
                freshness_status = "UNREADABLE"
                freshness_age_hours = $ageHours
                recovery_readiness = "REVIEW_REQUIRED"
                blockers = @("recovery_source_unreadable")
                warnings = @()
                heartbeat_status = "UNKNOWN"
                write_behavior = "telemetry_only"
                safety_status = "REVIEW_REQUIRED"
            }
        }

        if (-not ($doc.PSObject.Properties.Name -contains "recovery_readiness") -or -not ($doc.PSObject.Properties.Name -contains "heartbeat_status")) {
            return [pscustomobject]@{
                source = "RECOVERY_BOOTSTRAP_VIEW.json"
                path = $fullPath
                present = $false
                freshness_status = $freshnessStatus
                freshness_age_hours = $ageHours
                recovery_readiness = "REVIEW_REQUIRED"
                blockers = @("recovery_source_unreadable")
                warnings = @()
                heartbeat_status = if ($doc.PSObject.Properties.Name -contains "heartbeat_status") { [string]$doc.heartbeat_status } else { "UNKNOWN" }
                write_behavior = "telemetry_only"
                safety_status = "REVIEW_REQUIRED"
            }
        }

        $readiness = [string]$doc.recovery_readiness
        if ($doc.PSObject.Properties.Name -contains "blockers") {
            if ($null -eq $doc.blockers) {
                $blockers = @()
            }
            else {
                $blockers = @($doc.blockers)
            }
        }
        else {
            $blockers = @()
        }

        if ($doc.PSObject.Properties.Name -contains "warnings") {
            if ($null -eq $doc.warnings) {
                $warnings = @()
            }
            else {
                $warnings = @($doc.warnings)
            }
        }
        else {
            $warnings = @()
        }
        $heartbeat = [string]$doc.heartbeat_status

        $status = switch ($readiness) {
            "BLOCKED" { "BLOCKED" }
            "REVIEW_REQUIRED" { "REVIEW_REQUIRED" }
            "READY_KNOWN" { if ($blockers.Count -gt 0 -or $warnings.Count -gt 0) { "REVIEW_REQUIRED" } else { "SAFE_NO_WORK" } }
            default { "REVIEW_REQUIRED" }
        }

        return [pscustomobject]@{
            source = "RECOVERY_BOOTSTRAP_VIEW.json"
            path = $fullPath
            present = $true
            freshness_status = $freshnessStatus
            freshness_age_hours = $ageHours
            recovery_readiness = $readiness
            blockers = @($blockers)
            warnings = @($warnings)
            heartbeat_status = $heartbeat
            write_behavior = "telemetry_only"
            safety_status = $status
        }
    }
    catch {
        return [pscustomobject]@{
            source = "RECOVERY_BOOTSTRAP_VIEW.json"
            path = $fullPath
            present = $false
            freshness_status = "UNREADABLE"
            freshness_age_hours = $null
            recovery_readiness = "REVIEW_REQUIRED"
            blockers = @("recovery_source_unreadable")
            warnings = @()
            heartbeat_status = "UNKNOWN"
            write_behavior = "telemetry_only"
            safety_status = "REVIEW_REQUIRED"
        }
    }
}

function Read-AiOsLeadDispatchSummary {
    param([Parameter(Mandatory = $true)][string]$Path)

    $fullPath = Resolve-AiOsPath -Path $Path
    $freshness = Get-AiOsFileFreshness -Path $fullPath
    if ($freshness.status -in @("MISSING", "UNREADABLE", "STALE")) {
        return [pscustomobject]@{
            source = "LEAD_DISPATCH_VIEW.json"
            path = $fullPath
            present = $false
            freshness_status = $freshness.status
            freshness_age_hours = $freshness.age_hours
            dispatcher_safety_verdict = "REVIEW_REQUIRED"
            blocked_reason = "lead_dispatch_source_$($freshness.status.ToLowerInvariant())"
            depends_on_t2b = $true
            next_safe_action = "Refresh lead dispatch telemetry before any write-path work."
            write_behavior = "telemetry_only"
            safety_status = "REVIEW_REQUIRED"
            blockers = @("lead_dispatch_source_$($freshness.status.ToLowerInvariant())")
            warnings = @()
        }
    }

    try {
        $doc = Read-AiOsJsonDocument -Path $fullPath
        $verdict = if ($doc.PSObject.Properties.Name -contains "dispatcher_safety_verdict") { [string]$doc.dispatcher_safety_verdict } else { "UNKNOWN" }
        $reason = if ($doc.PSObject.Properties.Name -contains "blocked_reason") { [string]$doc.blocked_reason } else { "" }
        $nextAction = if ($doc.PSObject.Properties.Name -contains "next_safe_action") { [string]$doc.next_safe_action } else { "Review telemetry before any write-path work." }
        $dependsOnT2B = if ($doc.PSObject.Properties.Name -contains "depends_on_t2b") { [bool]$doc.depends_on_t2b } else { $true }

        $status = switch ($verdict) {
            "BLOCKED" { "BLOCKED" }
            "REVIEW_REQUIRED" { "REVIEW_REQUIRED" }
            "SAFE_NO_WORK" { "SAFE_NO_WORK" }
            default { "REVIEW_REQUIRED" }
        }

        $blockers = @()
        if ($status -eq "BLOCKED") {
            if (-not [string]::IsNullOrWhiteSpace($reason)) {
                $blockers += $reason
            }
            else {
                $blockers += "lead_dispatch_blocked"
            }
        }

        return [pscustomobject]@{
            source = "LEAD_DISPATCH_VIEW.json"
            path = $fullPath
            present = $true
            freshness_status = $freshness.status
            freshness_age_hours = $freshness.age_hours
            dispatcher_safety_verdict = $verdict
            blocked_reason = $reason
            depends_on_t2b = $dependsOnT2B
            next_safe_action = $nextAction
            write_behavior = "telemetry_only"
            safety_status = $status
            blockers = @($blockers)
            warnings = @()
        }
    }
    catch {
        return [pscustomobject]@{
            source = "LEAD_DISPATCH_VIEW.json"
            path = $fullPath
            present = $false
            freshness_status = "UNREADABLE"
            freshness_age_hours = $null
            dispatcher_safety_verdict = "REVIEW_REQUIRED"
            blocked_reason = "lead_dispatch_source_unreadable"
            depends_on_t2b = $true
            next_safe_action = "Refresh lead dispatch telemetry before any write-path work."
            write_behavior = "telemetry_only"
            safety_status = "REVIEW_REQUIRED"
            blockers = @("lead_dispatch_source_unreadable")
            warnings = @()
        }
    }
}

function Read-AiOsPacketFactorySummary {
    param([Parameter(Mandatory = $true)][string]$Path)

    $fullPath = Resolve-AiOsPath -Path $Path
    $freshness = Get-AiOsFileFreshness -Path $fullPath
    if ($freshness.status -eq "MISSING") {
        return [pscustomobject]@{
            source = "PACKET_FACTORY_VIEW.json"
            path = $fullPath
            present = $false
            freshness_status = "MISSING"
            freshness_age_hours = $null
            packet_factory_safety_verdict = "REVIEW_REQUIRED"
            write_behavior = "telemetry_only"
            write_path_enabled = $false
            blockers = @("packet_factory_source_missing")
            warnings = @()
            safety_status = "REVIEW_REQUIRED"
        }
    }

    if ($freshness.status -in @("UNREADABLE", "STALE")) {
        return [pscustomobject]@{
            source = "PACKET_FACTORY_VIEW.json"
            path = $fullPath
            present = $false
            freshness_status = $freshness.status
            freshness_age_hours = $freshness.age_hours
            packet_factory_safety_verdict = "REVIEW_REQUIRED"
            write_behavior = "telemetry_only"
            write_path_enabled = $false
            blockers = @("packet_factory_source_$($freshness.status.ToLowerInvariant())")
            warnings = @()
            safety_status = "REVIEW_REQUIRED"
        }
    }

    try {
        $doc = Read-AiOsJsonDocument -Path $fullPath
        $verdict = if ($doc.PSObject.Properties.Name -contains "packet_factory_safety_verdict") { [string]$doc.packet_factory_safety_verdict } else { "REVIEW_REQUIRED" }
        $warnings = @()
        $blockers = @()

        if ($verdict -eq "BLOCKED") {
            $blockers += "packet_factory_blocked"
        }
        elseif ($verdict -eq "REVIEW_REQUIRED") {
            $warnings += "packet_factory_review_required"
        }

        if ($doc.PSObject.Properties.Name -contains "missing_required_fields" -and @($doc.missing_required_fields).Count -gt 0) {
            $warnings += "packet_factory_missing_required_fields"
        }
        if ($doc.PSObject.Properties.Name -contains "approval_required_items" -and @($doc.approval_required_items).Count -gt 0) {
            $blockers += "packet_factory_approval_required"
        }

        $status = if ($blockers.Count -gt 0) { "BLOCKED" } elseif ($verdict -eq "SAFE_NO_WORK") { "SAFE_NO_WORK" } else { "REVIEW_REQUIRED" }

        return [pscustomobject]@{
            source = "PACKET_FACTORY_VIEW.json"
            path = $fullPath
            present = $true
            freshness_status = $freshness.status
            freshness_age_hours = $freshness.age_hours
            packet_factory_safety_verdict = $verdict
            write_behavior = if ($doc.PSObject.Properties.Name -contains "write_behavior") { [string]$doc.write_behavior } else { "telemetry_only" }
            write_path_enabled = if ($doc.PSObject.Properties.Name -contains "write_path_enabled") { [bool]$doc.write_path_enabled } else { $false }
            blockers = @($blockers)
            warnings = @($warnings)
            safety_status = $status
        }
    }
    catch {
        return [pscustomobject]@{
            source = "PACKET_FACTORY_VIEW.json"
            path = $fullPath
            present = $false
            freshness_status = "UNREADABLE"
            freshness_age_hours = $null
            packet_factory_safety_verdict = "REVIEW_REQUIRED"
            write_behavior = "telemetry_only"
            write_path_enabled = $false
            blockers = @("packet_factory_source_unreadable")
            warnings = @()
            safety_status = "REVIEW_REQUIRED"
        }
    }
}

function Read-AiOsMarkdownSummary {
    param([Parameter(Mandatory = $true)][string]$Path)

    $fullPath = Resolve-AiOsPath -Path $Path
    $freshness = Get-AiOsFileFreshness -Path $fullPath
    if ($freshness.status -eq "MISSING") {
        return [pscustomobject]@{
            source = Split-Path -Leaf $fullPath
            path = $fullPath
            present = $false
            freshness_status = "MISSING"
            freshness_age_hours = $null
            records_seen = 0
            status = "REVIEW_REQUIRED"
        }
    }

    if ($freshness.status -in @("UNREADABLE", "STALE")) {
        return [pscustomobject]@{
            source = Split-Path -Leaf $fullPath
            path = $fullPath
            present = $false
            freshness_status = $freshness.status
            freshness_age_hours = $freshness.age_hours
            records_seen = 0
            status = "REVIEW_REQUIRED"
        }
    }

    try {
        $text = Read-AiOsTextDocument -Path $fullPath
        $lines = if ([string]::IsNullOrWhiteSpace($text)) { 0 } else { @($text -split "`r?`n").Count }

        return [pscustomobject]@{
            source = Split-Path -Leaf $fullPath
            path = $fullPath
            present = $true
            freshness_status = $freshness.status
            freshness_age_hours = $freshness.age_hours
            records_seen = if ($lines -gt 0) { 1 } else { 0 }
            status = "PRESENT"
        }
    }
    catch {
        return [pscustomobject]@{
            source = Split-Path -Leaf $fullPath
            path = $fullPath
            present = $false
            freshness_status = "UNREADABLE"
            freshness_age_hours = $null
            records_seen = 0
            status = "REVIEW_REQUIRED"
        }
    }
}

function Write-AiOsAtomicJson {
    param(
        [Parameter(Mandatory = $true)][object]$InputObject,
        [Parameter(Mandatory = $true)][string]$DestinationPath
    )

    $destinationFull = Resolve-AiOsPath -Path $DestinationPath
    $destinationDir = Split-Path -Parent $destinationFull
    if (-not (Test-Path -LiteralPath $destinationDir -PathType Container)) {
        New-Item -ItemType Directory -Path $destinationDir -Force | Out-Null
    }

    $tempPath = Join-Path $destinationDir ((Split-Path -Leaf $destinationFull) + ".tmp")
    $json = $InputObject | ConvertTo-Json -Depth 16
    [System.IO.File]::WriteAllText($tempPath, $json, [System.Text.UTF8Encoding]::new($false))
    Move-Item -LiteralPath $tempPath -Destination $destinationFull -Force
}

$queueSummary = Read-AiOsQueueSummary -Path $QueueIndexPath
$lockSummary = Read-AiOsLockSummary -Path $LockStatusPath
$recoverySummary = Read-AiOsRecoverySummary -Path $RecoveryViewPath
$leadDispatchSummary = Read-AiOsLeadDispatchSummary -Path $LeadDispatchViewPath
$packetFactorySummary = Read-AiOsPacketFactorySummary -Path $PacketFactoryViewPath

$module5aCloseout = Read-AiOsMarkdownSummary -Path $Module5aCloseoutPath
$module5bDesign = Read-AiOsMarkdownSummary -Path $Module5bDesignPath
$spineOrchestratorDesign = Read-AiOsMarkdownSummary -Path $SpineOrchestratorDesignPath
$phaseCloseout = Read-AiOsMarkdownSummary -Path $PhaseCloseoutPath

$sourceReaders = @(
    [pscustomobject]@{ source = $queueSummary.source; path = $queueSummary.path; kind = "telemetry"; present = $queueSummary.present; freshness_status = $queueSummary.freshness_status; records_seen = $queueSummary.packet_count; status = $queueSummary.safety_status },
    [pscustomobject]@{ source = $lockSummary.source; path = $lockSummary.path; kind = "telemetry"; present = $lockSummary.present; freshness_status = $lockSummary.freshness_status; records_seen = $lockSummary.held_locks_count + $lockSummary.stale_locks_count + $lockSummary.collision_count; status = $lockSummary.safety_status },
    [pscustomobject]@{ source = $recoverySummary.source; path = $recoverySummary.path; kind = "telemetry"; present = $recoverySummary.present; freshness_status = $recoverySummary.freshness_status; records_seen = 1; status = $recoverySummary.safety_status },
    [pscustomobject]@{ source = $leadDispatchSummary.source; path = $leadDispatchSummary.path; kind = "telemetry"; present = $leadDispatchSummary.present; freshness_status = $leadDispatchSummary.freshness_status; records_seen = 1; status = $leadDispatchSummary.safety_status },
    [pscustomobject]@{ source = $packetFactorySummary.source; path = $packetFactorySummary.path; kind = "telemetry"; present = $packetFactorySummary.present; freshness_status = $packetFactorySummary.freshness_status; records_seen = if ($packetFactorySummary.present) { 1 } else { 0 }; status = $packetFactorySummary.safety_status },
    [pscustomobject]@{ source = $module5aCloseout.source; path = $module5aCloseout.path; kind = "report"; present = $module5aCloseout.present; freshness_status = $module5aCloseout.freshness_status; records_seen = $module5aCloseout.records_seen; status = $module5aCloseout.status },
    [pscustomobject]@{ source = $module5bDesign.source; path = $module5bDesign.path; kind = "report"; present = $module5bDesign.present; freshness_status = $module5bDesign.freshness_status; records_seen = $module5bDesign.records_seen; status = $module5bDesign.status },
    [pscustomobject]@{ source = $spineOrchestratorDesign.source; path = $spineOrchestratorDesign.path; kind = "report"; present = $spineOrchestratorDesign.present; freshness_status = $spineOrchestratorDesign.freshness_status; records_seen = $spineOrchestratorDesign.records_seen; status = $spineOrchestratorDesign.status },
    [pscustomobject]@{ source = $phaseCloseout.source; path = $phaseCloseout.path; kind = "report"; present = $phaseCloseout.present; freshness_status = $phaseCloseout.freshness_status; records_seen = $phaseCloseout.records_seen; status = $phaseCloseout.status }
)

$queueWarnings = @($queueSummary.warnings)
$lockWarnings = @($lockSummary.warnings)
$recoveryWarnings = @($recoverySummary.warnings)
$leadWarnings = @($leadDispatchSummary.warnings)
$packetFactoryWarnings = @($packetFactorySummary.warnings)
$moduleWarnings = @(
    if ($module5bDesign.present) { "module5b_design_only" } else { "module5b_design_missing" },
    "t2b_prerequisite_only",
    "live_dispatch_blocked_by_design"
)

$warnings = Merge-AiOsStrings -Items @($queueWarnings, $lockWarnings, $recoveryWarnings, $leadWarnings, $packetFactoryWarnings, $moduleWarnings)

$blockers = Merge-AiOsStrings -Items @(
    $queueSummary.blockers,
    $lockSummary.blockers,
    $recoverySummary.blockers,
    $leadDispatchSummary.blockers,
    $packetFactorySummary.blockers
)

$approvalGateStatus = Get-AiOsWorstStatus -Statuses @(
    $queueSummary.safety_status,
    $lockSummary.safety_status,
    $recoverySummary.safety_status,
    $leadDispatchSummary.safety_status,
    $packetFactorySummary.safety_status
)

$recommendedNextAction = switch ($approvalGateStatus) {
    "BLOCKED" { "Resolve the active queue, lock, recovery, or packet-factory blockers before any live action." }
    "REVIEW_REQUIRED" { "Review missing, stale, or unreadable telemetry and confirm approvals before APPLY." }
    default { "Continue read-only monitoring; no live dispatch is authorized." }
}

$result = [ordered]@{
    schema = "AIOS_COORDINATION_SPINE_VIEW.v1"
    system = "AI_OS"
    mode = "DRY_RUN"
    generated_at = (Get-Date).ToUniversalTime().ToString("o")
    repo_root = $RepoRoot
    source_readers = @($sourceReaders)
    queue_summary = $queueSummary
    lock_summary = $lockSummary
    recovery_summary = $recoverySummary
    lead_dispatch_summary = $leadDispatchSummary
    packet_factory_summary = $packetFactorySummary
    module5b_status = if ($module5bDesign.present) { "design_only" } else { "unknown" }
    t2b_status = "prerequisite_only"
    live_dispatch_status = "BLOCKED"
    approval_gate_status = $approvalGateStatus
    blockers = @($blockers)
    warnings = @($warnings)
    recommended_next_action = $recommendedNextAction
    write_path_enabled = $false
    write_behavior = "telemetry_only"
}

if ($Apply) {
    $defaultOutput = Resolve-AiOsPath -Path "telemetry/coordination_spine/COORDINATION_SPINE_VIEW.json"
    $resolvedOutput = Resolve-AiOsPath -Path $OutputPath
    if ($resolvedOutput -ne $defaultOutput) {
        throw "Apply mode may only write telemetry/coordination_spine/COORDINATION_SPINE_VIEW.json"
    }

    Write-AiOsAtomicJson -InputObject $result -DestinationPath $defaultOutput
}

$result | ConvertTo-Json -Depth 20
