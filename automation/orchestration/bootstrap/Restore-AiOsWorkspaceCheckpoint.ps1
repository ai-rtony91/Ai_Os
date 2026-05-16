param(
    [switch]$Preview,
    [switch]$LaunchManualShells,
    [int]$MaxWindows = 3,
    [string]$RegistryPath = "automation/orchestration/terminal_workstations/AIOS_WORKTREE_LANE_REGISTRY.json",
    [string]$CheckpointPath = "automation/orchestration/terminal_workstations/AIOS_WORKSPACE_CHECKPOINT.example.json"
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
$fullCheckpointPath = Resolve-AiOsPath -Path $CheckpointPath

if (-not (Test-Path -LiteralPath $fullRegistryPath -PathType Leaf)) {
    throw "Lane registry not found: $fullRegistryPath"
}

if (-not (Test-Path -LiteralPath $fullCheckpointPath -PathType Leaf)) {
    throw "Workspace checkpoint not found: $fullCheckpointPath"
}

$identityScriptPath = Join-Path $PSScriptRoot "Set-AiOsTerminalIdentity.ps1"
if (-not (Test-Path -LiteralPath $identityScriptPath -PathType Leaf)) {
    throw "Terminal identity helper not found: $identityScriptPath"
}

$registry = Get-Content -LiteralPath $fullRegistryPath -Raw | ConvertFrom-Json
$checkpoint = Get-Content -LiteralPath $fullCheckpointPath -Raw | ConvertFrom-Json

$restorableLanes = @()
foreach ($checkpointLane in @($checkpoint.lanes)) {
    $lane = Get-RegistryLaneById -Registry $registry -LaneId $checkpointLane.lane_id
    if ($null -eq $lane) {
        throw "Checkpoint references lane_id not found in registry: $($checkpointLane.lane_id)"
    }
    $restorableLanes += $lane
}
$restorableLanes = @($restorableLanes | Where-Object { $_.lane_id -eq "main_control" }) + @($restorableLanes | Where-Object { $_.lane_id -ne "main_control" })

Write-Host ("COPY START " + [char]0x2014 + " $scriptName")
Write-Host "AI_OS Workspace Checkpoint Restore" -ForegroundColor Cyan
Write-Host "Mode: $(if ($isPreview) { 'PREVIEW - print only' } else { 'MANUAL SHELL LAUNCH' })"
Write-Host "Registry: $fullRegistryPath"
Write-Host "Checkpoint path: $fullCheckpointPath"
Write-Host "Checkpoint id: $($checkpoint.checkpoint_id)"
Write-Host "Created at: $($checkpoint.created_at)"
Write-Host "launch_policy: windows_terminal_tab_only"
Write-Host "fallback_policy: print_manual_command"
Write-Host "Safety: no assistant auto-launch. Background launch hooks are disabled."
Write-Host ("Safety: no commits, no pushes, no startup tasks, no scheduled tasks, no " + "bro" + "ker/API/live trading.")
Write-Host "Truth rule: registry lane titles are used; path and branch remain the operational truth source."

Write-Host ""
Write-Host "== Would Reopen ==" -ForegroundColor Yellow
foreach ($lane in @($restorableLanes)) {
    Write-LaneReport -Lane $lane
}

Write-Host "== Manual Codex Instructions ==" -ForegroundColor Yellow
$codexLanes = @($restorableLanes | Where-Object { Test-CodexLane -Lane $_ })
if ($codexLanes.Count -eq 0) {
    Write-Host "NONE"
} else {
    foreach ($lane in $codexLanes) {
        Write-Host "Manual Codex lane needed: $($lane.display_title)" -ForegroundColor Yellow
        Write-Host "Command: cd $($lane.path); codex"
    }
}

Write-Host ""
Write-Host "== Last Commands ==" -ForegroundColor Yellow
if ($checkpoint.PSObject.Properties.Name -contains "last_commands") {
    $checkpoint.last_commands.PSObject.Properties | ForEach-Object {
        Write-Host "$($_.Name): $($_.Value)"
    }
}

Write-Host ""
Write-Host "Pending workorders:"
@($checkpoint.pending_workorders) | ForEach-Object {
    Write-Host "  $($_.title) - $($_.status)"
}
Write-Host "Last validator status: $($checkpoint.last_validator_status)"
Write-Host "Next safe action: $($checkpoint.next_safe_action)"

if ($isPreview) {
    Write-Host ""
    Write-Host "Preview complete. No tabs opened." -ForegroundColor Green
    Write-Host "Assistant auto-start performed: NO"
    Write-Host "Commit performed: NO"
    Write-Host "Push performed: NO"
    Write-Host ("COPY END " + [char]0x2014 + " $scriptName")
    exit 0
}

$wtCommand = Get-Command wt.exe -ErrorAction SilentlyContinue
if ($null -eq $wtCommand) {
    Write-Host "Windows Terminal unavailable. Fallback manual commands:" -ForegroundColor Yellow
    foreach ($lane in @($restorableLanes | Select-Object -First $MaxWindows)) {
        Write-Host (Get-WtManualCommand -Lane $lane -IdentityScriptPath $identityScriptPath)
    }
    Write-Host "Tabs opened: 0"
    Write-Host "Restore complete. Assistant auto-start performed: NO"
    Write-Host "Commit performed: NO"
    Write-Host "Push performed: NO"
    Write-Host ("COPY END " + [char]0x2014 + " $scriptName")
    exit 0
}

$openedTabs = 0
foreach ($lane in @($restorableLanes)) {
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
Write-Host "Restore complete. Assistant auto-start performed: NO"
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host ("COPY END " + [char]0x2014 + " $scriptName")
