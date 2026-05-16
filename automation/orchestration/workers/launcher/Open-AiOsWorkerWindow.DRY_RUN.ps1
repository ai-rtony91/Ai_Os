param(
    [Parameter(Mandatory = $true)][string]$WorkerId,
    [switch]$Apply
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

$registryPath = "automation/orchestration/workers/AIOS_WORKER_REGISTRY.json"

if (-not (Test-Path $registryPath)) {
    throw "Worker registry missing: $registryPath"
}

$registry = Get-Content -Raw $registryPath | ConvertFrom-Json
$worker = @($registry.workers | Where-Object { $_.worker_id -eq $WorkerId }) | Select-Object -First 1

if ($null -eq $worker) {
    throw "Worker not found: $WorkerId"
}

$title = "AIOS | $WorkerId"
$repoPath = (Get-Location).Path
$workerScript = "automation/orchestration/workers/inbox/Get-AiOsWorkerInbox.DRY_RUN.ps1"

$workerCommand = @"
Set-Location -LiteralPath '$repoPath'
Clear-Host
Write-Host '========================================' -ForegroundColor Cyan
Write-Host 'AIOS WORKER ONLINE' -ForegroundColor Green
Write-Host '========================================' -ForegroundColor Cyan
Write-Host 'Worker ID : $WorkerId' -ForegroundColor Yellow
Write-Host 'Type      : $($worker.type)' -ForegroundColor Yellow
Write-Host 'Purpose   : $($worker.purpose)' -ForegroundColor White
Write-Host 'Repo      : $repoPath' -ForegroundColor DarkGray
Write-Host '========================================' -ForegroundColor Cyan
Write-Host ''
powershell -ExecutionPolicy Bypass -File '$workerScript' -WorkerId '$WorkerId'
Write-Host ''
Write-Host 'WORKER READY FOR NEXT TASK' -ForegroundColor Green
"@

Write-Host "COPY START - Open-AiOsWorkerWindow.DRY_RUN.ps1"
Write-Host "AI_OS Worker Window Launcher" -ForegroundColor Cyan
Write-Host "Mode: $(if ($Apply) { 'APPLY' } else { 'DRY_RUN' })"
Write-Host "worker_id: $WorkerId"
Write-Host "worker_type: $($worker.type)"
Write-Host "title: $title"
Write-Host ""
Write-Host "Would open a clean worker terminal tab."
Write-Host "Command preview:"
Write-Host $workerCommand

if ($Apply) {
    $encodedCommand = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($workerCommand))
    wt new-tab --title $title powershell -NoExit -EncodedCommand $encodedCommand
    Write-Host "Worker window opened: YES"
} else {
    Write-Host "Worker window opened: NO"
}

Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host "COPY END - Open-AiOsWorkerWindow.DRY_RUN.ps1"
