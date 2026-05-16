param(
    [switch]$Preview,
    [switch]$LaunchManualShells,
    [string]$SessionPath = "automation/orchestration/terminal_workstations/AIOS_SESSION_STATE.example.json"
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
$fullSessionPath = Resolve-AiOsPath -Path $SessionPath

if (Test-Path -LiteralPath $fullSessionPath -PathType Leaf) {
    $statePath = $fullSessionPath
} else {
    throw "No session state found: $fullSessionPath"
}

$session = Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json

Write-Host "AI_OS Session Restore" -ForegroundColor Cyan
Write-Host "Mode: $(if ($isPreview) { 'PREVIEW - print only' } else { 'MANUAL SHELL LAUNCH' })"
Write-Host "State: $statePath"
Write-Host "Safety: assistant start is manual. Background launch hooks are disabled."
Write-Host "Safety: no commits, no pushes, no destructive cleanup, no external execution integration."

Write-Host ""
Write-Host "== Git Worktree List ==" -ForegroundColor Yellow
git worktree list

Write-Host ""
Write-Host "== Restorable Lanes ==" -ForegroundColor Yellow
foreach ($lane in @($session.lanes)) {
    Write-Host "ID: $($lane.id)" -ForegroundColor Cyan
    Write-Host "Name: $($lane.name)"
    Write-Host "Role: $($lane.role)"
    Write-Host "Path: $($lane.path)"
    Write-Host "Branch: $($lane.branch)"
    Write-Host "Restart command:"
    Write-Host "  $($lane.restart_command)"
    Write-Host ""
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
    exit 0
}

foreach ($lane in @($session.lanes)) {
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

Write-Host "Restore complete. Assistant auto-start performed: NO"
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
