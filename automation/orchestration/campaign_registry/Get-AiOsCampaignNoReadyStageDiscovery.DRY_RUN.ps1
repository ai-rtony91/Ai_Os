[CmdletBinding()]
param(
    [string]$RegistryPath = "automation/orchestration/campaign_registry/AIOS_STRATEGIC_CAMPAIGN_REGISTRY.json",
    [switch]$OutputJson
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Resolve-AiOsLocalPath {
    param([Parameter(Mandatory = $true)][string]$Path)

    if ([System.IO.Path]::IsPathRooted($Path)) {
        return $Path
    }

    return Join-Path (Get-Location).Path $Path
}

function Get-StageStatusBucket {
    param([AllowNull()][string]$Status)

    $normalized = ([string]$Status).Trim().ToUpperInvariant()
    switch ($normalized) {
        "READY" { return "READY" }
        "COMPLETE" { return "COMPLETE" }
        "BLOCKED" { return "BLOCKED" }
        "IN_PROGRESS" { return "IN_PROGRESS" }
        "PLANNED" { return "PLANNED" }
        "NOT_STARTED" { return "PLANNED" }
        "NEEDS_REVIEW" { return "NEEDS_REVIEW" }
        "DEFERRED" { return "DEFERRED" }
        default { return "UNKNOWN" }
    }
}

function Get-PriorityRank {
    param([AllowNull()][string]$Priority)

    switch ($Priority) {
        "critical" { return 0 }
        "high" { return 1 }
        "normal" { return 2 }
        "low" { return 3 }
        default { return 99 }
    }
}

function Get-StageMap {
    param([Parameter(Mandatory = $true)]$Campaigns)

    $map = @{}
    foreach ($campaign in @($Campaigns)) {
        foreach ($stage in @($campaign.stages)) {
            if ($stage.stage_id) {
                $map[[string]$stage.stage_id] = $stage
            }
        }
    }
    return $map
}

function Test-DependenciesComplete {
    param(
        [Parameter(Mandatory = $true)]$Stage,
        [Parameter(Mandatory = $true)][hashtable]$StageMap
    )

    foreach ($dependency in @($Stage.depends_on)) {
        $dependencyId = [string]$dependency
        if ([string]::IsNullOrWhiteSpace($dependencyId)) {
            continue
        }

        if (-not $StageMap.ContainsKey($dependencyId)) {
            return $false
        }

        if ([string]$StageMap[$dependencyId].status -ne "COMPLETE") {
            return $false
        }
    }

    return $true
}

function Convert-StageSummary {
    param(
        [Parameter(Mandatory = $true)]$Campaign,
        [Parameter(Mandatory = $true)]$Stage,
        [Parameter(Mandatory = $true)][hashtable]$StageMap,
        [string]$Gap = ""
    )

    $stageBlockers = @($Stage.blocked_by | Where-Object { -not [string]::IsNullOrWhiteSpace([string]$_) })
    $campaignBlockers = @($Campaign.blocked_by | Where-Object { -not [string]::IsNullOrWhiteSpace([string]$_) })
    $statusBucket = Get-StageStatusBucket -Status ([string]$Stage.status)
    $dependenciesComplete = Test-DependenciesComplete -Stage $Stage -StageMap $StageMap
    $nextPacketCandidate = if ($Stage.PSObject.Properties.Name -contains "next_packet_candidate") { $Stage.next_packet_candidate } else { $null }

    return [pscustomobject]@{
        campaign_id = [string]$Campaign.campaign_id
        campaign_title = [string]$Campaign.title
        stage_id = [string]$Stage.stage_id
        stage_title = [string]$Stage.title
        phase_id = [string]$Stage.phase_id
        status = [string]$Stage.status
        status_bucket = $statusBucket
        priority = [string]$Stage.priority
        depends_on = @($Stage.depends_on)
        dependencies_complete = $dependenciesComplete
        blocked_by = @($campaignBlockers + $stageBlockers)
        next_packet_candidate = $nextPacketCandidate
        gap = $Gap
    }
}

function Get-AiOsCampaignNextTaskState {
    param(
        [Parameter(Mandatory = $true)][string]$RepoRoot,
        [Parameter(Mandatory = $true)][string]$ResolvedRegistryPath
    )

    $nextTaskScript = Join-Path $RepoRoot "automation/orchestration/campaign_registry/Get-AiOsCampaignNextTask.DRY_RUN.ps1"
    if (-not (Test-Path -LiteralPath $nextTaskScript -PathType Leaf)) {
        return $null
    }

    try {
        $rawOutput = & $nextTaskScript -RegistryPath $ResolvedRegistryPath -OutputJson 2>$null
        $rawText = ($rawOutput | Out-String).Trim()
        if ([string]::IsNullOrWhiteSpace($rawText)) {
            return $null
        }
        return $rawText | ConvertFrom-Json -ErrorAction Stop
    }
    catch {
        return $null
    }
}

$repoRoot = (Get-Location).Path
$resolvedRegistryPath = Resolve-AiOsLocalPath -Path $RegistryPath
if (-not (Test-Path -LiteralPath $resolvedRegistryPath -PathType Leaf)) {
    throw "Campaign registry not found: $RegistryPath"
}

$registry = Get-Content -LiteralPath $resolvedRegistryPath -Raw | ConvertFrom-Json
$nextTaskState = Get-AiOsCampaignNextTaskState -RepoRoot $repoRoot -ResolvedRegistryPath $resolvedRegistryPath
$overallReadiness = if ($nextTaskState -and $nextTaskState.PSObject.Properties.Name -contains "overall_readiness") {
    [string]$nextTaskState.overall_readiness
}
else {
    "UNKNOWN"
}
$noReadyStageDetected = $overallReadiness -eq "NO_READY_STAGE"
$reason = if ($nextTaskState -and $nextTaskState.PSObject.Properties.Name -contains "reason") {
    [string]$nextTaskState.reason
}
else {
    "Campaign next-task selector output was unavailable or incomplete."
}

$stageMap = Get-StageMap -Campaigns $registry.campaigns
$statusCounts = [ordered]@{
    READY = 0
    COMPLETE = 0
    BLOCKED = 0
    IN_PROGRESS = 0
    PLANNED = 0
    NEEDS_REVIEW = 0
    DEFERRED = 0
    UNKNOWN = 0
}
$allStageSummaries = New-Object System.Collections.Generic.List[object]
$blockedStages = New-Object System.Collections.Generic.List[object]
$candidateNextStageOptions = New-Object System.Collections.Generic.List[object]
$supervisedAutonomySelectableStages = New-Object System.Collections.Generic.List[object]
$supervisedAutonomyStages = New-Object System.Collections.Generic.List[object]
$dependencyInconsistencies = New-Object System.Collections.Generic.List[object]
$readyStagesWithBlockers = New-Object System.Collections.Generic.List[object]
$completeStagesWithPacketCandidates = New-Object System.Collections.Generic.List[object]
$activeNextPacketCandidates = New-Object System.Collections.Generic.List[object]
$duplicateActiveNextPacketCandidates = New-Object System.Collections.Generic.List[object]
$activeHighPriorityBlockedStages = New-Object System.Collections.Generic.List[object]
$highPriorityInProgressMissingNextPacketCandidate = New-Object System.Collections.Generic.List[object]
$plannedOrInProgressCandidateOptions = New-Object System.Collections.Generic.List[object]
$stageIdCounts = @{}

$totalPhases = 0
foreach ($campaign in @($registry.campaigns)) {
    $totalPhases += @($campaign.phases).Count

    foreach ($stage in @($campaign.stages)) {
        $bucket = Get-StageStatusBucket -Status ([string]$stage.status)
        $stageId = [string]$stage.stage_id
        $stagePriority = ([string]$stage.priority).ToLowerInvariant()
        $campaignPriority = ([string]$campaign.priority).ToLowerInvariant()
        $campaignStatus = [string]$campaign.status
        if ($statusCounts.Contains($bucket)) {
            $statusCounts[$bucket] = [int]$statusCounts[$bucket] + 1
        }
        else {
            $statusCounts["UNKNOWN"] = [int]$statusCounts["UNKNOWN"] + 1
        }

        $summary = Convert-StageSummary -Campaign $campaign -Stage $stage -StageMap $stageMap
        [void]$allStageSummaries.Add($summary)

        if (-not [string]::IsNullOrWhiteSpace($stageId)) {
            if (-not $stageIdCounts.ContainsKey($stageId)) {
                $stageIdCounts[$stageId] = 0
            }
            $stageIdCounts[$stageId] = [int]$stageIdCounts[$stageId] + 1
        }

        foreach ($dependency in @($stage.depends_on)) {
            $dependencyId = [string]$dependency
            if ([string]::IsNullOrWhiteSpace($dependencyId)) {
                continue
            }

            if (-not $stageMap.ContainsKey($dependencyId)) {
                [void]$dependencyInconsistencies.Add([pscustomobject]@{
                    campaign_id = [string]$campaign.campaign_id
                    stage_id = $stageId
                    missing_dependency_id = $dependencyId
                    issue = "Stage depends on missing stage id."
                })
            }
        }

        if ([string]$stage.status -eq "READY" -and @($summary.blocked_by).Count -gt 0) {
            [void]$readyStagesWithBlockers.Add($summary)
        }

        if ([string]$stage.status -eq "COMPLETE" -and -not [string]::IsNullOrWhiteSpace([string]$summary.next_packet_candidate)) {
            [void]$completeStagesWithPacketCandidates.Add($summary)
        }

        if (
            -not [string]::IsNullOrWhiteSpace([string]$summary.next_packet_candidate) -and
            @("COMPLETE", "DEFERRED") -notcontains $bucket
        ) {
            [void]$activeNextPacketCandidates.Add([pscustomobject]@{
                next_packet_candidate = [string]$summary.next_packet_candidate
                campaign_id = [string]$campaign.campaign_id
                stage_id = $stageId
                status = [string]$stage.status
            })
        }

        $isHighPriorityPath = @("critical", "high") -contains $campaignPriority -or @("critical", "high") -contains $stagePriority
        $isActiveCampaignPath = $campaignStatus -eq "IN_PROGRESS"
        if (($bucket -eq "BLOCKED" -or @($summary.blocked_by).Count -gt 0) -and ($isHighPriorityPath -or $isActiveCampaignPath)) {
            [void]$activeHighPriorityBlockedStages.Add($summary)
        }

        if (
            $bucket -eq "IN_PROGRESS" -and
            ($isHighPriorityPath -or $isActiveCampaignPath) -and
            [string]::IsNullOrWhiteSpace([string]$summary.next_packet_candidate)
        ) {
            [void]$highPriorityInProgressMissingNextPacketCandidate.Add($summary)
        }

        if ([string]$campaign.campaign_id -eq "CAMPAIGN-SUPERVISED-AUTONOMY") {
            [void]$supervisedAutonomyStages.Add($summary)
            if (
                [string]$stage.status -eq "READY" -and
                $summary.dependencies_complete -and
                @($summary.blocked_by).Count -eq 0
            ) {
                [void]$supervisedAutonomySelectableStages.Add($summary)
            }
        }

        if ($bucket -eq "BLOCKED" -or @($summary.blocked_by).Count -gt 0) {
            [void]$blockedStages.Add($summary)
        }

        if (@("IN_PROGRESS", "PLANNED", "NEEDS_REVIEW") -contains $bucket) {
            $gap = if (@($summary.blocked_by).Count -gt 0) {
                "Blockers must be resolved before this stage can become selectable."
            }
            elseif (-not $summary.dependencies_complete) {
                "Dependencies must be completed before this stage can become selectable."
            }
            elseif ($bucket -eq "NEEDS_REVIEW") {
                "Review state must be resolved before this stage can be considered for READY."
            }
            elseif ($bucket -eq "IN_PROGRESS") {
                "In-progress stage needs scoped review before a next packet candidate is defined."
            }
            else {
                "Planned stage needs explicit planning review before any READY transition."
            }

            [void]$candidateNextStageOptions.Add((Convert-StageSummary -Campaign $campaign -Stage $stage -StageMap $stageMap -Gap $gap))
            if ($campaignStatus -eq "IN_PROGRESS" -and @("IN_PROGRESS", "PLANNED") -contains $bucket) {
                [void]$plannedOrInProgressCandidateOptions.Add($summary)
            }
        }
    }
}

foreach ($candidateGroup in @($activeNextPacketCandidates | Group-Object -Property next_packet_candidate | Where-Object { $_.Count -gt 1 })) {
    [void]$duplicateActiveNextPacketCandidates.Add([pscustomobject]@{
        next_packet_candidate = [string]$candidateGroup.Name
        count = [int]$candidateGroup.Count
        stages = @($candidateGroup.Group)
        issue = "Duplicate active next_packet_candidate values exist."
    })
}

$duplicateStageIds = New-Object System.Collections.Generic.List[object]
foreach ($stageIdKey in @($stageIdCounts.Keys)) {
    if ([int]$stageIdCounts[$stageIdKey] -gt 1) {
        [void]$duplicateStageIds.Add([pscustomobject]@{
            stage_id = [string]$stageIdKey
            count = [int]$stageIdCounts[$stageIdKey]
            issue = "Duplicate stage_id values exist."
        })
    }
}

$lastCompletedHighPriorityStage = @(
    $allStageSummaries |
        Where-Object { $_.status_bucket -eq "COMPLETE" -and @("critical", "high") -contains ([string]$_.priority).ToLowerInvariant() } |
        Sort-Object @{ Expression = { Get-PriorityRank -Priority ([string]$_.priority) } }, @{ Expression = { [string]$_.campaign_id } }, @{ Expression = { [string]$_.stage_id } }
) | Select-Object -Last 1

$supervisedAutonomyNoSelectableStage = $supervisedAutonomySelectableStages.Count -eq 0
$candidateGapNotes = New-Object System.Collections.Generic.List[string]
if ($noReadyStageDetected) {
    [void]$candidateGapNotes.Add("Campaign selector found no READY stage with complete dependencies and no blockers.")
}
if ($supervisedAutonomyNoSelectableStage) {
    [void]$candidateGapNotes.Add("Supervised autonomy ladder has no next selectable READY stage.")
}
if ($candidateNextStageOptions.Count -gt 0) {
    [void]$candidateGapNotes.Add("Potential next-stage gaps exist, but they require planning or review before any registry status change.")
}
else {
    [void]$candidateGapNotes.Add("No IN_PROGRESS, PLANNED, or NEEDS_REVIEW stage is immediately available as a candidate option.")
}

$registryInconsistencyDetected = (
    $dependencyInconsistencies.Count -gt 0 -or
    $readyStagesWithBlockers.Count -gt 0 -or
    $completeStagesWithPacketCandidates.Count -gt 0 -or
    $duplicateActiveNextPacketCandidates.Count -gt 0 -or
    $duplicateStageIds.Count -gt 0
)
$lastCompletedHighPriorityStageExists = $null -ne $lastCompletedHighPriorityStage
$activeHighPriorityBlockedCount = $activeHighPriorityBlockedStages.Count
$inProgressHighPriorityMissingNextPacketCandidateCount = $highPriorityInProgressMissingNextPacketCandidate.Count
$plannedOrInProgressCandidateCount = $plannedOrInProgressCandidateOptions.Count
$workloadCompletionState = "UNKNOWN"
$noReadyStageClassification = "NEEDS_NEXT_STAGE_PLANNING"
$noReadyStageClassificationReason = "No READY stage is available; planning review is required before defining new work."
$idleAllowed = $false
$nextStagePlanningRequired = $true

if ($noReadyStageDetected -and $registryInconsistencyDetected) {
    $noReadyStageClassification = "BLOCKED_BY_REGISTRY_INCONSISTENCY"
    $noReadyStageClassificationReason = "No READY stage is available and registry bookkeeping inconsistencies were detected."
    $workloadCompletionState = "BLOCKED_BY_REGISTRY_INCONSISTENCY"
    $idleAllowed = $false
    $nextStagePlanningRequired = $false
}
elseif (
    $noReadyStageDetected -and
    [int]$statusCounts["READY"] -eq 0 -and
    $activeHighPriorityBlockedCount -eq 0 -and
    $inProgressHighPriorityMissingNextPacketCandidateCount -eq 0 -and
    (-not $registryInconsistencyDetected) -and
    $lastCompletedHighPriorityStageExists -and
    $plannedOrInProgressCandidateCount -eq 0
) {
    $noReadyStageClassification = "COMPLETE_IDLE"
    $noReadyStageClassificationReason = "No READY stage is available, no active/high-priority blocker is detected, no in-progress high-priority stage is missing a packet candidate, and a high-priority stage was completed."
    $workloadCompletionState = "COMPLETE_IDLE"
    $idleAllowed = $true
    $nextStagePlanningRequired = $false
}
elseif (
    $noReadyStageDetected -and
    [int]$statusCounts["READY"] -eq 0 -and
    $plannedOrInProgressCandidateCount -gt 0 -and
    (-not $registryInconsistencyDetected)
) {
    $noReadyStageClassification = "NEEDS_NEXT_STAGE_PLANNING"
    $noReadyStageClassificationReason = "No READY stage is available and active planned or in-progress campaign work needs supervised planning before it can become selectable."
    $workloadCompletionState = "NEEDS_NEXT_STAGE_PLANNING"
    $idleAllowed = $false
    $nextStagePlanningRequired = $true
}
elseif ($noReadyStageDetected) {
    $noReadyStageClassification = "NEEDS_NEXT_STAGE_PLANNING"
    $noReadyStageClassificationReason = "No READY stage is available; a supervised planning review is required before defining any new selectable work."
    $workloadCompletionState = "NEEDS_NEXT_STAGE_PLANNING"
    $idleAllowed = $false
    $nextStagePlanningRequired = $true
}

$actionRecommendationPath = Join-Path $repoRoot "automation/orchestration/recommendations/Get-AiOsActionRecommendation.DRY_RUN.ps1"
$relayOperatorPath = Join-Path $repoRoot "automation/orchestration/review_bridge/Get-AiOsRelayOperatorState.DRY_RUN.ps1"
$relayResolverPath = Join-Path $repoRoot "automation/orchestration/relay_bus/Resolve-AiOsRelayHumanReview.DRY_RUN.ps1"
$routineReviewDocPath = Join-Path $repoRoot "docs/AI_OS/autonomy/AIOS_ROUTINE_REVIEW_CONTINUATION_GATE_V1.md"

$relatedSurfaces = @(
    [pscustomobject]@{
        path = "automation/orchestration/recommendations/Get-AiOsActionRecommendation.DRY_RUN.ps1"
        role = "Routes no-ready-stage state to this discovery helper as a read-only planning action."
        exists = [bool](Test-Path -LiteralPath $actionRecommendationPath -PathType Leaf)
    },
    [pscustomobject]@{
        path = "automation/orchestration/review_bridge/Get-AiOsRelayOperatorState.DRY_RUN.ps1"
        role = "Surfaces relay/SOS continuation state that can override campaign discovery when a relay review is active."
        exists = [bool](Test-Path -LiteralPath $relayOperatorPath -PathType Leaf)
    },
    [pscustomobject]@{
        path = "automation/orchestration/relay_bus/Resolve-AiOsRelayHumanReview.DRY_RUN.ps1"
        role = "Provides governed relay review resolution for routine review items."
        exists = [bool](Test-Path -LiteralPath $relayResolverPath -PathType Leaf)
    },
    [pscustomobject]@{
        path = "docs/AI_OS/autonomy/AIOS_ROUTINE_REVIEW_CONTINUATION_GATE_V1.md"
        role = "Documents the prior autonomy stage completed before this no-ready-stage discovery router."
        exists = [bool](Test-Path -LiteralPath $routineReviewDocPath -PathType Leaf)
    }
)

$recommendedNextAction = switch ($noReadyStageClassification) {
    "COMPLETE_IDLE" { "No READY stage is available and no blocker is detected. Idle cleanly or request a supervised planning review before defining new work." }
    "BLOCKED_BY_REGISTRY_INCONSISTENCY" { "Review and repair campaign registry inconsistencies before requesting a packet." }
    default {
        if ($noReadyStageDetected) {
            "Review campaign registry gaps and create a supervised DRY_RUN packet candidate for the next autonomy stage."
        }
        else {
            "Use the campaign next-task selector output before running no-ready-stage discovery."
        }
    }
}
$lastCompletedStageValue = if ($null -ne $lastCompletedHighPriorityStage) { $lastCompletedHighPriorityStage } else { $null }
$statusCountsObject = [pscustomobject]@{
    READY = [int]$statusCounts["READY"]
    COMPLETE = [int]$statusCounts["COMPLETE"]
    BLOCKED = [int]$statusCounts["BLOCKED"]
    IN_PROGRESS = [int]$statusCounts["IN_PROGRESS"]
    PLANNED = [int]$statusCounts["PLANNED"]
    NEEDS_REVIEW = [int]$statusCounts["NEEDS_REVIEW"]
    DEFERRED = [int]$statusCounts["DEFERRED"]
    UNKNOWN = [int]$statusCounts["UNKNOWN"]
}
$inventoryObject = [pscustomobject]@{
    total_campaigns = @($registry.campaigns).Count
    total_phases = $totalPhases
    total_stages = $allStageSummaries.Count
    status_counts = $statusCountsObject
}
$candidateGapSummaryObject = [pscustomobject]@{
    no_ready_stage_detected = $noReadyStageDetected
    supervised_autonomy_no_next_selectable_stage = $supervisedAutonomyNoSelectableStage
    supervised_autonomy_stage_count = $supervisedAutonomyStages.Count
    supervised_autonomy_selectable_stage_count = $supervisedAutonomySelectableStages.Count
    notes = @($candidateGapNotes.ToArray())
}
$safetyObject = [pscustomobject]@{
    planning_only = $true
    writes_files = $false
    mutates_registry = $false
    creates_ready_stage = $false
    reopens_completed_stage = $false
    approves_apply = $false
    runs_workers = $false
    starts_runtime = $false
    mutates_queue = $false
    mutates_approval = $false
    commits = $false
    pushes = $false
    broker_or_live_trading = $false
}
$classifierEvidenceObject = [pscustomobject]@{
    ready_count = [int]$statusCounts["READY"]
    blocked_count = [int]$statusCounts["BLOCKED"]
    active_high_priority_blocked_count = $activeHighPriorityBlockedCount
    planned_or_in_progress_candidate_count = $plannedOrInProgressCandidateCount
    in_progress_high_priority_missing_next_packet_candidate_count = $inProgressHighPriorityMissingNextPacketCandidateCount
    last_completed_high_priority_stage_exists = $lastCompletedHighPriorityStageExists
    dependency_inconsistency_count = $dependencyInconsistencies.Count
    ready_stage_with_blocker_count = $readyStagesWithBlockers.Count
    complete_stage_with_next_packet_candidate_count = $completeStagesWithPacketCandidates.Count
    duplicate_active_next_packet_candidate_count = $duplicateActiveNextPacketCandidates.Count
    duplicate_stage_id_count = $duplicateStageIds.Count
    dependency_inconsistencies = @($dependencyInconsistencies.ToArray())
    ready_stages_with_blockers = @($readyStagesWithBlockers.ToArray())
    complete_stages_with_packet_candidates = @($completeStagesWithPacketCandidates.ToArray())
    duplicate_active_next_packet_candidates = @($duplicateActiveNextPacketCandidates.ToArray())
    duplicate_stage_ids = @($duplicateStageIds.ToArray())
    active_high_priority_blocked_stages = @($activeHighPriorityBlockedStages.ToArray())
    high_priority_in_progress_missing_next_packet_candidate = @($highPriorityInProgressMissingNextPacketCandidate.ToArray())
}
$candidateNextStageOptionArray = @($candidateNextStageOptions.ToArray())
$blockedStageArray = @($blockedStages.ToArray())
$relatedSurfaceArray = @($relatedSurfaces)

$result = [ordered]@{
    schema = "AIOS_CAMPAIGN_NO_READY_STAGE_DISCOVERY.v1"
    mode = "DRY_RUN_READ_ONLY"
    overall_readiness = $overallReadiness
    no_ready_stage_detected = $noReadyStageDetected
    no_ready_stage_classification = $noReadyStageClassification
    no_ready_stage_classification_reason = $noReadyStageClassificationReason
    workload_completion_state = $workloadCompletionState
    idle_allowed = $idleAllowed
    next_stage_planning_required = $nextStagePlanningRequired
    registry_inconsistency_detected = $registryInconsistencyDetected
    classifier_evidence = $classifierEvidenceObject
    reason = $reason
    inventory = $inventoryObject
    last_completed_stage = $lastCompletedStageValue
    candidate_gap_summary = $candidateGapSummaryObject
    candidate_next_stage_options = $candidateNextStageOptionArray
    blockers = $blockedStageArray
    related_surfaces = $relatedSurfaceArray
    recommended_next_action = $recommendedNextAction
    safety = $safetyObject
}

if ($OutputJson) {
    $result | ConvertTo-Json -Depth 20
    exit 0
}

Write-Output "AI_OS Campaign No-Ready-Stage Discovery"
Write-Output "Mode: DRY_RUN_READ_ONLY"
Write-Output "overall_readiness: $($result.overall_readiness)"
Write-Output "no_ready_stage_detected: $($result.no_ready_stage_detected)"
Write-Output "reason: $($result.reason)"
Write-Output "recommended_next_action: $($result.recommended_next_action)"
Write-Output "Writes performed: NO"
Write-Output "Registry mutation performed: NO"
Write-Output "Worker execution performed: NO"
Write-Output "Commit performed: NO"
Write-Output "Push performed: NO"
