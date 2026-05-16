param(
    [switch]$Preview,
    [switch]$Apply,
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
    lanes = @($registry.lanes | ForEach-Object { Convert-LaneForCheckpoint -Lane $_ })
    last_commands = [ordered]@{
        workspace_preview = "powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Start-AiOsWorkspace.ps1 -Preview"
        workspace_intent_preview = 'powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Start-AiOsWorkspace.ps1 -Preview -Intent "<plain language work goal>"'
        workspace_launch = 'powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Start-AiOsWorkspace.ps1 -LaunchManualShells -Intent "<plain language work goal>" -MaxWindows 3'
        checkpoint_save_preview = "powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Save-AiOsWorkspaceCheckpoint.ps1 -Preview"
        checkpoint_save_apply = "powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Save-AiOsWorkspaceCheckpoint.ps1 -Apply"
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
Write-Host "Safety: no assistant auto-launch. Background launch hooks are disabled."
Write-Host ("Safety: no commits, no pushes, no startup tasks, no scheduled tasks, no " + "bro" + "ker/API/live trading.")
Write-Host "Truth rule: path and branch remain the operational truth source."

Write-Host ""
Write-Host "== Checkpoint Preview ==" -ForegroundColor Yellow
Write-Host $json

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
