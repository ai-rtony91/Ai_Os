param(
    [int]$IntervalSeconds = 60,
    [int]$MaxCycles = 3,
    [switch]$Apply
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

Write-Host "COPY START — Start-AiOsRuntimeDaemon.DRY_RUN.ps1"
Write-Host "AI_OS Persistent Runtime Daemon" -ForegroundColor Cyan
Write-Host "Mode: $(if ($Apply) { 'APPLY' } else { 'DRY_RUN' })"
Write-Host "IntervalSeconds: $IntervalSeconds"
Write-Host "MaxCycles: $MaxCycles"

for ($i = 1; $i -le $MaxCycles; $i++) {
    Write-Host ""
    Write-Host "DAEMON CYCLE $i" -ForegroundColor Yellow

    if ($Apply) {
        powershell -ExecutionPolicy Bypass -File automation/orchestration/runtime/Start-AiOsRuntimeCycle.DRY_RUN.ps1 -Cycles 1 -Apply
    } else {
        powershell -ExecutionPolicy Bypass -File automation/orchestration/runtime/Start-AiOsRuntimeCycle.DRY_RUN.ps1 -Cycles 1
    }

    if ($i -lt $MaxCycles) {
        Write-Host "Sleeping $IntervalSeconds seconds..."
        Start-Sleep -Seconds $IntervalSeconds
    }
}

Write-Host ""
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host "COPY END — Start-AiOsRuntimeDaemon.DRY_RUN.ps1"
