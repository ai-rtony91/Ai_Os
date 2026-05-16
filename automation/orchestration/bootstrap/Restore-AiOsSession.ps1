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
    param(
        [Parameter(Mandatory = $true)]$Lane,
        [Parameter(Mandatory = $true)][string]$IdentityScriptPath
    )

    $escapedPath = $Lane.path.Replace("'", "''")
    $escapedIdentityScriptPath = $IdentityScriptPath.Replace("'", "''")
    $laneJson = $Lane | ConvertTo-Json -Depth 8 -Compress
    $laneJsonBase64 = [System.Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($laneJson))

    $command = "Set-Location -LiteralPath '$escapedPath'; & '$escapedIdentityScriptPath' -LaneJsonBase64 '$laneJsonBase64'; Write-Host 'Trust prompt path and Git branch, not stale terminal/tab title after cd.' -ForegroundColor Yellow; git status --short --branch"
    if (Test-CodexLane -Lane $Lane) {
        $escapedDisplayTitle = $Lane.display_title.Replace("'", "''")
        $command += "; Write-Host 'Manual Codex lane needed: $escapedDisplayTitle' -ForegroundColor Yellow; Write-Host 'Command: cd $escapedPath; codex'"
    }

    return $command
}

function Test-CodexLane {
    param([Parameter(Mandatory = $true)]$Lane)

    return (
        $Lane.lane_id.IndexOf("codex", [System.StringComparison]::OrdinalIgnoreCase) -ge 0 -or
        $Lane.display_title.IndexOf("codex", [System.StringComparison]::OrdinalIgnoreCase) -ge 0
    )
}

function Get-WtManualCommand {
    param(
        [Parameter(Mandatory = $true)]$Lane,
        [Parameter(Mandatory = $true)][string]$IdentityScriptPath
    )

    $escapedPath = $Lane.path.Replace('"', '\"')
    $escapedIdentityScriptPath = $IdentityScriptPath.Replace('"', '\"')
    $laneJson = $Lane | ConvertTo-Json -Depth 8 -Compress
    $laneJsonBase64 = [System.Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($laneJson))
    return "cd `"$escapedPath`"; powershell -ExecutionPolicy Bypass -File `"$escapedIdentityScriptPath`" -LaneJsonBase64 `"$laneJsonBase64`"; git status --short --branch"
}

function Open-LaneTab {
    param(
        [Parameter(Mandatory = $true)]$Lane,
        [Parameter(Mandatory = $true)][string]$IdentityScriptPath
    )

    Start-Process -FilePath "wt.exe" -ArgumentList @(
        "-w",
        "0",
        "new-tab",
        "--title",
        $Lane.tab_title,
        "powershell.exe",
        "-NoExit",
        "-ExecutionPolicy",
        "Bypass",
        "-Command",
        (Get-LaneCommand -Lane $Lane -IdentityScriptPath $IdentityScriptPath)
    )
}

if ($Preview -and $LaunchManualShells) {
    throw "Use either -Preview or -LaunchManualShells, not both."
}

$isPreview = -not $LaunchManualShells
$scriptName = Split-Path -Leaf $PSCommandPath
$fullSessionPath = Resolve-AiOsPath -Path $SessionPath
$identityScriptPath = Join-Path $PSScriptRoot "Set-AiOsTerminalIdentity.ps1"
if (-not (Test-Path -LiteralPath $identityScriptPath -PathType Leaf)) {
    throw "Terminal identity helper not found: $identityScriptPath"
}

if (Test-Path -LiteralPath $fullSessionPath -PathType Leaf) {
    $statePath = $fullSessionPath
} else {
    throw "No session state found: $fullSessionPath"
}

$session = Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json
$restorableLanes = @($session.lanes | Where-Object { $_.lane_id -eq "main_control" }) + @($session.lanes | Where-Object { $_.lane_id -ne "main_control" })

Write-Host ("COPY START " + [char]0x2014 + " $scriptName")
Write-Host "AI_OS Session Restore" -ForegroundColor Cyan
Write-Host "Mode: $(if ($isPreview) { 'PREVIEW - print only' } else { 'MANUAL SHELL LAUNCH' })"
Write-Host "State: $statePath"
Write-Host "launch_policy: windows_terminal_tab_only"
Write-Host "fallback_policy: print_manual_command"
Write-Host "Safety: no assistant auto-launch. Background launch hooks are disabled."
Write-Host ("Safety: no commits, no pushes, no startup tasks, no scheduled tasks, no " + "bro" + "ker/API/live trading.")
Write-Host "Truth rule: trust prompt path and Git branch, not stale terminal/tab title after cd."

Write-Host ""
Write-Host "== Git Worktree List ==" -ForegroundColor Yellow
git worktree list

Write-Host ""
Write-Host "== Restorable Lanes ==" -ForegroundColor Yellow
foreach ($lane in @($restorableLanes)) {
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
    Write-Host "Preview complete. No tabs opened." -ForegroundColor Green
    Write-Host ("COPY END " + [char]0x2014 + " $scriptName")
    exit 0
}

$wtCommand = Get-Command wt.exe -ErrorAction SilentlyContinue
if ($null -eq $wtCommand) {
    Write-Host "Windows Terminal unavailable. Fallback manual commands:" -ForegroundColor Yellow
    foreach ($lane in @($restorableLanes)) {
        Write-Host (Get-WtManualCommand -Lane $lane -IdentityScriptPath $identityScriptPath)
    }
    Write-Host "Tabs opened: 0"
    Write-Host "Restore complete. Assistant auto-start performed: NO"
    Write-Host "Commit performed: NO"
    Write-Host "Push performed: NO"
    Write-Host ("COPY END " + [char]0x2014 + " $scriptName")
    exit 0
}

foreach ($lane in @($restorableLanes)) {
    if (-not (Test-Path -LiteralPath $lane.path -PathType Container)) {
        throw "Lane path not found for $($lane.lane_id): $($lane.path)"
    }

    Open-LaneTab -Lane $lane -IdentityScriptPath $identityScriptPath
    Write-Host "Opened Windows Terminal tab: $($lane.lane_id)"
}

Write-Host "Restore complete. Assistant auto-start performed: NO"
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host ("COPY END " + [char]0x2014 + " $scriptName")
