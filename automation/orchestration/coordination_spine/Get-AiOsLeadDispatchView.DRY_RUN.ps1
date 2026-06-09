[CmdletBinding()]
param(
    [switch]$Apply,
    [string]$RepoRoot,
    [string]$DispatcherSourcePath,
    [switch]$DispatcherSampleCheck,
    [string]$QueueIndexPath,
    [string]$LockStatusPath,
    [string]$RecoveryViewPath,
    [string]$OutputPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($RepoRoot)) {
    $RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
}

if (-not $PSBoundParameters.ContainsKey("DispatcherSourcePath")) {
    $DispatcherSourcePath = Join-Path $RepoRoot "automation\orchestration\dispatcher\assignment_executor.py"
}

if (-not $PSBoundParameters.ContainsKey("QueueIndexPath")) {
    $QueueIndexPath = Join-Path $RepoRoot "telemetry\coordination_spine\UNIFIED_QUEUE_INDEX.json"
}

if (-not $PSBoundParameters.ContainsKey("LockStatusPath")) {
    $LockStatusPath = Join-Path $RepoRoot "telemetry\coordination_spine\UNIFIED_LOCK_STATUS.json"
}

if (-not $PSBoundParameters.ContainsKey("RecoveryViewPath")) {
    $RecoveryViewPath = Join-Path $RepoRoot "telemetry\coordination_spine\RECOVERY_BOOTSTRAP_VIEW.json"
}

