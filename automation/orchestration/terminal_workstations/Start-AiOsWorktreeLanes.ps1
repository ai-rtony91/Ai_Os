param(
    [switch]$Preview
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$registryPath = Join-Path $PSScriptRoot "AIOS_WORKTREE_LANE_REGISTRY.json"
$repoRootResolverPath = Join-Path (Split-Path -Parent $PSScriptRoot) "bootstrap\Resolve-AiOsRepoRoot.ps1"

function Write-Section {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Title
    )

    Write-Host ""
    Write-Host "== $Title ==" -ForegroundColor Yellow
}

function Assert-RequiredValue {
    param(
        [Parameter(Mandatory = $true)]
        [object]$Value,

        [Parameter(Mandatory = $true)]
        [string]$Name
    )

    if ($null -eq $Value -or [string]::IsNullOrWhiteSpace([string]$Value)) {
        throw "Lane registry validation failed: missing $Name."
    }
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
            Assert-RequiredValue -Value $Lane.worktree_path -Name "$($Lane.lane_id).worktree_path"
            return [string]$Lane.worktree_path
        }
        default {
            throw "Lane $($Lane.lane_id) cannot launch with path_mode '$($Lane.path_mode)'."
        }
    }
}

function Get-CurrentBranch {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    $branch = & git -C $Path branch --show-current 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to read git branch for $Path`: $($branch | Select-Object -First 1)"
    }

    return [string]$branch
}

function Get-LaneCommand {
    param(
        [Parameter(Mandatory = $true)]
        [object]$Lane,

        [Parameter(Mandatory = $true)]
        [string]$ResolvedPath
    )

    $escapedPath = $ResolvedPath.Replace("'", "''")
    $escapedWindowTitle = ([string]$Lane.window_title).Replace("'", "''")
    $escapedDisplayTitle = ([string]$Lane.display_title).Replace("'", "''")
    $escapedRole = ([string]$Lane.role).Replace("'", "''")
    $escapedBranch = ([string]$Lane.branch).Replace("'", "''")

    return "Set-Location -LiteralPath '$escapedPath'; `$Host.UI.RawUI.WindowTitle = '$escapedWindowTitle'; Write-Host '$escapedDisplayTitle'; Write-Host 'ROLE: $escapedRole'; Write-Host 'PATH: $escapedPath'; Write-Host 'BRANCH: $escapedBranch'; Write-Host 'No Codex auto-launch. No startup tasks. No scheduled tasks. No broker/API/live trading.' -ForegroundColor Red; git status --short --branch"
}

if (-not (Test-Path -LiteralPath $registryPath -PathType Leaf)) {
    throw "AI_OS lane registry not found: $registryPath"
}

if (-not (Test-Path -LiteralPath $repoRootResolverPath -PathType Leaf)) {
    throw "AI_OS repo root resolver not found: $repoRootResolverPath"
}

. $repoRootResolverPath

$repoRoot = Resolve-AiOsRepoRoot -StartPath $PSScriptRoot
$registry = Get-Content -LiteralPath $registryPath -Raw | ConvertFrom-Json
$registryJson = $registry | ConvertTo-Json -Depth 40

$legacyRepoToken = "ai-rtony91_" + "Ai_Os_" + "CLEAN"
if ($registryJson -match $legacyRepoToken) {
    throw "Lane registry validation failed: stale legacy path reference found."
}

if ($registry.schema_version -ne "4.0") {
    throw "Lane registry validation failed: expected schema_version 4.0, found '$($registry.schema_version)'."
}

if ($registry.status -ne "canonical_topology_authority") {
    throw "Lane registry validation failed: expected canonical_topology_authority status, found '$($registry.status)'."
}

if ($registry.launch_policy -ne "manual_preview_required") {
    throw "Lane registry validation failed: expected manual_preview_required launch policy, found '$($registry.launch_policy)'."
}

$activeLanes = @($registry.active_lanes)
if ($activeLanes.Count -lt 1) {
    throw "Lane registry validation failed: active_lanes is empty."
}

$duplicateLaneIds = $activeLanes.lane_id | Group-Object | Where-Object { $_.Count -gt 1 }
if ($duplicateLaneIds) {
    throw "Lane registry validation failed: duplicate active lane_id '$($duplicateLaneIds[0].Name)'."
}

$resolvedLanes = @()

