param(
    [string]$WorkerId = "",
    [switch]$QuietJson
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

$path = "automation/orchestration/workers/AIOS_WORKER_REGISTRY.json"

if (-not (Test-Path $path)) {
    throw "Worker registry missing: $path"
}

$registry = Get-Content -Raw $path | ConvertFrom-Json

if ([string]::IsNullOrWhiteSpace($WorkerId)) {
    $result = $registry
} else {
    $result = @($registry.workers | Where-Object { $_.worker_id -eq $WorkerId }) | Select-Object -First 1
    if ($null -eq $result) {
        throw "Worker not found: $WorkerId"
    }
}

if ($QuietJson) {
    $result | ConvertTo-Json -Depth 8
    exit 0
}

Write-Host "COPY START - Get-AiOsWorkerRegistry.DRY_RUN.ps1"
Write-Host "AI_OS Worker Registry" -ForegroundColor Cyan

if ([string]::IsNullOrWhiteSpace($WorkerId)) {
    Write-Host "workers: $(@($registry.workers).Count)"
    foreach ($worker in @($registry.workers)) {
        Write-Host ""
        Write-Host "worker_id: $($worker.worker_id)"
        Write-Host "type: $($worker.type)"
        Write-Host "purpose: $($worker.purpose)"
    }
} else {
    Write-Host "worker_id: $($result.worker_id)"
    Write-Host "type: $($result.type)"
    Write-Host "purpose: $($result.purpose)"
    Write-Host "allowed_actions:"
    @($result.allowed_actions) | ForEach-Object { Write-Host "  $_" }
    Write-Host "blocked_actions:"
    @($result.blocked_actions) | ForEach-Object { Write-Host "  $_" }
}

Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host "COPY END - Get-AiOsWorkerRegistry.DRY_RUN.ps1"
