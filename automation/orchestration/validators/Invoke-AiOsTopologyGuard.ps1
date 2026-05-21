param(
    [string]$RegistryPath = "automation/orchestration/terminal_workstations/AIOS_WORKTREE_LANE_REGISTRY.json",
    [string]$RepoRootResolverPath = "automation/orchestration/bootstrap/Resolve-AiOsRepoRoot.ps1"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Stop-AiOsTopologyGuard {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Reason,

        [string]$LaneId = "registry",

        [string]$Field = "UNKNOWN"
    )

    Write-Host "AI_OS TOPOLOGY GUARD: STOP" -ForegroundColor Red
    Write-Host "Failure reason: $Reason" -ForegroundColor Red
    Write-Host "Failing lane_id: $LaneId" -ForegroundColor Red
    Write-Host "Failing field: $Field" -ForegroundColor Red
    Write-Host "Escalation summary: topology validation failed before launcher execution. Do not launch lanes, workers, runtime, or Codex. Review registry authority and rerun this guard." -ForegroundColor Yellow
    throw "AI_OS topology guard failed: $Reason"
}

function Assert-RequiredValue {
    param(
        [Parameter(Mandatory = $true)]
        [AllowNull()]
        [object]$Value,

        [Parameter(Mandatory = $true)]
        [string]$LaneId,

        [Parameter(Mandatory = $true)]
        [string]$Field
    )

    if ($null -eq $Value -or [string]::IsNullOrWhiteSpace([string]$Value)) {
        Stop-AiOsTopologyGuard -Reason "Required field is missing." -LaneId $LaneId -Field $Field
    }
}

function Resolve-GuardPath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,

        [Parameter(Mandatory = $true)]
        [string[]]$BasePaths
    )

    if ([System.IO.Path]::IsPathRooted($Path)) {
        return $Path
    }

    foreach ($basePath in $BasePaths) {
        Assert-RequiredValue -Value $basePath -LaneId "registry" -Field "BasePaths"
        $candidatePath = Join-Path $basePath $Path
        if (Test-Path -LiteralPath $candidatePath) {
            return $candidatePath
        }
    }

    return Join-Path $BasePaths[0] $Path
}

function Get-CurrentBranch {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,
        [Parameter(Mandatory = $true)]
        [string]$LaneId
    )

    $branchOutput = & git -C $Path branch --show-current 2>&1
    if ($LASTEXITCODE -ne 0) {
        Stop-AiOsTopologyGuard -Reason "Unable to read git branch for path: $Path" -LaneId $LaneId -Field "branch"
    }

    return [string]$branchOutput
}

function Resolve-LanePath {
    param(
        [Parameter(Mandatory = $true)]
        [object]$Lane,
        [Parameter(Mandatory = $true)]
        [string]$RepoRoot
    )

    switch ($Lane.path_mode) {
        "repo_root" {
            return $RepoRoot
        }
        "explicit_worktree" {
            Assert-RequiredValue -Value $Lane.worktree_path -LaneId $Lane.lane_id -Field "worktree_path"
            return [string]$Lane.worktree_path
        }
        default {
            Stop-AiOsTopologyGuard -Reason "Unsupported launchable path_mode." -LaneId $Lane.lane_id -Field "path_mode"
        }
    }
}