if (-not $PSBoundParameters.ContainsKey("OutputPath")) {
    $OutputPath = Join-Path $RepoRoot "telemetry\coordination_spine\LEAD_DISPATCH_VIEW.json"
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

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return $null
    }

    $raw = Get-Content -LiteralPath $Path -Raw
    if ([string]::IsNullOrWhiteSpace($raw)) {
        return $null
    }

    try {
        return $raw | ConvertFrom-Json
    }
    catch {
        return $null
    }
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

    $tempPath = Join-Path $destinationDir (".{0}.tmp" -f [System.IO.Path]::GetRandomFileName())
    try {
        $json = $Payload | ConvertTo-Json -Depth 20
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

function Read-AiOsDispatcherSource {
    param(
        [Parameter(Mandatory = $true)]
        [string]$SourcePath
    )

    if (-not (Test-Path -LiteralPath $SourcePath -PathType Leaf)) {
        throw "Dispatcher source not found: $SourcePath"
    }

    $args = @($SourcePath, "--json")
    if ($DispatcherSampleCheck) {
        $args = @($SourcePath, "--sample-check", "--json")
    }

    $output = & python @args 2>&1
    if ($LASTEXITCODE -ne 0) {
        $message = ($output -join "`n").Trim()
        throw "Dispatcher source failed: $message"
    }

    $text = ($output -join "`n").Trim()
    if ([string]::IsNullOrWhiteSpace($text)) {
        throw "Dispatcher source produced no JSON output."
    }

    return $text | ConvertFrom-Json
}

function Get-QueueSummary {
    param([object]$QueueDocument)

    $counts = [ordered]@{
        QUEUED = 0
        RUNNING = 0
        BLOCKED = 0
        WAITING_APPROVAL = 0
        COMPLETE = 0
        FAILED = 0
        ARCHIVED = 0
    }

    $packetCount = 0
    $present = $null -ne $QueueDocument
    if ($present) {
        if ($QueueDocument.PSObject.Properties.Name -contains "packet_count") {
            $packetCount = [int]$QueueDocument.packet_count
        }

        if ($QueueDocument.PSObject.Properties.Name -contains "normalized_state_counts") {
            foreach ($state in @($counts.Keys)) {
                $value = $QueueDocument.normalized_state_counts.$state
                if ($null -ne $value) {
                    $counts[$state] = [int]$value
                }
            }
        }
    }

    $openCandidateCount = [int]$counts.QUEUED + [int]$counts.RUNNING + [int]$counts.WAITING_APPROVAL
    $sourceStateCounts = [ordered]@{}
    if ($present -and $QueueDocument.PSObject.Properties.Name -contains "source_state_counts") {
        foreach ($property in $QueueDocument.source_state_counts.PSObject.Properties) {
            $sourceStateCounts[$property.Name] = [int]$property.Value
        }
    }

    $summary = [ordered]@{
        present = $present
        packet_count = $packetCount
        open_candidate_count = $openCandidateCount
        blocked_count = [int]$counts.BLOCKED
        waiting_approval_count = [int]$counts.WAITING_APPROVAL
        complete_count = [int]$counts.COMPLETE
        normalized_state_counts = $counts
        source_state_counts = $sourceStateCounts
    }

    return $summary
}

function Get-LockSummary {
    param([object]$LockDocument)

    $present = $null -ne $LockDocument
    $heldLocksCount = 0
    $staleLocksCount = 0
    $collisionCount = 0
    $safetyStatus = "REVIEW_REQUIRED"
    if ($present) {
        if ($LockDocument.PSObject.Properties.Name -contains "held_locks_count") {
            $heldLocksCount = [int]$LockDocument.held_locks_count
        }
        if ($LockDocument.PSObject.Properties.Name -contains "stale_locks_count") {
            $staleLocksCount = [int]$LockDocument.stale_locks_count
        }
        if ($LockDocument.PSObject.Properties.Name -contains "collision_count") {
            $collisionCount = [int]$LockDocument.collision_count
        }
        if ($LockDocument.PSObject.Properties.Name -contains "safety_status") {
            $safetyStatus = [string]$LockDocument.safety_status
        }
        elseif ($collisionCount -eq 0 -and $staleLocksCount -eq 0) {
            $safetyStatus = "PASS"
        }
    }

    $summary = [ordered]@{
        present = $present
        held_locks_count = $heldLocksCount
        stale_locks_count = $staleLocksCount
        collision_count = $collisionCount
        safety_status = $safetyStatus
        write_behavior = "telemetry_only"
    }

    return $summary
}

function Get-RecoverySummary {
    param([object]$RecoveryDocument)

    $present = $null -ne $RecoveryDocument
    $readiness = "REVIEW_REQUIRED"
    $blockers = @()
    $warnings = @()
    $heartbeatStatus = "UNAVAILABLE"

    if ($present) {
        if ($RecoveryDocument.PSObject.Properties.Name -contains "recovery_readiness") {
            $readiness = [string]$RecoveryDocument.recovery_readiness
        }
        if ($RecoveryDocument.PSObject.Properties.Name -contains "blockers") {
            $blockers = @($RecoveryDocument.blockers)
        }
        if ($RecoveryDocument.PSObject.Properties.Name -contains "warnings") {
            $warnings = @($RecoveryDocument.warnings)
        }
        if ($RecoveryDocument.PSObject.Properties.Name -contains "heartbeat_status") {
            $heartbeatStatus = [string]$RecoveryDocument.heartbeat_status
        }
    }

    $summary = [ordered]@{
        present = $present
        recovery_readiness = $readiness
        blockers = $blockers
        warnings = $warnings
        heartbeat_status = $heartbeatStatus
        write_behavior = "telemetry_only"
    }

    return $summary
}

function Select-DispatcherEvaluation {
    param(
        [object]$DispatcherReport,
        [object]$QueueSummary,
        [object]$LockSummary,
        [object]$RecoverySummary
    )

    $sourceRecommended = $null
    if ($null -ne $DispatcherReport -and $DispatcherReport.PSObject.Properties.Name -contains "recommended_lanes") {
        $recommended = @($DispatcherReport.recommended_lanes)
        if ($recommended.Count -gt 0) {
            $sourceRecommended = $recommended[0]
        }
    }

    $sourceBlockers = @()
    if ($null -ne $DispatcherReport -and $DispatcherReport.PSObject.Properties.Name -contains "blockers") {
        $sourceBlockers = @($DispatcherReport.blockers)
    }

    $queueBlocked = [int]$QueueSummary.blocked_count -gt 0
    $queueOpenCandidates = [int]$QueueSummary.open_candidate_count
    $lockBlocked = ($LockSummary.safety_status -eq "REVIEW_REQUIRED" -or [int]$LockSummary.collision_count -gt 0 -or [int]$LockSummary.held_locks_count -gt 0)
    $recoveryBlocked = ($RecoverySummary.recovery_readiness -eq "BLOCKED")

    if ($queueBlocked -or $lockBlocked -or $recoveryBlocked) {
        $reasonParts = New-Object System.Collections.Generic.List[string]
        if ($queueBlocked) { [void]$reasonParts.Add("queue_blocked") }
        if ($lockBlocked) { [void]$reasonParts.Add("lock_review_required_or_collision") }
        if ($recoveryBlocked) { [void]$reasonParts.Add("recovery_blocked") }

        $result = [ordered]@{
            dispatcher_safety_verdict = "BLOCKED"
            blocked_reason = ($reasonParts -join ", ")
            dispatcher_candidate = @{
                source = "assignment_executor.py"
                source_task_id = if ($null -ne $sourceRecommended -and $sourceRecommended.PSObject.Properties.Name -contains "task_id") { [string]$sourceRecommended.task_id } else { $null }
                source_lane = if ($null -ne $sourceRecommended -and $sourceRecommended.PSObject.Properties.Name -contains "lane") { [string]$sourceRecommended.lane } else { $null }
                source_decision = if ($null -ne $sourceRecommended -and $sourceRecommended.PSObject.Properties.Name -contains "decision") { [string]$sourceRecommended.decision } else { "UNKNOWN" }
                evaluated_decision = "BLOCKED"
                source_next_safe_action = if ($null -ne $sourceRecommended -and $sourceRecommended.PSObject.Properties.Name -contains "next_safe_action") { [string]$sourceRecommended.next_safe_action } else { "Resolve blockers before dispatch." }
            }
            next_safe_action = "Resolve the active blocker in queue, lock, or recovery telemetry before any assignment mutation."
        }

        return $result
    }

    if ($queueOpenCandidates -eq 0) {
        $result = [ordered]@{
            dispatcher_safety_verdict = "SAFE_NO_WORK"
            blocked_reason = $null
            dispatcher_candidate = @{
                source = "assignment_executor.py"
                source_task_id = $null
                source_lane = $null
                source_decision = "NO_WORK"
                evaluated_decision = "NO_WORK"
                source_next_safe_action = "No queue candidates available."
            }
            next_safe_action = "Keep watching telemetry; no dispatch action is needed."
        }

        return $result
    }

    if ($null -eq $sourceRecommended) {
        $result = [ordered]@{
            dispatcher_safety_verdict = "REVIEW_REQUIRED"
            blocked_reason = "dispatcher_source_missing_recommendation"
            dispatcher_candidate = @{
                source = "assignment_executor.py"
                source_task_id = $null
                source_lane = $null
                source_decision = "UNKNOWN"
                evaluated_decision = "REVIEW_REQUIRED"
                source_next_safe_action = "Inspect dispatcher source output."
            }
            next_safe_action = "Inspect dispatcher source output before any future dispatch or write-path work."
        }

        return $result
    }

    $sourceDecision = if ($sourceRecommended.PSObject.Properties.Name -contains "decision") { [string]$sourceRecommended.decision } else { "UNKNOWN" }
    $evaluatedDecision = switch ($sourceDecision) {
        "READY" { "READY_FOR_REVIEW" }
        "DRY_RUN_ONLY" { "READY_FOR_REVIEW" }
        "WAITING_APPROVAL" { "REVIEW_REQUIRED" }
        "BLOCKED_BY_LOCK" { "BLOCKED" }
        "BLOCKED_BY_PR_DEPENDENCY" { "REVIEW_REQUIRED" }
        "BLOCKED_BY_PROTECTED_PATH" { "BLOCKED" }
        "BLOCKED_BY_COLLISION" { "BLOCKED" }
        "REVIEW_REQUIRED" { "REVIEW_REQUIRED" }
        default { "REVIEW_REQUIRED" }
    }

    $blockedReason = $null
    if ($sourceBlockers.Count -gt 0) {
        $blockedReason = "dispatcher_source_reports_blockers"
    }

    $result = [ordered]@{
        dispatcher_safety_verdict = $evaluatedDecision
        blocked_reason = $blockedReason
        dispatcher_candidate = @{
            source = "assignment_executor.py"
            source_task_id = if ($sourceRecommended.PSObject.Properties.Name -contains "task_id") { [string]$sourceRecommended.task_id } else { $null }
            source_lane = if ($sourceRecommended.PSObject.Properties.Name -contains "lane") { [string]$sourceRecommended.lane } else { $null }
            source_decision = $sourceDecision
            evaluated_decision = $evaluatedDecision
            source_next_safe_action = if ($sourceRecommended.PSObject.Properties.Name -contains "next_safe_action") { [string]$sourceRecommended.next_safe_action } else { "Review dispatcher source output." }
        }
        next_safe_action = if ($evaluatedDecision -eq "READY_FOR_REVIEW") {
            "Review the candidate with the T2B prerequisite in mind; do not assign or claim locks here."
        }
        elseif ($evaluatedDecision -eq "REVIEW_REQUIRED") {
            "Review dispatcher evidence before any write-path work."
        }
        else {
            "No dispatcher write-path action is authorized."
        }
    }

    return $result
}

$dispatcherSource = Read-AiOsDispatcherSource -SourcePath (Resolve-AiOsPath -Path $DispatcherSourcePath)
$queueDocument = Read-AiOsJsonDocument -Path (Resolve-AiOsPath -Path $QueueIndexPath)
$lockDocument = Read-AiOsJsonDocument -Path (Resolve-AiOsPath -Path $LockStatusPath)
$recoveryDocument = Read-AiOsJsonDocument -Path (Resolve-AiOsPath -Path $RecoveryViewPath)

$queueSummary = Get-QueueSummary -QueueDocument $queueDocument
$lockSummary = Get-LockSummary -LockDocument $lockDocument
$recoverySummary = Get-RecoverySummary -RecoveryDocument $recoveryDocument
$evaluation = Select-DispatcherEvaluation -DispatcherReport $dispatcherSource -QueueSummary $queueSummary -LockSummary $lockSummary -RecoverySummary $recoverySummary

$sourceReaders = @(
    [pscustomobject]@{
        source = "assignment_executor.py"
        path = Resolve-AiOsPath -Path $DispatcherSourcePath
        exists = [bool](Test-Path -LiteralPath (Resolve-AiOsPath -Path $DispatcherSourcePath) -PathType Leaf)
        records_seen = if ($dispatcherSource.PSObject.Properties.Name -contains "recommended_lanes") { @($dispatcherSource.recommended_lanes).Count } elseif ($dispatcherSource.PSObject.Properties.Name -contains "candidate_decisions") { @($dispatcherSource.candidate_decisions).Count } else { 0 }
    },
    [pscustomobject]@{
        source = "UNIFIED_QUEUE_INDEX.json"
        path = Resolve-AiOsPath -Path $QueueIndexPath
        exists = $queueSummary.present
        records_seen = [int]$queueSummary.packet_count
    },
    [pscustomobject]@{
        source = "UNIFIED_LOCK_STATUS.json"
        path = Resolve-AiOsPath -Path $LockStatusPath
        exists = $lockSummary.present
        records_seen = [int]$lockSummary.held_locks_count + [int]$lockSummary.stale_locks_count + [int]$lockSummary.collision_count
    },
    [pscustomobject]@{
        source = "RECOVERY_BOOTSTRAP_VIEW.json"
        path = Resolve-AiOsPath -Path $RecoveryViewPath
        exists = $recoverySummary.present
        records_seen = if ($recoverySummary.present) { 1 } else { 0 }
    }
)

$payload = [ordered]@{
    schema = "AIOS_LEAD_DISPATCH_VIEW.v1"
    system = "AI_OS"
    mode = "DRY_RUN"
    generated_at = (Get-Date).ToUniversalTime().ToString("o")
    repo_root = $RepoRoot
    source_readers = $sourceReaders
    queue_status_summary = $queueSummary
    lock_status_summary = $lockSummary
    recovery_status_summary = $recoverySummary
    dispatcher_candidate = $evaluation.dispatcher_candidate
    dispatcher_safety_verdict = $evaluation.dispatcher_safety_verdict
    blocked_reason = $evaluation.blocked_reason
    depends_on_t2b = $true
    t2b_dependency_note = "T2B assignment-plus-lock integration remains a prerequisite for any future write-path dispatch."
    write_path_enabled = $false
    write_behavior = "telemetry_only"
    next_safe_action = $evaluation.next_safe_action
}

if ($Apply) {
    $defaultOutput = Resolve-AiOsPath -Path "telemetry\coordination_spine\LEAD_DISPATCH_VIEW.json"
    $resolvedOutput = Resolve-AiOsPath -Path $OutputPath
    if ($resolvedOutput -ne $defaultOutput) {
        throw "Apply mode may only write telemetry\coordination_spine\LEAD_DISPATCH_VIEW.json"
    }

    Write-AiOsAtomicJson -DestinationPath $defaultOutput -Payload $payload
}

$payload | ConvertTo-Json -Depth 20
