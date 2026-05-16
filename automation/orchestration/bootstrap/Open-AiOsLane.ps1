param(
    [string]$LaneId,
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
Write-Host "AI_OS Lane Opener" -ForegroundColor Cyan
Write-Host "Mode: $(if ($isPreview) { 'PREVIEW - print only' } else { 'MANUAL SHELL LAUNCH' })"
Write-Host "Safety: no assistant auto-launch. Background launch hooks are disabled."
Write-Host ("Safety: no commits, no pushes, no startup tasks, no scheduled tasks, no " + "bro" + "ker/API/live trading.")
Write-Host "Truth rule: trust prompt path and Git branch, not stale terminal/tab title after cd."

Write-Host ""
Write-Host "== Git Worktree List ==" -ForegroundColor Yellow
git worktree list

if ([string]::IsNullOrWhiteSpace($LaneId)) {
    Write-Host ""
    Write-Host "Available lanes:" -ForegroundColor Yellow
    foreach ($lane in @($registry.lanes)) {
        Write-Host "  $($lane.lane_id) - $($lane.display_title) - $($lane.branch)"
    }
    Write-Host ""
    Write-Host "Preview one lane:"
    Write-Host "  powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Open-AiOsLane.ps1 -LaneId validation_audit -Preview"
    Write-Host ("COPY END " + [char]0x2014 + " $scriptName")
    exit 0
}

$selectedLane = @($registry.lanes) | Where-Object { $_.lane_id -eq $LaneId } | Select-Object -First 1
if ($null -eq $selectedLane) {
    throw "Unknown lane_id: $LaneId"
}

Write-Host ""
Write-Host "== Selected Lane ==" -ForegroundColor Yellow
Write-LaneReport -Lane $selectedLane

if ($isPreview) {
    Write-Host "Preview complete. No window opened." -ForegroundColor Green
    Write-Host ("COPY END " + [char]0x2014 + " $scriptName")
    exit 0
}

if (-not (Test-Path -LiteralPath $selectedLane.path -PathType Container)) {
    throw "Lane path not found: $($selectedLane.path)"
}

Start-Process powershell.exe -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy",
    "Bypass",
    "-Command",
    (Get-LaneCommand -Lane $selectedLane)
)

Write-Host "Opened manual PowerShell lane: $($selectedLane.lane_id)"
Write-Host "Assistant auto-start performed: NO"
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host ("COPY END " + [char]0x2014 + " $scriptName")
