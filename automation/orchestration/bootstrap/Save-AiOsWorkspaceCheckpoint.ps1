param(
    [switch]$Preview,
    [switch]$Apply,
    [string]$Intent = "",
    [string[]]$LaneId = @(),
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

function Convert-LaneForCheckpoint {
    param([Parameter(Mandatory = $true)]$Lane)

    [ordered]@{
        lane_id = $Lane.lane_id
        display_title = $Lane.display_title
        window_title = $Lane.window_title
        tab_title = $Lane.tab_title
        emoji_marker = $Lane.emoji_marker
        role = $Lane.role
        path = $Lane.path
        branch = $Lane.branch
        truth_source = $Lane.truth_source
    }
}

function Get-RegistryLaneById {
    param(
        [Parameter(Mandatory = $true)]$Registry,
        [Parameter(Mandatory = $true)][string]$LaneId
    )

    return @($Registry.lanes) | Where-Object { $_.lane_id -eq $LaneId } | Select-Object -First 1
}

function Get-LaneKind {
    param([Parameter(Mandatory = $true)]$Lane)

    return ([string]$Lane.display_title).Split([char]0x00b7)[0].Trim()
}

function Write-OperatorInstructionBlock {
    param(
        [Parameter(Mandatory = $true)]$Lane,
        [Parameter(Mandatory = $true)][string]$ExactNextCommand
    )

    Write-Host ""
    Write-Host "== WHERE TO RUN NEXT ==" -ForegroundColor Yellow
    Write-Host "Visible tab/window: $($Lane.tab_title)"
    if ($ExactNextCommand -match "\bgit\s+(add|commit|push)\b" -or $Lane.lane_id -eq "save_git") {
        Write-Host "Related Codex worker: Use Git/PowerShell tab tied to $($Lane.display_title)"
    } else {
        Write-Host "Related Codex worker: $($Lane.display_title)"
    }
    Write-Host "Required path: $($Lane.path)"
    Write-Host "Required branch: $($Lane.branch)"
    Write-Host "Role: $(Get-LaneKind -Lane $Lane) - $($Lane.role)"
    Write-Host "Exact next command: $ExactNextCommand"
}

if ($Preview -and $Apply) {
    throw "Use either -Preview or -Apply, not both."
}

$scriptName = Split-Path -Leaf $PSCommandPath
$fullRegistryPath = Resolve-AiOsPath -Path $RegistryPath
$fullCheckpointPath = Resolve-AiOsPath -Path $CheckpointPath

if (-not (Test-Path -LiteralPath $fullRegistryPath -PathType Leaf)) {
    throw "Lane registry not found: $fullRegistryPath"
}

$registry = Get-Content -LiteralPath $fullRegistryPath -Raw | ConvertFrom-Json
$resolverPath = Join-Path $PSScriptRoot "Resolve-AiOsWorkspaceIntent.ps1"
if (-not (Test-Path -LiteralPath $resolverPath -PathType Leaf)) {
    throw "Intent resolver not found: $resolverPath"
}

if (@($LaneId).Count -gt 0) {
    $selectedLaneIds = @($LaneId)
    if ($selectedLaneIds -notcontains "main_control") {
        $selectedLaneIds = @("main_control") + $selectedLaneIds
    }
    $intentLabel = "explicit lane selection"
} else {
    $intentResolution = (& $resolverPath -Intent $Intent -QuietJson | ConvertFrom-Json)
    $selectedLaneIds = @($intentResolution.selected_lane_ids)
    $intentLabel = $intentResolution.intent
}

foreach ($selectedLaneId in @($selectedLaneIds)) {
    $lane = Get-RegistryLaneById -Registry $registry -LaneId $selectedLaneId
    if ($null -eq $lane) {
        throw "Selected lane_id not found in registry: $selectedLaneId"
    }
}

$selectedLanes = @($registry.lanes | Where-Object { $selectedLaneIds -contains $_.lane_id })
if (@($selectedLanes).Count -lt 1 -or @($selectedLanes)[0].lane_id -ne "main_control") {
    throw "Checkpoint lane selection must include CONTROL first."
}

$timestamp = (Get-Date).ToString("o")
$activeBranch = git branch --show-current

$checkpoint = [ordered]@{
    checkpoint_id = "AIOS_WORKSPACE_CHECKPOINT"
    created_at = $timestamp
    active_workspace = Split-Path -Leaf (Get-Location).Path
    active_worktree = (Get-Location).Path
    active_branch = $activeBranch
    launch_policy = "windows_terminal_tab_only"
    fallback_policy = "print_manual_command"
    lanes = @($selectedLanes | ForEach-Object { Convert-LaneForCheckpoint -Lane $_ })
    last_commands = [ordered]@{
        workspace_preview = "powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Start-AiOsWorkspace.ps1 -Preview"
        workspace_intent_preview = 'powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Start-AiOsWorkspace.ps1 -Preview -Intent "<plain language work goal>"'
        workspace_launch = 'powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Start-AiOsWorkspace.ps1 -LaunchManualShells -Intent "<plain language work goal>" -MaxWindows 3'
        checkpoint_save_preview = 'powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Save-AiOsWorkspaceCheckpoint.ps1 -Preview -Intent "<plain language work goal>"'
        checkpoint_save_apply = 'powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Save-AiOsWorkspaceCheckpoint.ps1 -Apply -Intent "<plain language work goal>"'
        checkpoint_restore_preview = "powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Restore-AiOsWorkspaceCheckpoint.ps1 -Preview"
        validator = "powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Test-AiOsWorkspaceBootstrap.DRY_RUN.ps1"
    }
    pending_workorders = @(
        [ordered]@{
            title = "Workspace cementing and sticky lane checkpoint"
            status = "in_progress"
        }
    )
    last_validator_status = "UNKNOWN"
    next_safe_action = "powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Test-AiOsWorkspaceBootstrap.DRY_RUN.ps1"
}

$json = $checkpoint | ConvertTo-Json -Depth 8

Write-Host ("COPY START " + [char]0x2014 + " $scriptName")
Write-Host "AI_OS Workspace Checkpoint Save" -ForegroundColor Cyan
Write-Host "Mode: $(if ($Apply) { 'APPLY - write checkpoint' } else { 'PREVIEW - no file written' })"
Write-Host "Registry: $fullRegistryPath"
Write-Host "Checkpoint path: $fullCheckpointPath"
Write-Host "Intent: $intentLabel"
Write-Host "Safety: no assistant auto-launch. Background launch hooks are disabled."
Write-Host ("Safety: no commits, no pushes, no startup tasks, no scheduled tasks, no " + "bro" + "ker/API/live trading.")
Write-Host "Truth rule: path and branch remain the operational truth source."

Write-Host ""
Write-Host "== Selected Lanes ==" -ForegroundColor Yellow
foreach ($lane in @($selectedLanes)) {
    Write-Host "lane_id: $($lane.lane_id)" -ForegroundColor Cyan
    Write-Host "display_title: $($lane.display_title)"
    Write-Host "tab_title: $($lane.tab_title)"
    Write-Host "path: $($lane.path)"
    Write-Host "branch: $($lane.branch)"
    Write-Host ""
}

Write-Host ""
Write-Host "== Checkpoint Preview ==" -ForegroundColor Yellow
Write-Host $json

$instructionLane = @($selectedLanes | Where-Object { $_.lane_id -eq "save_git" } | Select-Object -First 1)
if ($instructionLane.Count -eq 0) {
    $instructionLane = @($selectedLanes | Select-Object -First 1)
}

$saveSelection = if (@($LaneId).Count -gt 0) {
    "-LaneId $($selectedLaneIds -join ',')"
} elseif ([string]::IsNullOrWhiteSpace($Intent)) {
    ""
} else {
    "-Intent `"$Intent`""
}
$exactNextCommand = if ($Apply) {
    "powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Restore-AiOsWorkspaceCheckpoint.ps1 -Preview"
} else {
    ("powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Save-AiOsWorkspaceCheckpoint.ps1 -Apply $saveSelection").Trim()
}
Write-OperatorInstructionBlock -Lane $instructionLane[0] -ExactNextCommand $exactNextCommand

if (-not $Apply) {
    Write-Host ""
    Write-Host "Preview complete. No checkpoint file written." -ForegroundColor Green
    Write-Host "Commit performed: NO"
    Write-Host "Push performed: NO"
    Write-Host ("COPY END " + [char]0x2014 + " $scriptName")
    exit 0
}

$checkpointDirectory = Split-Path -Parent $fullCheckpointPath
if (-not (Test-Path -LiteralPath $checkpointDirectory -PathType Container)) {
    New-Item -ItemType Directory -Path $checkpointDirectory | Out-Null
}

Set-Content -LiteralPath $fullCheckpointPath -Value $json -Encoding UTF8
Write-Host ""
Write-Host "Checkpoint saved: $fullCheckpointPath" -ForegroundColor Green
Write-Host "Assistant auto-start performed: NO"
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host ("COPY END " + [char]0x2014 + " $scriptName")
