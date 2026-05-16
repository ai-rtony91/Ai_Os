param(
    [switch]$Preview,
    [switch]$LaunchManualShells,
    [string]$RegistryPath = "automation/orchestration/terminal_workstations/AIOS_WORKTREE_LANE_REGISTRY.json"
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

function Resolve-AiOsPath {
    param([Parameter(Mandatory = $true)][string]$Path)

    if ([System.IO.Path]::IsPathRooted($Path)) {
        return $Path
    }

    return Join-Path (Get-Location).Path $Path
}

function Write-AiOsSection {
    param([Parameter(Mandatory = $true)][string]$Title)

    Write-Host ""
    Write-Host "== $Title ==" -ForegroundColor Yellow
}

function Write-LaneReport {
    param([Parameter(Mandatory = $true)]$Lane)

    Write-Host "lane_id: $($Lane.lane_id)" -ForegroundColor Cyan
    Write-Host "display_title: $($Lane.display_title)"
    Write-Host "window_title: $($Lane.window_title)"
    Write-Host "tab_title: $($Lane.tab_title)"
    Write-Host "emoji_marker: $($Lane.emoji_marker)"
    Write-Host "truth_source: $($Lane.truth_source)"
    Write-Host "path: $($Lane.path)"
    Write-Host "branch: $($Lane.branch)"
    Write-Host "role: $($Lane.role)"
    Write-Host ""
}

function Get-LaneCommand {
    param([Parameter(Mandatory = $true)]$Lane)

    $escapedPath = $Lane.path.Replace("'", "''")
    $escapedWindowTitle = $Lane.window_title.Replace("'", "''")
    $escapedDisplayTitle = $Lane.display_title.Replace("'", "''")
    $escapedTabTitle = $Lane.tab_title.Replace("'", "''")
    $escapedLaneId = $Lane.lane_id.Replace("'", "''")
    $escapedEmoji = $Lane.emoji_marker.Replace("'", "''")
    $escapedTruthSource = $Lane.truth_source.Replace("'", "''")
    $escapedBranch = $Lane.branch.Replace("'", "''")

    return "Set-Location -LiteralPath '$escapedPath'; `$Host.UI.RawUI.WindowTitle = '$escapedWindowTitle'; Write-Host '$escapedEmoji $escapedDisplayTitle' -ForegroundColor Cyan; Write-Host 'lane_id: $escapedLaneId'; Write-Host 'display_title: $escapedDisplayTitle'; Write-Host 'window_title: $escapedWindowTitle'; Write-Host 'tab_title: $escapedTabTitle'; Write-Host 'emoji_marker: $escapedEmoji'; Write-Host 'truth_source: $escapedTruthSource'; Write-Host 'path: $escapedPath'; Write-Host 'branch: $escapedBranch'; Write-Host 'Trust prompt path and Git branch, not stale terminal/tab title after cd.' -ForegroundColor Yellow; git status --short --branch"
}

if ($Preview -and $LaunchManualShells) {
    throw "Use either -Preview or -LaunchManualShells, not both."
}

$isPreview = -not $LaunchManualShells
$scriptName = Split-Path -Leaf $PSCommandPath
$fullRegistryPath = Resolve-AiOsPath -Path $RegistryPath
if (-not (Test-Path -LiteralPath $fullRegistryPath -PathType Leaf)) {
    throw "Lane registry not found: $fullRegistryPath"
}

$registry = Get-Content -LiteralPath $fullRegistryPath -Raw | ConvertFrom-Json

Write-Host ("COPY START " + [char]0x2014 + " $scriptName")
Write-Host "AI_OS Workspace Bootstrap" -ForegroundColor Cyan
Write-Host "Issue: #60"
Write-Host "Mode: $(if ($isPreview) { 'PREVIEW - print only' } else { 'MANUAL SHELL LAUNCH' })"
Write-Host "Registry: $fullRegistryPath"
Write-Host "Safety: no assistant auto-launch. Background launch hooks are disabled."
Write-Host ("Safety: no commits, no pushes, no startup tasks, no scheduled tasks, no " + "bro" + "ker/API/live trading.")
Write-Host "Truth rule: trust prompt path and Git branch, not stale terminal/tab title after cd."

Write-AiOsSection -Title "Git Worktree List"
git worktree list

Write-AiOsSection -Title "Lane Registry"
foreach ($lane in @($registry.lanes)) {
    Write-LaneReport -Lane $lane
}

Write-AiOsSection -Title "Operator Commands"
Write-Host "Preview workspace:"
Write-Host "  powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Start-AiOsWorkspace.ps1 -Preview"
Write-Host "Open all lane shells manually:"
Write-Host "  powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Start-AiOsWorkspace.ps1 -LaunchManualShells"
Write-Host "Preview one lane:"
Write-Host "  powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Open-AiOsLane.ps1 -LaneId bootstrap_git -Preview"
Write-Host "Save session metadata:"
Write-Host "  powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Save-AiOsSession.ps1 -Apply"
Write-Host "Restore session preview:"
Write-Host "  powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Restore-AiOsSession.ps1 -Preview"

if ($isPreview) {
    Write-Host ""
    Write-Host "Preview complete. Windows opened: NO" -ForegroundColor Green
    Write-Host "Assistant auto-start performed: NO"
    Write-Host "Commit performed: NO"
    Write-Host "Push performed: NO"
    Write-Host ("COPY END " + [char]0x2014 + " $scriptName")
    exit 0
}

foreach ($lane in @($registry.lanes)) {
    if (-not (Test-Path -LiteralPath $lane.path -PathType Container)) {
        throw "Lane path not found for $($lane.lane_id): $($lane.path)"
    }

    Start-Process powershell.exe -ArgumentList @(
        "-NoExit",
        "-ExecutionPolicy",
        "Bypass",
        "-Command",
        (Get-LaneCommand -Lane $lane)
    )
    Write-Host "Opened manual PowerShell lane: $($lane.lane_id)"
}

Write-Host "Workspace bootstrap complete. Assistant auto-start performed: NO"
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host ("COPY END " + [char]0x2014 + " $scriptName")
