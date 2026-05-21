param(
    [switch]$Preview
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$registryPath = Join-Path $PSScriptRoot "AIOS_WORKTREE_LANE_REGISTRY.json"
$repoRootResolverPath = Join-Path (Split-Path -Parent $PSScriptRoot) "bootstrap\Resolve-AiOsRepoRoot.ps1"
$topologyGuardPath = Join-Path (Split-Path -Parent $PSScriptRoot) "validators\Invoke-AiOsTopologyGuard.ps1"

function Write-Section {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Title
    )

    Write-Host ""
    Write-Host "== $Title ==" -ForegroundColor Yellow
}

function Resolve-LaneCommandPath {
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
            return [string]$Lane.worktree_path
        }
        default {
            throw "Guard-approved lane $($Lane.lane_id) has unsupported command path_mode '$($Lane.path_mode)'."
        }
    }
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

if (-not (Test-Path -LiteralPath $topologyGuardPath -PathType Leaf)) {
    throw "AI_OS topology guard not found: $topologyGuardPath"
}

& $topologyGuardPath -RegistryPath $registryPath -RepoRootResolverPath $repoRootResolverPath -Preview

. $repoRootResolverPath

$repoRoot = Resolve-AiOsRepoRoot -StartPath $PSScriptRoot
$registry = Get-Content -LiteralPath $registryPath -Raw | ConvertFrom-Json

$activeLanes = @($registry.active_lanes)
$resolvedLanes = @()

foreach ($lane in $activeLanes) {
    $resolvedPath = Resolve-LaneCommandPath -Lane $lane -RepoRoot $repoRoot

    $resolvedLanes += [pscustomobject]@{
        Lane = $lane
        Path = $resolvedPath
        Branch = [string]$lane.branch
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
