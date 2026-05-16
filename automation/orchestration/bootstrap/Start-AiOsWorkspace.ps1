param(
    [string]$Intent = "",
    [switch]$Preview,
    [switch]$LaunchManualShells,
    [int]$MaxWindows = 3,
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
    param(
        [Parameter(Mandatory = $true)]$Lane,
        [Parameter(Mandatory = $true)][string]$IdentityScriptPath
    )

    $escapedPath = $Lane.path.Replace("'", "''")
    $escapedIdentityScriptPath = $IdentityScriptPath.Replace("'", "''")
    $escapedDisplayTitle = $Lane.display_title.Replace("'", "''")
    $laneJson = $Lane | ConvertTo-Json -Depth 8 -Compress
    $laneJsonBase64 = [System.Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($laneJson))

    $command = "Set-Location -LiteralPath '$escapedPath'; . '$escapedIdentityScriptPath' -LaneJsonBase64 '$laneJsonBase64'; git status --short --branch"
    if (Test-CodexLane -Lane $Lane) {
        $command += "; Write-Host 'Manual Codex lane needed: $escapedDisplayTitle' -ForegroundColor Yellow; Write-Host 'Command: cd $escapedPath; codex'"
    }

    return $command
}

function Get-EncodedLaneCommand {
    param(
        [Parameter(Mandatory = $true)]$Lane,
        [Parameter(Mandatory = $true)][string]$IdentityScriptPath
    )

    $command = Get-LaneCommand -Lane $Lane -IdentityScriptPath $IdentityScriptPath
    return [System.Convert]::ToBase64String([System.Text.Encoding]::Unicode.GetBytes($command))
}

function ConvertTo-ProcessArgument {
    param([Parameter(Mandatory = $true)][string]$Value)

    return '"' + $Value.Replace('"', '\"') + '"'
}

function Get-WtArgumentList {
    param(
        [Parameter(Mandatory = $true)]$Lane,
        [Parameter(Mandatory = $true)][string]$IdentityScriptPath
    )

    $encodedPayload = Get-EncodedLaneCommand -Lane $Lane -IdentityScriptPath $IdentityScriptPath
    $arguments = @(
        "-w",
        "0",
        "new-tab",
        "--title",
        [string]$Lane.tab_title,
        "-d",
        [string]$Lane.path,
        "powershell.exe",
        "-NoExit",
        "-ExecutionPolicy",
        "Bypass",
        "-EncodedCommand",
        $encodedPayload
    )

    return (@($arguments) | ForEach-Object { ConvertTo-ProcessArgument -Value $_ }) -join " "
}

