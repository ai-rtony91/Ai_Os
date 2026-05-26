param(
    [Parameter(Mandatory = $true)][string]$WorkerId,
    [Parameter(Mandatory = $true)][string]$Type,
    [Parameter(Mandatory = $true)][string]$Purpose
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

$registryPath = "automation/orchestration/workers/AIOS_WORKER_REGISTRY.json"
$workerFolder = "automation/orchestration/workers/custom/$WorkerId"
$workerScript = "$workerFolder/Invoke-$WorkerId.DRY_RUN.ps1"

Write-Host "COPY START - New-AiOsWorker.DRY_RUN.ps1"
Write-Host "AI_OS Worker Builder" -ForegroundColor Cyan
Write-Host "Mode: DRY_RUN"
Write-Host "worker_id: $WorkerId"
Write-Host "type: $Type"
Write-Host "purpose: $Purpose"

$registry = Get-Content -Raw $registryPath | ConvertFrom-Json
$exists = @($registry.workers | Where-Object { $_.worker_id -eq $WorkerId }).Count -gt 0

if ($exists) {
    throw "Worker already exists: $WorkerId"
}

Write-Host "Would create worker folder: $workerFolder"
Write-Host "Would create worker script: $workerScript"
Write-Host "Would update registry: $registryPath"
Write-Host "Worker created: NO"
Write-Host "Mutation skipped: YES - DRY_RUN worker builder cannot create folders, write scripts, or update registry."

Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host "COPY END - New-AiOsWorker.DRY_RUN.ps1"
