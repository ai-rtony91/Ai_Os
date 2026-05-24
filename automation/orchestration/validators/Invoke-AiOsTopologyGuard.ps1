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

function ConvertTo-NormalizedPath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    return ([System.IO.Path]::GetFullPath($Path)).TrimEnd("\", "/").ToLowerInvariant()
}

function Invoke-GitChecked {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,

        [Parameter(Mandatory = $true)]
        [string[]]$Arguments,

        [Parameter(Mandatory = $true)]
        [string]$LaneId,

        [Parameter(Mandatory = $true)]
        [string]$Field
    )

    $output = & git -C $Path @Arguments 2>&1
    if ($LASTEXITCODE -ne 0) {
        Stop-AiOsTopologyGuard -Reason "git -C '$Path' $($Arguments -join ' ') failed: $output" -LaneId $LaneId -Field $Field
    }

    return $output
}

function Get-GitWorktreeMap {
    param(
        [Parameter(Mandatory = $true)]
        [string]$RepoRoot
    )

    $output = Invoke-GitChecked -Path $RepoRoot -Arguments @("worktree", "list", "--porcelain") -LaneId "registry" -Field "worktree"
    $map = @{}
    $currentPath = $null
    $currentBranch = $null

    foreach ($line in @($output)) {
        if ([string]::IsNullOrWhiteSpace($line)) {
            if ($currentPath) {
                $map[(ConvertTo-NormalizedPath -Path $currentPath)] = [pscustomobject]@{
                    Path = $currentPath
                    Branch = $currentBranch
                }
            }
            $currentPath = $null
            $currentBranch = $null
            continue
        }

        if ($line -like "worktree *") {
            $currentPath = $line.Substring("worktree ".Length)
            continue
        }

        if ($line -like "branch refs/heads/*") {
            $currentBranch = $line.Substring("branch refs/heads/".Length)
        }
    }

    if ($currentPath) {
        $map[(ConvertTo-NormalizedPath -Path $currentPath)] = [pscustomobject]@{
            Path = $currentPath
            Branch = $currentBranch
        }
    }

    return $map
}

