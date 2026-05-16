param(
    [switch]$OpenLanes,
    [string]$SessionPath = "automation/orchestration/terminal_workstations/AIOS_SESSION_STATE.json",
    [string]$FallbackExamplePath = "automation/orchestration/terminal_workstations/AIOS_SESSION_STATE.example.json"
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

$fullSessionPath = Resolve-AiOsPath -Path $SessionPath
$fullFallbackExamplePath = Resolve-AiOsPath -Path $FallbackExamplePath

if (Test-Path -LiteralPath $fullSessionPath -PathType Leaf) {
    $statePath = $fullSessionPath
} elseif (Test-Path -LiteralPath $fullFallbackExamplePath -PathType Leaf) {
    $statePath = $fullFallbackExamplePath
} else {
    throw "No session state found. Checked: $fullSessionPath and $fullFallbackExamplePath"
}

$session = Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json

Write-Host "AI_OS Session Restore" -ForegroundColor Cyan
Write-Host "Mode: $(if ($OpenLanes) { 'OPEN LANES - manual PowerShell shells only' } else { 'PREVIEW - no windows opened' })"
Write-Host "State: $statePath"
Write-Host "Safety: no Codex auto-launch, no scheduled tasks, no startup tasks."
Write-Host "Safety: no broker/API/live trading, no commits, no pushes, no destructive actions."

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

if (-not $OpenLanes) {
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
        $lane.restart_command.Replace("powershell -NoExit -ExecutionPolicy Bypass -Command ", "")
    )
    Write-Host "Opened manual PowerShell lane: $($lane.id)"
}

Write-Host "Restore complete. Codex auto-launch performed: NO"
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
