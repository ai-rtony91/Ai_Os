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

$title = "AIOS WORKER - $WorkerId"
$repoPath = (Get-Location).Path

$workerCommand = "cd `"$repoPath`"; Write-Host 'AIOS WORKER READY: $WorkerId'; Write-Host 'Type: $($worker.type)'; Write-Host 'Purpose: $($worker.purpose)'; powershell -ExecutionPolicy Bypass -File automation/orchestration/workers/inbox/Get-AiOsWorkerInbox.DRY_RUN.ps1 -WorkerId $WorkerId"

Write-Host "COPY START - Open-AiOsWorkerWindow.DRY_RUN.ps1"
Write-Host "AI_OS Worker Window Launcher" -ForegroundColor Cyan
Write-Host "Mode: $(if ($Apply) { 'APPLY' } else { 'DRY_RUN' })"
Write-Host "worker_id: $WorkerId"
Write-Host "worker_type: $($worker.type)"
Write-Host "title: $title"
Write-Host ""
Write-Host "Would open a worker terminal window."
Write-Host "Command:"
Write-Host $workerCommand

if ($Apply) {
    wt new-tab --title $title powershell -NoExit -Command $workerCommand
    Write-Host "Worker window opened: YES"
} else {
    Write-Host "Worker window opened: NO"
}

Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host "COPY END - Open-AiOsWorkerWindow.DRY_RUN.ps1"
