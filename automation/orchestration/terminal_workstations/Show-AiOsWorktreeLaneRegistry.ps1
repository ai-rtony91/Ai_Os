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
    param([string]$Title, [System.ConsoleColor]$Color = "Yellow")

    Write-Host ""
    Write-Host "  ── $Title ──" -ForegroundColor $Color
    Write-Host ""
}

$fullRegistryPath = Resolve-AiOsPath -Path $RegistryPath
if (-not (Test-Path -LiteralPath $fullRegistryPath -PathType Leaf)) {
    throw "Lane registry not found: $RegistryPath"
}

$registry = Get-Content -LiteralPath $fullRegistryPath -Raw | ConvertFrom-Json

$border = "#" * 100
$titleIcon = [char]::ConvertFromUtf32(0x1F5FA)  # World map - lane topology overview

Write-Host $border -ForegroundColor Yellow
Write-Host ""
Write-Host "  $titleIcon  AI_OS WORKTREE LANE REGISTRY" -ForegroundColor Yellow
Write-Host "  LOOK FOR THIS COLOR TO IDENTIFY THIS WINDOW." -ForegroundColor Yellow
Write-Host ""
Write-Host "  AIOS BASE : #05070b  TEXT #e5f6ff  WARNING #ffd166  ACTION #38bdf8" -ForegroundColor DarkYellow
Write-Host "  OCC LANE  : ALL LANES  |  Lane topology and worktree registry" -ForegroundColor Yellow
Write-Host "  MODE      : [ PRINT-ONLY ]  Default print-only — no windows opened" -ForegroundColor DarkYellow
Write-Host "  STATUS    : [ READ-ONLY ]  No Codex launch, no startup/scheduled tasks" -ForegroundColor DarkYellow
Write-Host "  Registry  : $fullRegistryPath" -ForegroundColor DarkYellow
Write-Host ""
Write-Host $border -ForegroundColor Yellow
Write-Host "  No Codex auto-launch. No startup tasks. No scheduled tasks. No automatic extra windows."
Write-Host "  No commits. No pushes. No broker/OANDA/API/webhook/live trading."

Write-Section -Title "Git Worktree List" -Color Cyan
git worktree list

Write-Section -Title "Registered Lanes" -Color Yellow
foreach ($lane in @($registry.lanes)) {
    Write-Host "  lane_id       : $($lane.lane_id)" -ForegroundColor Cyan
    Write-Host "  display_title : $($lane.display_title)"
    Write-Host "  window_title  : $($lane.window_title)"
    Write-Host "  tab_title     : $($lane.tab_title)"
    Write-Host "  emoji_marker  : $($lane.emoji_marker)"
    Write-Host "  truth_source  : $($lane.truth_source)"
    Write-Host "  role          : $($lane.role)"
    Write-Host "  path          : $($lane.path)"
    Write-Host "  branch        : $($lane.branch)"
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
        throw "Lane path not found for $($lane.lane_id): $($lane.path)"
    }

    Start-Process powershell.exe -ArgumentList @(
        "-NoExit",
        "-ExecutionPolicy",
        "Bypass",
        "-Command",
        "Set-Location -LiteralPath '$($lane.path)'; `$Host.UI.RawUI.WindowTitle = '$($lane.window_title)'; Write-Host 'lane_id: $($lane.lane_id)'; Write-Host 'display_title: $($lane.display_title)'; Write-Host 'window_title: $($lane.window_title)'; Write-Host 'tab_title: $($lane.tab_title)'; Write-Host 'emoji_marker: $($lane.emoji_marker)'; Write-Host 'truth_source: $($lane.truth_source)'; Write-Host 'path: $($lane.path)'; Write-Host 'branch: $($lane.branch)'; git status --short --branch"
    )
    Write-Host "Opened manual PowerShell shell for $($lane.lane_id)"
}

Write-Host "Codex auto-launch performed: NO"
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
