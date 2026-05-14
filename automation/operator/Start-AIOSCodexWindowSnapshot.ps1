[CmdletBinding()]
param(
    [string]$SnapshotPath = "automation/operator/window_snapshots/AIOS_10_WORKER_MORNING_SNAPSHOT.example.json",
    [switch]$Launch
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath ".git")) {
    throw "Run this script from the repository root."
}

if (-not (Test-Path -LiteralPath $SnapshotPath)) {
    throw "Snapshot file not found: $SnapshotPath"
}

$RepoRoot = (Resolve-Path -LiteralPath ".").Path
$Snapshot = Get-Content -LiteralPath $SnapshotPath -Raw | ConvertFrom-Json

Write-Host "AI_OS CODEX WINDOW SNAPSHOT" -ForegroundColor Cyan
Write-Host "Repo: $RepoRoot" -ForegroundColor Cyan
Write-Host "Snapshot: $SnapshotPath" -ForegroundColor Cyan
Write-Host ""

Write-Host "Git status before launch:" -ForegroundColor Yellow
& git status --short --branch
Write-Host ""

Write-Host "Worker window plan:" -ForegroundColor Yellow
foreach ($Worker in $Snapshot.workers) {
    $Title = "$($Worker.worker_id) $($Worker.worker_label)"
    Write-Host (" - {0}" -f $Title)
    Write-Host ("   Next safe action: {0}" -f $Worker.next_safe_action)
}

Write-Host ""
if (-not $Launch) {
    Write-Host "Preview only. No windows launched." -ForegroundColor Yellow
    Write-Host "To launch manually, rerun with -Launch after reviewing git status." -ForegroundColor Yellow
    exit 0
}

Write-Host "Launching worker windows..." -ForegroundColor Cyan
foreach ($Worker in $Snapshot.workers) {
    $Title = "$($Worker.worker_id) $($Worker.worker_label)"
    $Command = "Write-Host '$Title' -ForegroundColor Cyan; Set-Location '$RepoRoot'; codex --cd '$RepoRoot'"
    Start-Process powershell -ArgumentList @(
        "-NoExit",
        "-Command",
        $Command
    )
    Start-Sleep -Milliseconds 500
}

Write-Host "Launch requested. No APPLY, stage, commit, or push was performed." -ForegroundColor Green

