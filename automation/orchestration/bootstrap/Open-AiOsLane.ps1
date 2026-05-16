param(
    [string]$LaneId,
    [switch]$Open,
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

$fullRegistryPath = Resolve-AiOsPath -Path $RegistryPath
if (-not (Test-Path -LiteralPath $fullRegistryPath -PathType Leaf)) {
    throw "Lane registry not found: $fullRegistryPath"
}

$registry = Get-Content -LiteralPath $fullRegistryPath -Raw | ConvertFrom-Json

Write-Host "AI_OS Lane Opener" -ForegroundColor Cyan
Write-Host "Mode: $(if ($Open) { 'OPEN - manual PowerShell shell only' } else { 'PREVIEW - no window opened' })"
Write-Host "Safety: no Codex auto-launch, no scheduled tasks, no startup tasks."
Write-Host "Safety: no broker/API/live trading, no commits, no pushes, no destructive actions."

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
    Write-Host "  powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Open-AiOsLane.ps1 -LaneId validation"
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
Write-Host "Codex allowed: $($selectedLane.codex_allowed)"
if ($selectedLane.PSObject.Properties.Name -contains "codex_launch") {
    Write-Host "Codex launch: $($selectedLane.codex_launch)"
}
Write-Host "Restart command:"
Write-Host "  $($selectedLane.restart_command)"

if (-not $Open) {
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
    $selectedLane.restart_command.Replace("powershell -NoExit -ExecutionPolicy Bypass -Command ", "")
)

Write-Host "Opened manual PowerShell lane: $($selectedLane.id)"
Write-Host "Codex auto-launch performed: NO"
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
