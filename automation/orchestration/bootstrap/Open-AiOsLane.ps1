param(
    [string]$LaneId,
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

Write-Host "AI_OS Lane Opener" -ForegroundColor Cyan
Write-Host "Mode: $(if ($isPreview) { 'PREVIEW - print only' } else { 'MANUAL SHELL LAUNCH' })"
Write-Host "Safety: assistant start is manual. Background launch hooks are disabled."
Write-Host "Safety: no commits, no pushes, no destructive cleanup, no external execution integration."

Write-Host ""
Write-Host "== Git Worktree List ==" -ForegroundColor Yellow
git worktree list

if ([string]::IsNullOrWhiteSpace($LaneId)) {
    Write-Host ""
    Write-Host "Available lanes:" -ForegroundColor Yellow
    foreach ($lane in @($registry.lanes)) {
        Write-Host "  $($lane.id) - $($lane.name) - $($lane.branch)"
    }
    Write-Host ""
    Write-Host "Preview one lane:"
    Write-Host "  powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Open-AiOsLane.ps1 -LaneId validation -Preview"
    exit 0
}

$selectedLane = @($registry.lanes) | Where-Object { $_.id -eq $LaneId } | Select-Object -First 1
if ($null -eq $selectedLane) {
    throw "Unknown lane id: $LaneId"
}

Write-Host ""
Write-Host "== Selected Lane ==" -ForegroundColor Yellow
Write-Host "ID: $($selectedLane.id)" -ForegroundColor Cyan
Write-Host "Name: $($selectedLane.name)"
Write-Host "Role: $($selectedLane.role)"
Write-Host "Path: $($selectedLane.path)"
Write-Host "Branch: $($selectedLane.branch)"
Write-Host "Codex policy: $($selectedLane.codex_policy)"
Write-Host "Launch policy: $($selectedLane.launch_policy)"
Write-Host "Allowed actions: $(@($selectedLane.allowed_actions) -join '; ')"
Write-Host "Blocked actions: $(@($selectedLane.blocked_actions) -join '; ')"
Write-Host "Restart command:"
Write-Host "  $($selectedLane.restart_command)"

if ($isPreview) {
    Write-Host ""
    Write-Host "Preview complete. No window opened." -ForegroundColor Green
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
    (Get-RestartPayload -Command $selectedLane.restart_command)
)

Write-Host "Opened manual PowerShell lane: $($selectedLane.id)"
Write-Host "Assistant auto-start performed: NO"
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
