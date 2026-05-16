param(
    [switch]$Preview,
    [switch]$LaunchManualShells,
    [string]$SessionPath = "automation/orchestration/terminal_workstations/AIOS_SESSION_STATE.example.json"
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
$fullSessionPath = Resolve-AiOsPath -Path $SessionPath

if (Test-Path -LiteralPath $fullSessionPath -PathType Leaf) {
    $statePath = $fullSessionPath
} else {
    throw "No session state found: $fullSessionPath"
}

$session = Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json

Write-Host ("COPY START " + [char]0x2014 + " $scriptName")
Write-Host "AI_OS Session Restore" -ForegroundColor Cyan
Write-Host "Mode: $(if ($isPreview) { 'PREVIEW - print only' } else { 'MANUAL SHELL LAUNCH' })"
Write-Host "State: $statePath"
Write-Host "Safety: no assistant auto-launch. Background launch hooks are disabled."
Write-Host ("Safety: no commits, no pushes, no startup tasks, no scheduled tasks, no " + "bro" + "ker/API/live trading.")
Write-Host "Truth rule: trust prompt path and Git branch, not stale terminal/tab title after cd."

Write-Host ""
Write-Host "== Git Worktree List ==" -ForegroundColor Yellow
git worktree list

Write-Host ""
Write-Host "== Restorable Lanes ==" -ForegroundColor Yellow
foreach ($lane in @($session.lanes)) {
    Write-LaneReport -Lane $lane
}

Write-Host ""
Write-Host "== Last Commands ==" -ForegroundColor Yellow
if ($session.PSObject.Properties.Name -contains "last_commands") {
    $session.last_commands.PSObject.Properties | ForEach-Object {
        Write-Host "$($_.Name): $($_.Value)"
    }
}

Write-Host ""
Write-Host "Next safe action: $($session.next_safe_action)"

if ($isPreview) {
    Write-Host "Preview complete. No windows opened." -ForegroundColor Green
    Write-Host ("COPY END " + [char]0x2014 + " $scriptName")
    exit 0
}

foreach ($lane in @($session.lanes)) {
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

Write-Host "Restore complete. Assistant auto-start performed: NO"
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host ("COPY END " + [char]0x2014 + " $scriptName")