function Resolve-LanePath {
    param(
        [Parameter(Mandatory = $true)]
        [object]$Lane,

        [Parameter(Mandatory = $true)]
        [string]$RepoRoot
    )

    switch ($Lane.path_mode) {
        "main_control" {
            Assert-RequiredValue -Value $Lane.worktree_path -LaneId $Lane.lane_id -Field "worktree_path"
            return [string]$Lane.worktree_path
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

function Assert-NoDuplicateValue {
    param(
        [Parameter()]
        [AllowEmptyCollection()]
        [object[]]$Items,

        [Parameter(Mandatory = $true)]
        [string]$PropertyName,

        [Parameter(Mandatory = $true)]
        [string]$Scope
    )

    if ($null -eq $Items -or $Items.Count -eq 0) {
        return
    }

    $duplicates = $Items |
        Where-Object { $null -ne $_.$PropertyName -and -not [string]::IsNullOrWhiteSpace([string]$_.$PropertyName) } |
        Group-Object -Property $PropertyName |
        Where-Object { $_.Count -gt 1 }

    if ($duplicates) {
        Stop-AiOsTopologyGuard -Reason "Duplicate $PropertyName in $Scope`: $($duplicates[0].Name)" -LaneId $duplicates[0].Group[0].lane_id -Field $PropertyName
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
    Assert-RequiredValue -Value $Registry.repo_remote -LaneId "registry" -Field "repo_remote"
    Assert-RequiredValue -Value $Registry.launch_policy -LaneId "registry" -Field "launch_policy"
    Assert-RequiredValue -Value $Registry.codex_policy -LaneId "registry" -Field "codex_policy"
    Assert-RequiredValue -Value $Registry.create_policy -LaneId "registry" -Field "create_policy"

    if ($Registry.schema_version -ne "5.0") {
        Stop-AiOsTopologyGuard -Reason "Unsupported registry schema version: $($Registry.schema_version)" -LaneId "registry" -Field "schema_version"
    }

    if ($Registry.status -ne "canonical_topology_authority") {
        Stop-AiOsTopologyGuard -Reason "Registry is not marked canonical_topology_authority." -LaneId "registry" -Field "status"
    }

    if ($Registry.launch_policy -ne "manual_preview_required") {
        Stop-AiOsTopologyGuard -Reason "Top-level launch policy must be manual_preview_required." -LaneId "registry" -Field "launch_policy"
    }

    if ($Registry.codex_policy -ne "manual_only") {
        Stop-AiOsTopologyGuard -Reason "Top-level codex_policy must be manual_only." -LaneId "registry" -Field "codex_policy"
    }

    if ($Registry.create_policy -ne "never_from_launcher") {
        Stop-AiOsTopologyGuard -Reason "Top-level create_policy must be never_from_launcher." -LaneId "registry" -Field "create_policy"
    }

    $registryJson = $Registry | ConvertTo-Json -Depth 80
    $legacyRepoToken = "ai-rtony91_" + "Ai_Os_" + "CLEAN"
    if ($registryJson -match $legacyRepoToken) {
        Stop-AiOsTopologyGuard -Reason "Legacy CLEAN path reference found in registry." -LaneId "registry" -Field "path"
    }

    $activeLanes = @($Registry.active_lanes)
    if ($activeLanes.Count -lt 1) {
        Stop-AiOsTopologyGuard -Reason "Registry has no active lanes." -LaneId "registry" -Field "active_lanes"
    }

    Assert-NoDuplicateValue -Items $activeLanes -PropertyName "lane_id" -Scope "active_lanes"
    Assert-NoDuplicateValue -Items $activeLanes -PropertyName "window_title" -Scope "active_lanes"
    Assert-NoDuplicateValue -Items $activeLanes -PropertyName "tab_title" -Scope "active_lanes"

    $activeWorkerLanes = @($activeLanes | Where-Object { $_.path_mode -eq "explicit_worktree" })
    Assert-NoDuplicateValue -Items $activeWorkerLanes -PropertyName "branch" -Scope "active worker lanes"
    Assert-NoDuplicateValue -Items $activeWorkerLanes -PropertyName "worktree_path" -Scope "active worker lanes"

    $worktreeMap = Get-GitWorktreeMap -RepoRoot $RepoRoot
    $branchToWorktree = @{}
    foreach ($key in $worktreeMap.Keys) {
        $entry = $worktreeMap[$key]
        if (-not [string]::IsNullOrWhiteSpace($entry.Branch)) {
            $branchToWorktree[$entry.Branch] = $entry.Path
        }
    }

    foreach ($lane in $activeLanes) {
        Assert-RequiredValue -Value $lane.lane_id -LaneId "UNKNOWN" -Field "lane_id"
        $laneId = [string]$lane.lane_id

        foreach ($field in @("worker_id", "mode", "path_mode", "worktree_path", "base_branch", "branch", "repo_remote", "display_title", "window_title", "tab_title", "role", "launch_policy", "codex_policy", "create_policy", "stop_rule")) {
            Assert-RequiredValue -Value $lane.$field -LaneId $laneId -Field $field
        }

        foreach ($arrayField in @("allowed_paths", "blocked_paths")) {
            if (@($lane.PSObject.Properties.Name) -notcontains $arrayField) {
                Stop-AiOsTopologyGuard -Reason "Required field is missing." -LaneId $laneId -Field $arrayField
            }
        }

        if (@($Registry.allowed_modes) -notcontains $lane.mode) {
            Stop-AiOsTopologyGuard -Reason "Lane mode is not allowed: $($lane.mode)" -LaneId $laneId -Field "mode"
        }

        if (@($Registry.allowed_launch_policies) -notcontains $lane.launch_policy) {
            Stop-AiOsTopologyGuard -Reason "Launch policy is not allowed: $($lane.launch_policy)" -LaneId $laneId -Field "launch_policy"
        }

        if (@($Registry.allowed_path_modes) -notcontains $lane.path_mode) {
            Stop-AiOsTopologyGuard -Reason "Path mode is not allowed: $($lane.path_mode)" -LaneId $laneId -Field "path_mode"
        }

        if ($lane.codex_policy -ne "manual_only") {
            Stop-AiOsTopologyGuard -Reason "codex_policy must be manual_only." -LaneId $laneId -Field "codex_policy"
        }

        if ($lane.path_mode -eq "main_control") {
            if ($lane.lane_id -ne "main_control" -or $lane.branch -ne "main") {
                Stop-AiOsTopologyGuard -Reason "main_control path_mode is reserved for lane_id main_control on branch main." -LaneId $laneId -Field "path_mode"
            }
        } elseif ($lane.path_mode -eq "explicit_worktree") {
            if ($lane.branch -eq "main") {
                Stop-AiOsTopologyGuard -Reason "Worker lane targets main branch. Worker lanes require a non-main branch." -LaneId $laneId -Field "branch"
            }
        } else {
            Stop-AiOsTopologyGuard -Reason "Active lane is not launchable." -LaneId $laneId -Field "path_mode"
        }

        if ($lane.launch_policy -eq "disabled") {
            Stop-AiOsTopologyGuard -Reason "Active lane is disabled." -LaneId $laneId -Field "launch_policy"
        }

        $resolvedPath = Resolve-LanePath -Lane $lane -RepoRoot $RepoRoot
        $normalizedPath = ConvertTo-NormalizedPath -Path $resolvedPath

        if (-not (Test-Path -LiteralPath $resolvedPath -PathType Container)) {
            Stop-AiOsTopologyGuard -Reason "Resolved lane path does not exist: $resolvedPath" -LaneId $laneId -Field "worktree_path"
        }

        if (-not $worktreeMap.ContainsKey($normalizedPath)) {
            Stop-AiOsTopologyGuard -Reason "Folder exists but is not listed by git worktree list --porcelain. Treat as stale leftover folder; do not repair or delete from this lane: $resolvedPath" -LaneId $laneId -Field "worktree_path"
        }

        $listedWorktree = $worktreeMap[$normalizedPath]
        if ($listedWorktree.Branch -ne $lane.branch) {
            Stop-AiOsTopologyGuard -Reason "Git worktree branch mismatch. Expected '$($lane.branch)', found '$($listedWorktree.Branch)'." -LaneId $laneId -Field "branch"
        }

        if ($lane.path_mode -eq "explicit_worktree" -and $branchToWorktree.ContainsKey([string]$lane.branch)) {
            $listedPath = ConvertTo-NormalizedPath -Path $branchToWorktree[[string]$lane.branch]
            if ($listedPath -ne $normalizedPath) {
                Stop-AiOsTopologyGuard -Reason "Branch '$($lane.branch)' is already checked out in a different worktree: $($branchToWorktree[[string]$lane.branch])" -LaneId $laneId -Field "branch"
            }
        }

        $currentBranch = (Invoke-GitChecked -Path $resolvedPath -Arguments @("branch", "--show-current") -LaneId $laneId -Field "branch") -join "`n"
        if ($currentBranch.Trim() -ne $lane.branch) {
            Stop-AiOsTopologyGuard -Reason "Absolute git -C branch mismatch. Expected '$($lane.branch)', found '$currentBranch'." -LaneId $laneId -Field "branch"
        }

        $remote = (Invoke-GitChecked -Path $resolvedPath -Arguments @("remote", "get-url", "origin") -LaneId $laneId -Field "repo_remote") -join "`n"
        if ($remote.Trim() -ne $lane.repo_remote -or $remote.Trim() -ne $Registry.repo_remote) {
            Stop-AiOsTopologyGuard -Reason "Remote mismatch. Registry '$($Registry.repo_remote)', lane '$($lane.repo_remote)', found '$remote'." -LaneId $laneId -Field "repo_remote"
        }

        [void](Invoke-GitChecked -Path $resolvedPath -Arguments @("status", "--short", "--branch") -LaneId $laneId -Field "status")
    }

    return [pscustomobject]@{
        Status = "PASS"
        SchemaVersion = $Registry.schema_version
        ActiveLaneCount = $activeLanes.Count
        ActiveWorkerLaneCount = $activeWorkerLanes.Count
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
Write-Host "Active worker lanes validated: $($result.ActiveWorkerLaneCount)"
Write-Host "Optional inactive lanes observed: $($result.OptionalInactiveLaneCount)"
Write-Host "Repo root: $($result.RepoRoot)"
Write-Host "No launchers, lanes, workers, runtime, telemetry, dashboard, worktree creation/deletion, or Codex actions were executed."

$result | Add-Member -NotePropertyName RegistryPath -NotePropertyValue $resolvedRegistryPath -PassThru |
    Add-Member -NotePropertyName Registry -NotePropertyValue $registry -PassThru
