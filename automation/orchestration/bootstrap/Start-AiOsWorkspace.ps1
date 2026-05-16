param(
    [switch]$Preview,
    [switch]$LaunchManualShells,
    [string]$RegistryPath = "automation/orchestration/terminal_workstations/AIOS_WORKTREE_LANE_REGISTRY.json"
)

Set-StrictMode -Version Latest
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

function Get-RestartPayload {
    param([Parameter(Mandatory = $true)][string]$Command)

    $prefix = "powershell -NoExit -ExecutionPolicy Bypass -Command "
    if ($Command.StartsWith($prefix)) {
        return $Command.Substring($prefix.Length)
    }

    return $Command
}

if ($Preview -and $LaunchManualShells) {
    throw "Use either -Preview or -LaunchManualShells, not both."
}

$isPreview = -not $LaunchManualShells
$fullRegistryPath = Resolve-AiOsPath -Path $RegistryPath
if (-not (Test-Path -LiteralPath $fullRegistryPath -PathType Leaf)) {
    throw "Lane registry not found: $fullRegistryPath"
}

$registry = Get-Content -LiteralPath $fullRegistryPath -Raw | ConvertFrom-Json

Write-Host "AI_OS Workspace Bootstrap" -ForegroundColor Cyan
Write-Host "Issue: #60"
Write-Host "Mode: $(if ($isPreview) { 'PREVIEW - print only' } else { 'MANUAL SHELL LAUNCH' })"
Write-Host "Registry: $fullRegistryPath"
Write-Host "Safety: assistant start is manual. Background launch hooks are disabled."
Write-Host "Safety: no commits, no pushes, no destructive cleanup, no external execution integration."

Write-AiOsSection -Title "Git Worktree List"
git worktree list

Write-AiOsSection -Title "Lane Registry"
foreach ($lane in @($registry.lanes)) {
    Write-Host "ID: $($lane.id)" -ForegroundColor Cyan
    Write-Host "Name: $($lane.name)"
    Write-Host "Role: $($lane.role)"
    Write-Host "Path: $($lane.path)"
    Write-Host "Branch: $($lane.branch)"
    Write-Host "Codex policy: $($lane.codex_policy)"
    Write-Host "Launch policy: $($lane.launch_policy)"
    Write-Host "Allowed actions: $(@($lane.allowed_actions) -join '; ')"
    Write-Host "Blocked actions: $(@($lane.blocked_actions) -join '; ')"
    Write-Host "Restart command:"
    Write-Host "  $($lane.restart_command)"
    Write-Host ""
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
    exit 0
}

foreach ($lane in @($registry.lanes)) {
    if (-not (Test-Path -LiteralPath $lane.path -PathType Container)) {
        throw "Lane path not found for $($lane.id): $($lane.path)"
    }

    Start-Process powershell.exe -ArgumentList @(
        "-NoExit",
        "-ExecutionPolicy",
        "Bypass",
        "-Command",
        (Get-RestartPayload -Command $lane.restart_command)
    )
    Write-Host "Opened manual PowerShell lane: $($lane.id)"
}

Write-Host "Workspace bootstrap complete. Assistant auto-start performed: NO"
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