function Get-RegistryLaneById {
    param(
        [Parameter(Mandatory = $true)]$Registry,
        [Parameter(Mandatory = $true)][string]$LaneId
    )

    return @($Registry.lanes) | Where-Object { $_.lane_id -eq $LaneId } | Select-Object -First 1
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

function Get-WtPreviewCommand {
    param([Parameter(Mandatory = $true)]$Lane)

    $escapedTitle = $Lane.tab_title.Replace('"', '\"')
    $escapedPath = $Lane.path.Replace('"', '\"')
    return "wt.exe `"-w`" `"0`" `"new-tab`" `"--title`" `"$escapedTitle`" `"-d`" `"$escapedPath`" `"powershell.exe`" `"-NoExit`" `"-ExecutionPolicy`" `"Bypass`" `"-EncodedCommand`" `"<base64 UTF-16LE lane payload>`""
}

function Open-LaneTab {
    param(
        [Parameter(Mandatory = $true)]$Lane,
        [Parameter(Mandatory = $true)][string]$IdentityScriptPath
    )

    Start-Process -FilePath "wt.exe" -ArgumentList (Get-WtArgumentList -Lane $Lane -IdentityScriptPath $IdentityScriptPath)
}

if ($Preview -and $LaunchManualShells) {
    throw "Use either -Preview or -LaunchManualShells, not both."
}

if ($MaxWindows -lt 1) {
    throw "MaxWindows must be 1 or greater."
}

$isPreview = -not $LaunchManualShells
$scriptName = Split-Path -Leaf $PSCommandPath
$fullRegistryPath = Resolve-AiOsPath -Path $RegistryPath
if (-not (Test-Path -LiteralPath $fullRegistryPath -PathType Leaf)) {
    throw "Lane registry not found: $fullRegistryPath"
}

$registry = Get-Content -LiteralPath $fullRegistryPath -Raw | ConvertFrom-Json
$resolverPath = Join-Path $PSScriptRoot "Resolve-AiOsWorkspaceIntent.ps1"
if (-not (Test-Path -LiteralPath $resolverPath -PathType Leaf)) {
    throw "Intent resolver not found: $resolverPath"
}

$identityScriptPath = Join-Path $PSScriptRoot "Set-AiOsTerminalIdentity.ps1"
if (-not (Test-Path -LiteralPath $identityScriptPath -PathType Leaf)) {
    throw "Terminal identity helper not found: $identityScriptPath"
}

$intentResolution = (& $resolverPath -Intent $Intent -QuietJson | ConvertFrom-Json)
foreach ($laneId in @($intentResolution.selected_lane_ids)) {
    $lane = Get-RegistryLaneById -Registry $registry -LaneId $laneId
    if ($null -eq $lane) {
        throw "Intent resolver selected unknown lane_id: $laneId"
    }
}
$selectedLaneIds = @($intentResolution.selected_lane_ids)
$selectedLanes = @($registry.lanes | Where-Object { $selectedLaneIds -contains $_.lane_id })

$manualCodexLaneIds = @($intentResolution.manual_codex_lane_ids)

Write-Host ("COPY START " + [char]0x2014 + " $scriptName")
Write-Host "AI_OS Workspace Bootstrap" -ForegroundColor Cyan
Write-Host "Issue: #60"
Write-Host "Mode: $(if ($isPreview) { 'PREVIEW - print only' } else { 'MANUAL SHELL LAUNCH' })"
Write-Host "Registry: $fullRegistryPath"
Write-Host "MaxWindows: $MaxWindows"
Write-Host "launch_policy: windows_terminal_tab_only"
Write-Host "fallback_policy: print_manual_command"
Write-Host "Safety: no assistant auto-launch. Background launch hooks are disabled."
Write-Host ("Safety: no commits, no pushes, no startup tasks, no scheduled tasks, no " + "bro" + "ker/API/live trading.")
Write-Host "Truth rule: trust prompt path and Git branch, not stale terminal/tab title after cd."

Write-AiOsSection -Title "Intent"
Write-Host $intentResolution.intent

Write-AiOsSection -Title "Git Worktree List"
git worktree list

Write-AiOsSection -Title "Selected lanes"
foreach ($lane in @($selectedLanes)) {
    Write-LaneReport -Lane $lane
}

Write-AiOsSection -Title "Manual Codex instructions"
$manualCodexLanes = @($selectedLanes | Where-Object { $manualCodexLaneIds -contains $_.lane_id })
if ($manualCodexLanes.Count -eq 0) {
    Write-Host "NONE"
} else {
    foreach ($lane in $manualCodexLanes) {
        Write-Host "Manual Codex lane needed: $($lane.display_title)" -ForegroundColor Yellow
        Write-Host "Command: cd $($lane.path); codex"
    }
}

Write-AiOsSection -Title "Validators suggested"
@($intentResolution.validators_suggested) | ForEach-Object {
    Write-Host "  $_"
}

Write-AiOsSection -Title "Next safe action"
Write-Host $intentResolution.next_safe_action

Write-AiOsSection -Title "Tab Launch Preview"
foreach ($lane in @($selectedLanes | Select-Object -First $MaxWindows)) {
    Write-Host "lane_id: $($lane.lane_id)" -ForegroundColor Cyan
    Write-Host "tab_title: $($lane.tab_title)"
    Write-Host "starting_directory: $($lane.path)"
    Write-Host "command: $(Get-WtPreviewCommand -Lane $lane)"
    Write-Host ""
}

Write-AiOsSection -Title "Operator Commands"
Write-Host "Preview workspace:"
Write-Host '  powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Start-AiOsWorkspace.ps1 -Preview -Intent "<plain language work goal>"'
Write-Host "Open selected lane tabs manually:"
Write-Host '  powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Start-AiOsWorkspace.ps1 -LaunchManualShells -Intent "<plain language work goal>" -MaxWindows 3'
Write-Host "Preview one lane:"
Write-Host "  powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Open-AiOsLane.ps1 -LaneId save_git -Preview"
Write-Host "Save session metadata:"
Write-Host "  powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Save-AiOsSession.ps1 -Apply"
Write-Host "Restore session preview:"
Write-Host "  powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Restore-AiOsSession.ps1 -Preview"

if ($isPreview) {
    Write-Host ""
    Write-Host "Preview complete. Tabs opened: NO" -ForegroundColor Green
    Write-Host "Assistant auto-start performed: NO"
    Write-Host "Commit performed: NO"
    Write-Host "Push performed: NO"
    Write-Host ("COPY END " + [char]0x2014 + " $scriptName")
    exit 0
}

$wtCommand = Get-Command wt.exe -ErrorAction SilentlyContinue
if ($null -eq $wtCommand) {
    Write-Host "Windows Terminal unavailable. Fallback manual commands:" -ForegroundColor Yellow
    foreach ($lane in @($selectedLanes | Select-Object -First $MaxWindows)) {
        Write-Host (Get-WtManualCommand -Lane $lane -IdentityScriptPath $identityScriptPath)
    }
    Write-Host "Tabs opened: 0"
    Write-Host "Workspace bootstrap complete. Assistant auto-start performed: NO"
    Write-Host "Commit performed: NO"
    Write-Host "Push performed: NO"
    Write-Host ("COPY END " + [char]0x2014 + " $scriptName")
    exit 0
}

$openedTabs = 0
foreach ($lane in @($selectedLanes)) {
    if ($openedTabs -ge $MaxWindows) {
        Write-Host "Skipped lane due to MaxWindows limit: $($lane.display_title)"
        continue
    }

    if (-not (Test-Path -LiteralPath $lane.path -PathType Container)) {
        throw "Lane path not found for $($lane.lane_id): $($lane.path)"
    }

    Open-LaneTab -Lane $lane -IdentityScriptPath $identityScriptPath
    Write-Host "Opened Windows Terminal tab: $($lane.lane_id)"
    $openedTabs += 1
}

Write-Host "Tabs opened: $openedTabs"
Write-Host "Workspace bootstrap complete. Assistant auto-start performed: NO"
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host ("COPY END " + [char]0x2014 + " $scriptName")