function Test-AiOsTopologyRegistry {
    param(
        [Parameter(Mandatory = $true)]
        [object]$Registry,
        [Parameter(Mandatory = $true)]
        [string]$RepoRoot
    )

    Assert-RequiredValue -Value $Registry.registry_id -LaneId "registry" -Field "registry_id"
    Assert-RequiredValue -Value $Registry.schema_version -LaneId "registry" -Field "schema_version"
    Assert-RequiredValue -Value $Registry.status -LaneId "registry" -Field "status"
    Assert-RequiredValue -Value $Registry.launch_policy -LaneId "registry" -Field "launch_policy"

    if ($Registry.schema_version -ne "4.0") {
        Stop-AiOsTopologyGuard -Reason "Unsupported registry schema version: $($Registry.schema_version)" -LaneId "registry" -Field "schema_version"
    }

    if ($Registry.status -ne "canonical_topology_authority") {
        Stop-AiOsTopologyGuard -Reason "Registry is not marked canonical_topology_authority." -LaneId "registry" -Field "status"
    }

    if ($Registry.launch_policy -ne "manual_preview_required") {
        Stop-AiOsTopologyGuard -Reason "Top-level launch policy must be manual_preview_required." -LaneId "registry" -Field "launch_policy"
    }

    $registryJson = $Registry | ConvertTo-Json -Depth 60
    $legacyRepoToken = "ai-rtony91_" + "Ai_Os_" + "CLEAN"
    if ($registryJson -match $legacyRepoToken) {
        Stop-AiOsTopologyGuard -Reason "Legacy CLEAN path reference found in registry." -LaneId "registry" -Field "path"
    }

    $activeLanes = @($Registry.active_lanes)
    if ($activeLanes.Count -lt 1) {
        Stop-AiOsTopologyGuard -Reason "Registry has no active lanes." -LaneId "registry" -Field "active_lanes"
    }

    $duplicateLaneIds = $activeLanes.lane_id | Group-Object | Where-Object { $_.Count -gt 1 }
    if ($duplicateLaneIds) {
        Stop-AiOsTopologyGuard -Reason "Duplicate active lane_id: $($duplicateLaneIds[0].Name)" -LaneId $duplicateLaneIds[0].Name -Field "lane_id"
    }

    foreach ($lane in $activeLanes) {
        Assert-RequiredValue -Value $lane.lane_id -LaneId "UNKNOWN" -Field "lane_id"
        $laneId = [string]$lane.lane_id

        foreach ($field in @("lane_category", "display_title", "window_title", "tab_title", "tab_color", "role", "path_mode", "branch", "launch_policy", "truth_source")) {
            Assert-RequiredValue -Value $lane.$field -LaneId $laneId -Field $field
        }

        if (@($Registry.allowed_lane_categories) -notcontains $lane.lane_category) {
            Stop-AiOsTopologyGuard -Reason "Lane category is not allowed: $($lane.lane_category)" -LaneId $laneId -Field "lane_category"
        }

        if (@($Registry.allowed_launch_policies) -notcontains $lane.launch_policy) {
            Stop-AiOsTopologyGuard -Reason "Launch policy is not allowed: $($lane.launch_policy)" -LaneId $laneId -Field "launch_policy"
        }

        if (@($Registry.allowed_path_modes) -notcontains $lane.path_mode) {
            Stop-AiOsTopologyGuard -Reason "Path mode is not allowed: $($lane.path_mode)" -LaneId $laneId -Field "path_mode"
        }

        if ($lane.branch -eq "main") {
            Stop-AiOsTopologyGuard -Reason "Active lane targets main branch." -LaneId $laneId -Field "branch"
        }

        if ($lane.launch_policy -eq "disabled") {
            Stop-AiOsTopologyGuard -Reason "Active lane is disabled." -LaneId $laneId -Field "launch_policy"
        }

        $resolvedPath = Resolve-LanePath -Lane $lane -RepoRoot $RepoRoot
        if (-not (Test-Path -LiteralPath $resolvedPath -PathType Container)) {
            Stop-AiOsTopologyGuard -Reason "Resolved lane path does not exist: $resolvedPath" -LaneId $laneId -Field "path_mode"
        }

        $currentBranch = Get-CurrentBranch -Path $resolvedPath -LaneId $laneId
        if ($currentBranch -ne $lane.branch) {
            Stop-AiOsTopologyGuard -Reason "Branch mismatch. Expected '$($lane.branch)', found '$currentBranch'." -LaneId $laneId -Field "branch"
        }
    }

    return [pscustomobject]@{
        Status = "PASS"
        SchemaVersion = $Registry.schema_version
        ActiveLaneCount = $activeLanes.Count
        OptionalInactiveLaneCount = @($Registry.optional_inactive_lanes).Count
        RepoRoot = $RepoRoot
    }
}

$orchestrationRoot = Split-Path -Parent $PSScriptRoot
$automationRoot = Split-Path -Parent $orchestrationRoot
$scriptRepoRootCandidate = Split-Path -Parent $automationRoot
$resolvedResolverPath = Resolve-GuardPath -Path $RepoRootResolverPath -BasePaths @(
    (Get-Location).Path,
    $scriptRepoRootCandidate,
    $orchestrationRoot
)

if (-not (Test-Path -LiteralPath $resolvedResolverPath -PathType Leaf)) {
    Stop-AiOsTopologyGuard -Reason "Repo root resolver not found: $resolvedResolverPath" -LaneId "registry" -Field "RepoRootResolverPath"
}

. $resolvedResolverPath

$repoRoot = Resolve-AiOsRepoRoot -StartPath $PSScriptRoot
$resolvedRegistryPath = Resolve-GuardPath -Path $RegistryPath -BasePaths @($repoRoot)

if (-not (Test-Path -LiteralPath $resolvedRegistryPath -PathType Leaf)) {
    Stop-AiOsTopologyGuard -Reason "Topology registry not found: $resolvedRegistryPath" -LaneId "registry" -Field "RegistryPath"
}

try {
    $registry = Get-Content -LiteralPath $resolvedRegistryPath -Raw | ConvertFrom-Json
} catch {
    Stop-AiOsTopologyGuard -Reason "Registry JSON parse failed: $($_.Exception.Message)" -LaneId "registry" -Field "json"
}

$result = Test-AiOsTopologyRegistry -Registry $registry -RepoRoot $repoRoot

Write-Host "AI_OS TOPOLOGY GUARD: PASS" -ForegroundColor Green
Write-Host "Mode: Validation only"
Write-Host "Registry: $resolvedRegistryPath"
Write-Host "Schema: $($result.SchemaVersion)"
Write-Host "Active lanes validated: $($result.ActiveLaneCount)"
Write-Host "Optional inactive lanes observed: $($result.OptionalInactiveLaneCount)"
Write-Host "Repo root: $($result.RepoRoot)"
Write-Host "No launchers, lanes, workers, runtime, telemetry, dashboard, or Codex actions were executed."

$result | Add-Member -NotePropertyName RegistryPath -NotePropertyValue $resolvedRegistryPath -PassThru |
    Add-Member -NotePropertyName Registry -NotePropertyValue $registry -PassThru
