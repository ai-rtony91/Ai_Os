param(
    [Parameter(Mandatory = $true)][string]$WorkerId,
    [Parameter(Mandatory = $true)][string]$Type,
    [Parameter(Mandatory = $true)][string]$Purpose,
    [switch]$Apply
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

$registryPath = "automation/orchestration/workers/AIOS_WORKER_REGISTRY.json"
$workerFolder = "automation/orchestration/workers/custom/$WorkerId"
$workerScript = "$workerFolder/Invoke-$WorkerId.DRY_RUN.ps1"

Write-Host "COPY START - New-AiOsWorker.DRY_RUN.ps1"
Write-Host "AI_OS Worker Builder" -ForegroundColor Cyan
Write-Host "Mode: $(if ($Apply) { 'APPLY' } else { 'DRY_RUN' })"
Write-Host "worker_id: $WorkerId"
Write-Host "type: $Type"
Write-Host "purpose: $Purpose"

$registry = Get-Content -Raw $registryPath | ConvertFrom-Json
$exists = @($registry.workers | Where-Object { $_.worker_id -eq $WorkerId }).Count -gt 0

if ($exists) {
    throw "Worker already exists: $WorkerId"
}

if ($Apply) {
    New-Item -ItemType Directory -Force -Path $workerFolder | Out-Null

@"
Set-StrictMode -Off
`$ErrorActionPreference = "Stop"

Write-Host "COPY START - Invoke-$WorkerId.DRY_RUN.ps1"
Write-Host "AIOS CUSTOM WORKER: $WorkerId" -ForegroundColor Cyan
Write-Host "Type: $Type"
Write-Host "Purpose: $Purpose"
Write-Host "Status: READY"
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host "COPY END - Invoke-$WorkerId.DRY_RUN.ps1"
"@ | Set-Content $workerScript -Encoding UTF8

    $newWorker = [pscustomobject]@{
        worker_id = $WorkerId
        type = $Type
        purpose = $Purpose
        allowed_actions = @("read_inbox","preview_task","report_status")
        blocked_actions = @("merge_pr","touch_secrets","live_trading","delete_files")
    }

    $registry.workers = @($registry.workers) + $newWorker
    $registry | ConvertTo-Json -Depth 10 | Set-Content $registryPath -Encoding UTF8

    Write-Host "Worker created: YES" -ForegroundColor Green
    Write-Host "Worker script: $workerScript"
} else {
    Write-Host "Worker created: NO"
}

Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host "COPY END - New-AiOsWorker.DRY_RUN.ps1"
