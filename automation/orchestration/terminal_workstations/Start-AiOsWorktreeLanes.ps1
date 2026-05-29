param(
    [switch]$Preview,
    [switch]$OpenShells
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
        "main_control" {
            return [string]$Lane.worktree_path
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

    return "Set-Location -LiteralPath '$escapedPath'; `$Host.UI.RawUI.WindowTitle = '$escapedWindowTitle'; Write-Host '$escapedDisplayTitle'; Write-Host 'ROLE: $escapedRole'; Write-Host 'PATH: $escapedPath'; Write-Host 'BRANCH: $escapedBranch'; Write-Host 'No Codex auto-launch. No startup tasks. No scheduled tasks. No broker/API/live trading.' -ForegroundColor Red; git -C '$escapedPath' status --short --branch; git -C '$escapedPath' branch --show-current; git -C '$escapedPath' remote -v"
}

if ($Preview -and $OpenShells) {
    throw "Use either -Preview or -OpenShells. Preview/report-only is the default."
}

if (-not (Test-Path -LiteralPath $topologyGuardPath -PathType Leaf)) {
    throw "AI_OS topology guard not found: $topologyGuardPath"
}

$guardResult = & $topologyGuardPath -RegistryPath $registryPath -RepoRootResolverPath $repoRootResolverPath

if ($null -eq $guardResult -or $guardResult.Status -ne "PASS") {
    throw "AI_OS topology guard did not return PASS. Launcher stopped before consuming topology."
}

$repoRoot = [string]$guardResult.RepoRoot
$registry = $guardResult.Registry

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

$border = "#" * 100
$titleIcon = [char]::ConvertFromUtf32(0x1F5FA)  # World map - lane topology

Write-Host $border -ForegroundColor Yellow
Write-Host ""
Write-Host "  $titleIcon  AI_OS WORKTREE LANE RESTORE" -ForegroundColor Yellow
Write-Host ""
Write-Host "  AIOS BASE : #05070b  TEXT #e5f6ff  WARNING #ffd166  OCC/PASS #37ff88" -ForegroundColor DarkYellow
Write-Host "  OCC LANE  : ALL LANES  |  Worktree lane topology restore and shell launcher" -ForegroundColor Yellow
Write-Host "  MODE      : $(if ($OpenShells) { '[ OPEN_SHELLS ]  Manual shell launch after registry validation' } else { '[ PREVIEW    ]  Preview/report-only — no windows opened' })" -ForegroundColor DarkYellow
Write-Host "  STATUS    : [ READ-ONLY ]  No Codex auto-launch, no startup/scheduled tasks" -ForegroundColor DarkYellow
Write-Host "  Registry  : $registryPath" -ForegroundColor DarkYellow
Write-Host "  Schema    : $($registry.schema_version)" -ForegroundColor DarkYellow
Write-Host "  Authority : $($registry.status)" -ForegroundColor DarkYellow
Write-Host "  Repo root : $repoRoot" -ForegroundColor DarkYellow
Write-Host ""
Write-Host "  No Codex auto-launch. No startup tasks. No scheduled tasks. No commits. No pushes." -ForegroundColor Gray
Write-Host "  No installs. No broker/API/live trading." -ForegroundColor Gray
Write-Host "  Opening PowerShell shells requires the explicit -OpenShells switch." -ForegroundColor Gray
Write-Host ""
Write-Host $border -ForegroundColor Yellow

Write-Section -Title "Active Lane Mapping"
foreach ($resolvedLane in $resolvedLanes) {
    $lane = $resolvedLane.Lane
    Write-Host "LANE: $($lane.lane_id)" -ForegroundColor Cyan
    Write-Host "TITLE: $($lane.display_title)"
    Write-Host "WORKER_ID: $($lane.worker_id)"
    Write-Host "MODE: $($lane.mode)"
    Write-Host "PATH_MODE: $($lane.path_mode)"
    Write-Host "PATH: $($resolvedLane.Path)"
    Write-Host "BRANCH: $($resolvedLane.Branch)"
    Write-Host "LAUNCH_POLICY: $($lane.launch_policy)"
    Write-Host ""
}

Write-Section -Title "Inactive Optional Lanes"
foreach ($lane in @($registry.optional_inactive_lanes)) {
    Write-Host "SKIPPED: $($lane.lane_id) ($($lane.mode)) - $($lane.launch_policy)"
}

Write-Section -Title "Lane Commands"
foreach ($resolvedLane in $resolvedLanes) {
    $lane = $resolvedLane.Lane
    $startCommand = "Start-Process powershell.exe -ArgumentList @('-NoExit','-ExecutionPolicy','Bypass','-Command',`"$($resolvedLane.Command)`")"

    Write-Host "LANE: $($lane.lane_id)" -ForegroundColor Cyan
    Write-Host $startCommand

    if ($OpenShells) {
        Start-Process powershell.exe -ArgumentList @(
            "-NoExit",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            $resolvedLane.Command
        )
    }
}

if ($OpenShells) {
    Write-Host ""
    Write-Host "  [ COMPLETE ]  Lane windows opened from registry active_lanes only." -ForegroundColor Green
    Write-Host "  [ CONFIRM  ]  Codex was NOT launched. Commit: NO. Push: NO." -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "  [ COMPLETE ]  Preview complete. No PowerShell windows opened." -ForegroundColor Green
    Write-Host "  [ CONFIRM  ]  Run with -OpenShells to open lane windows. Commit: NO. Push: NO." -ForegroundColor Green
}
