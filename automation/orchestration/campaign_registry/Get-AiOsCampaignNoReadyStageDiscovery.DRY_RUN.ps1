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

$totalPhases = 0
foreach ($campaign in @($registry.campaigns)) {
    $totalPhases += @($campaign.phases).Count

    foreach ($stage in @($campaign.stages)) {
        $bucket = Get-StageStatusBucket -Status ([string]$stage.status)
        if ($statusCounts.Contains($bucket)) {
            $statusCounts[$bucket] = [int]$statusCounts[$bucket] + 1
        }
        else {
            $statusCounts["UNKNOWN"] = [int]$statusCounts["UNKNOWN"] + 1
        }

        $summary = Convert-StageSummary -Campaign $campaign -Stage $stage -StageMap $stageMap
        [void]$allStageSummaries.Add($summary)

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
        }
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

$recommendedNextAction = if ($noReadyStageDetected) {
    "Review campaign registry gaps and create a supervised DRY_RUN packet candidate for the next autonomy stage."
}
else {
    "Use the campaign next-task selector output before running no-ready-stage discovery."
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
$candidateNextStageOptionArray = @($candidateNextStageOptions.ToArray())
$blockedStageArray = @($blockedStages.ToArray())
$relatedSurfaceArray = @($relatedSurfaces)

$result = [ordered]@{
    schema = "AIOS_CAMPAIGN_NO_READY_STAGE_DISCOVERY.v1"
    mode = "DRY_RUN_READ_ONLY"
    overall_readiness = $overallReadiness
    no_ready_stage_detected = $noReadyStageDetected
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
