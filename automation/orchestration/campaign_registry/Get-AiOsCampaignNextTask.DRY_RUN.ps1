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

$resolvedRegistryPath = Resolve-AiOsLocalPath -Path $RegistryPath
if (-not (Test-Path -LiteralPath $resolvedRegistryPath -PathType Leaf)) {
    throw "Campaign registry not found: $RegistryPath"
}

$registry = Get-Content -LiteralPath $resolvedRegistryPath -Raw | ConvertFrom-Json
$stageMap = Get-StageMap -Campaigns $registry.campaigns
$candidates = New-Object System.Collections.Generic.List[object]

foreach ($campaign in @($registry.campaigns)) {
    foreach ($stage in @($campaign.stages)) {
        $stageStatus = [string]$stage.status
        $stageBlockers = @($stage.blocked_by | Where-Object { -not [string]::IsNullOrWhiteSpace([string]$_) })
        $campaignBlockers = @($campaign.blocked_by | Where-Object { -not [string]::IsNullOrWhiteSpace([string]$_) })
        $dependenciesComplete = Test-DependenciesComplete -Stage $stage -StageMap $stageMap

        if ($stageStatus -ne "READY") {
            continue
        }

        if ($stageBlockers.Count -gt 0 -or $campaignBlockers.Count -gt 0) {
            continue
        }

        if (-not $dependenciesComplete) {
            continue
        }

        $phase = @($campaign.phases | Where-Object { [string]$_.phase_id -eq [string]$stage.phase_id } | Select-Object -First 1)

        $candidates.Add([pscustomobject]@{
            campaign = $campaign
            phase = if ($phase.Count -gt 0) { $phase[0] } else { $null }
            stage = $stage
            priority_rank = Get-PriorityRank -Priority ([string]$stage.priority)
            campaign_priority_rank = Get-PriorityRank -Priority ([string]$campaign.priority)
        }) | Out-Null
    }
}

$selected = @($candidates | Sort-Object priority_rank, campaign_priority_rank, @{ Expression = { [string]$_.campaign.campaign_id } }, @{ Expression = { [string]$_.stage.stage_id } } | Select-Object -First 1)

if ($selected.Count -eq 0) {
    $result = [pscustomobject]@{
        schema = "AIOS_CAMPAIGN_NEXT_TASK_RECOMMENDATION.v1"
        mode = "DRY_RUN_READ_ONLY"
        generated_utc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
        recommended_campaign = $null
        recommended_phase = $null
        recommended_stage = $null
        recommended_worker = $null
        recommended_lane = $null
        next_packet_candidate = $null
        reason = "No READY stage with complete dependencies and no blockers was found."
        blockers = @("No selectable campaign stage.")
        next_safe_action = "Review campaign registry statuses and dependencies before requesting a packet."
        overall_readiness = "NO_READY_STAGE"
        safety = [pscustomobject]@{
            planning_only = $true
            writes_files = $false
            approves_apply = $false
            runs_workers = $false
            mutates_registry = $false
            commits = $false
            pushes = $false
        }
    }
}
else {
    $item = $selected[0]
    $stageBlockers = @($item.stage.blocked_by | Where-Object { -not [string]::IsNullOrWhiteSpace([string]$_) })
    $campaignBlockers = @($item.campaign.blocked_by | Where-Object { -not [string]::IsNullOrWhiteSpace([string]$_) })

    $result = [pscustomobject]@{
        schema = "AIOS_CAMPAIGN_NEXT_TASK_RECOMMENDATION.v1"
        mode = "DRY_RUN_READ_ONLY"
        generated_utc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
        recommended_campaign = [pscustomobject]@{
            campaign_id = $item.campaign.campaign_id
            title = $item.campaign.title
            status = $item.campaign.status
            priority = $item.campaign.priority
            completion_percent = $item.campaign.completion_percent
        }
        recommended_phase = [pscustomobject]@{
            phase_id = if ($null -ne $item.phase) { $item.phase.phase_id } else { $item.stage.phase_id }
            title = if ($null -ne $item.phase) { $item.phase.title } else { "UNKNOWN" }
            status = if ($null -ne $item.phase) { $item.phase.status } else { "UNKNOWN" }
        }
        recommended_stage = [pscustomobject]@{
            stage_id = $item.stage.stage_id
            title = $item.stage.title
            status = $item.stage.status
            priority = $item.stage.priority
            depends_on = @($item.stage.depends_on)
        }
        recommended_worker = $item.campaign.recommended_worker
        recommended_lane = $item.campaign.crew_lane
        next_packet_candidate = $item.stage.next_packet_candidate
        reason = "Selected highest-priority READY stage with complete dependencies and no blockers."
        blockers = @($campaignBlockers + $stageBlockers)
        next_safe_action = "Create or review packet candidate '$($item.stage.next_packet_candidate)' as DRY_RUN first. Human Owner approval is required before APPLY."
        overall_readiness = "READY_FOR_PACKET_PREVIEW"
        safety = [pscustomobject]@{
            planning_only = $true
            writes_files = $false
            approves_apply = $false
            runs_workers = $false
            mutates_registry = $false
            commits = $false
            pushes = $false
        }
    }
}

if ($OutputJson) {
    $result | ConvertTo-Json -Depth 12
    exit 0
}

Write-Output "AI_OS Campaign Next Task Recommendation"
Write-Output "Mode: DRY_RUN_READ_ONLY"
Write-Output "Campaign: $($result.recommended_campaign.campaign_id)"
Write-Output "Stage: $($result.recommended_stage.stage_id)"
Write-Output "Reason: $($result.reason)"
Write-Output "Next safe action: $($result.next_safe_action)"
Write-Output "Writes performed: NO"
Write-Output "Worker execution performed: NO"
Write-Output "Commit performed: NO"
Write-Output "Push performed: NO"
