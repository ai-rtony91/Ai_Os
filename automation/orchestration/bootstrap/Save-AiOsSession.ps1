param(
    [switch]$Preview,
    [switch]$Apply,
    [string]$RegistryPath = "automation/orchestration/terminal_workstations/AIOS_WORKTREE_LANE_REGISTRY.json",
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

function Convert-LaneForSession {
    param([Parameter(Mandatory = $true)]$Lane)

    [ordered]@{
        lane_id = $Lane.lane_id
        display_title = $Lane.display_title
        window_title = $Lane.window_title
        tab_title = $Lane.tab_title
        path = $Lane.path
        branch = $Lane.branch
        role = $Lane.role
        emoji_marker = $Lane.emoji_marker
        truth_source = $Lane.truth_source
    }
}

$fullRegistryPath = Resolve-AiOsPath -Path $RegistryPath
$fullSessionPath = Resolve-AiOsPath -Path $SessionPath
$scriptName = Split-Path -Leaf $PSCommandPath

if ($Preview -and $Apply) {
    throw "Use either -Preview or -Apply, not both."
}

if (-not (Test-Path -LiteralPath $fullRegistryPath -PathType Leaf)) {
    throw "Lane registry not found: $fullRegistryPath"
}

$registry = Get-Content -LiteralPath $fullRegistryPath -Raw | ConvertFrom-Json
$timestamp = (Get-Date).ToString("o")

$session = [ordered]@{
    session_id = "AIOS_SESSION_STATE"
    version = "2.0"
    saved_at = $timestamp
    mode = "manual_restore_only"
    source_registry = $RegistryPath
    active_workspace = "aios-worker-bootstrap"
    active_worktree = (Get-Location).Path
    active_branch = (git branch --show-current)
    truth_rule = "Trust prompt path and Git branch, not stale terminal/tab title after cd."
    open_lanes = @("bootstrap_git", "bootstrap_codex")
    last_known_roles = @($registry.lanes | ForEach-Object { Convert-LaneForSession -Lane $_ })
    last_commands = [ordered]@{
        workspace_preview = "powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Start-AiOsWorkspace.ps1 -Preview"
        workspace_launch = "powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Start-AiOsWorkspace.ps1 -LaunchManualShells"
        lane_preview = "powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Open-AiOsLane.ps1 -LaneId bootstrap_git -Preview"
        save_session = "powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Save-AiOsSession.ps1 -Apply"
        restore_preview = "powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Restore-AiOsSession.ps1 -Preview"
        validator = "powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Test-AiOsWorkspaceBootstrap.DRY_RUN.ps1"
    }
    pending_workorders = @(
        [ordered]@{
            issue = 60
            title = "AI_OS workspace bootstrap and lane recovery"
            status = "in_progress"
        }
    )
    last_validator_status = "UNKNOWN"
    next_safe_action = "powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Test-AiOsWorkspaceBootstrap.DRY_RUN.ps1"
    lanes = @($registry.lanes | ForEach-Object { Convert-LaneForSession -Lane $_ })
}

$json = $session | ConvertTo-Json -Depth 8

Write-Host ("COPY START " + [char]0x2014 + " $scriptName")
Write-Host "AI_OS Session Save" -ForegroundColor Cyan
Write-Host "Mode: $(if ($Apply) { 'APPLY - write session state' } else { 'PREVIEW - no file written' })"
Write-Host "Session path: $fullSessionPath"
Write-Host "Safety: no assistant auto-launch. Background launch hooks are disabled."
Write-Host ("Safety: no commits, no pushes, no startup tasks, no scheduled tasks, no " + "bro" + "ker/API/live trading.")
Write-Host "Truth rule: trust prompt path and Git branch, not stale terminal/tab title after cd."

Write-Host ""
Write-Host "== Git Worktree List ==" -ForegroundColor Yellow
git worktree list

Write-Host ""
Write-Host "== Session Preview ==" -ForegroundColor Yellow
Write-Host $json

if (-not $Apply) {
    Write-Host ""
    Write-Host "Preview complete. No session file written." -ForegroundColor Green
    Write-Host ("COPY END " + [char]0x2014 + " $scriptName")
    exit 0
}

$sessionDirectory = Split-Path -Parent $fullSessionPath
if (-not (Test-Path -LiteralPath $sessionDirectory -PathType Container)) {
    New-Item -ItemType Directory -Path $sessionDirectory | Out-Null
}

Set-Content -LiteralPath $fullSessionPath -Value $json -Encoding UTF8
Write-Host "Session saved: $fullSessionPath" -ForegroundColor Green
Write-Host "Assistant auto-start performed: NO"
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host ("COPY END " + [char]0x2014 + " $scriptName")