foreach ($lane in $activeLanes) {
    Assert-RequiredValue -Value $lane.lane_id -Name "lane_id"
    Assert-RequiredValue -Value $lane.lane_category -Name "$($lane.lane_id).lane_category"
    Assert-RequiredValue -Value $lane.display_title -Name "$($lane.lane_id).display_title"
    Assert-RequiredValue -Value $lane.window_title -Name "$($lane.lane_id).window_title"
    Assert-RequiredValue -Value $lane.tab_title -Name "$($lane.lane_id).tab_title"
    Assert-RequiredValue -Value $lane.tab_color -Name "$($lane.lane_id).tab_color"
    Assert-RequiredValue -Value $lane.role -Name "$($lane.lane_id).role"
    Assert-RequiredValue -Value $lane.path_mode -Name "$($lane.lane_id).path_mode"
    Assert-RequiredValue -Value $lane.branch -Name "$($lane.lane_id).branch"
    Assert-RequiredValue -Value $lane.launch_policy -Name "$($lane.lane_id).launch_policy"
    Assert-RequiredValue -Value $lane.truth_source -Name "$($lane.lane_id).truth_source"

    if (@($registry.allowed_lane_categories) -notcontains $lane.lane_category) {
        throw "Lane registry validation failed: lane $($lane.lane_id) has unsupported lane_category '$($lane.lane_category)'."
    }

    if (@($registry.allowed_launch_policies) -notcontains $lane.launch_policy) {
        throw "Lane registry validation failed: lane $($lane.lane_id) has unsupported launch_policy '$($lane.launch_policy)'."
    }

    if (@($registry.allowed_path_modes) -notcontains $lane.path_mode) {
        throw "Lane registry validation failed: lane $($lane.lane_id) has unsupported path_mode '$($lane.path_mode)'."
    }

    if ($lane.branch -eq "main") {
        throw "Lane registry validation failed: lane $($lane.lane_id) uses disallowed active branch 'main'."
    }

    if ($lane.launch_policy -eq "disabled") {
        throw "Lane registry validation failed: active lane $($lane.lane_id) is disabled."
    }

    $resolvedPath = Resolve-LanePath -Lane $lane -RepoRoot $repoRoot
    if (-not (Test-Path -LiteralPath $resolvedPath -PathType Container)) {
        throw "Lane path not found for $($lane.lane_id): $resolvedPath"
    }

    $currentBranch = Get-CurrentBranch -Path $resolvedPath
    if ($currentBranch -ne $lane.branch) {
        throw "Lane branch mismatch for $($lane.lane_id): expected '$($lane.branch)', found '$currentBranch'."
    }

    $resolvedLanes += [pscustomobject]@{
        Lane = $lane
        Path = $resolvedPath
        Branch = $currentBranch
        Command = Get-LaneCommand -Lane $lane -ResolvedPath $resolvedPath
    }
}

Write-Host "AI_OS WORKTREE LANE RESTORE" -ForegroundColor Yellow
Write-Host "Mode: $(if ($Preview) { 'Preview only - no windows opened' } else { 'Manual shell launch after registry validation' })"
Write-Host "Registry: $registryPath"
Write-Host "Schema: $($registry.schema_version)"
Write-Host "Topology authority: $($registry.status)"
Write-Host "Repo root: $repoRoot"
Write-Host "No Codex auto-launch. No startup tasks. No scheduled tasks. No commits. No pushes."
Write-Host "No installs. No broker/API/live trading."

Write-Section -Title "Active Lane Mapping"
foreach ($resolvedLane in $resolvedLanes) {
    $lane = $resolvedLane.Lane
    Write-Host "LANE: $($lane.lane_id)" -ForegroundColor Cyan
    Write-Host "TITLE: $($lane.display_title)"
    Write-Host "CATEGORY: $($lane.lane_category)"
    Write-Host "PATH_MODE: $($lane.path_mode)"
    Write-Host "PATH: $($resolvedLane.Path)"
    Write-Host "BRANCH: $($resolvedLane.Branch)"
    Write-Host "LAUNCH_POLICY: $($lane.launch_policy)"
    Write-Host ""
}

Write-Section -Title "Inactive Optional Lanes"
foreach ($lane in @($registry.optional_inactive_lanes)) {
    Write-Host "SKIPPED: $($lane.lane_id) ($($lane.lane_category)) - $($lane.launch_policy)"
}

Write-Section -Title "Lane Commands"
foreach ($resolvedLane in $resolvedLanes) {
    $lane = $resolvedLane.Lane
    $startCommand = "Start-Process powershell.exe -ArgumentList @('-NoExit','-ExecutionPolicy','Bypass','-Command',`"$($resolvedLane.Command)`")"

    Write-Host "LANE: $($lane.lane_id)" -ForegroundColor Cyan
    Write-Host $startCommand

    if (-not $Preview) {
        Start-Process powershell.exe -ArgumentList @(
            "-NoExit",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            $resolvedLane.Command
        )
    }
}

if ($Preview) {
    Write-Host ""
    Write-Host "Preview complete. No PowerShell windows opened." -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "Lane windows opened from registry active_lanes only. Codex was not launched." -ForegroundColor Green
}
