param(
    [switch]$LaunchManualShells,
    [string]$RegistryPath = "automation/orchestration/terminal_workstations/AIOS_WORKTREE_LANE_REGISTRY.json"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Resolve-AiOsPath {
    param([string]$Path)

    if ([System.IO.Path]::IsPathRooted($Path)) {
        return $Path
    }

    return Join-Path (Get-Location).Path $Path
}

function Write-Section {
    param([string]$Title)

    Write-Host ""
    Write-Host "== $Title ==" -ForegroundColor Yellow
}

$fullRegistryPath = Resolve-AiOsPath -Path $RegistryPath
if (-not (Test-Path -LiteralPath $fullRegistryPath -PathType Leaf)) {
    throw "Lane registry not found: $RegistryPath"
}

$registry = Get-Content -LiteralPath $fullRegistryPath -Raw | ConvertFrom-Json

Write-Host "AI_OS Worktree Lane Registry" -ForegroundColor Cyan
Write-Host "Mode: default print-only"
Write-Host "Registry: $fullRegistryPath"
Write-Host "No Codex auto-launch. No startup tasks. No scheduled tasks. No automatic extra windows."
Write-Host "No commits. No pushes. No broker/OANDA/API/webhook/live trading."

Write-Section -Title "Git Worktree List"
git worktree list

Write-Section -Title "Registered Lanes"
foreach ($lane in @($registry.lanes)) {
    Write-Host "ID: $($lane.id)" -ForegroundColor Cyan
    Write-Host "Name: $($lane.name)"
    Write-Host "Role: $($lane.role)"
    Write-Host "Path: $($lane.path)"
    Write-Host "Branch: $($lane.branch)"
    Write-Host "Codex allowed: $($lane.codex_allowed)"
    if ($lane.PSObject.Properties.Name -contains "codex_launch") {
        Write-Host "Codex launch: $($lane.codex_launch)"
    }
    Write-Host "Restart command:"
    Write-Host "  $($lane.restart_command)"
    Write-Host ""
}

if (-not $LaunchManualShells) {
    Write-Host "LaunchManualShells: OFF. No windows opened." -ForegroundColor Green
    Write-Host "Commit performed: NO"
    Write-Host "Push performed: NO"
    exit 0
}

Write-Section -Title "Manual Shell Launch"
foreach ($lane in @($registry.lanes)) {
    if (-not (Test-Path -LiteralPath $lane.path -PathType Container)) {
        throw "Lane path not found for $($lane.id): $($lane.path)"
    }

    Start-Process powershell.exe -ArgumentList @(
        "-NoExit",
        "-ExecutionPolicy",
        "Bypass",
        "-Command",
        "Set-Location -LiteralPath '$($lane.path)'; `$Host.UI.RawUI.WindowTitle = '$($lane.name)'; git status --short --branch"
    )
    Write-Host "Opened manual PowerShell shell for $($lane.id)"
}

Write-Host "Codex auto-launch performed: NO"
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
