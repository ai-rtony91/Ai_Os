param(
    [int]$Cycles = 3,
    [int]$IntervalSeconds = 5,
    [switch]$Apply
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

Write-Host "AIOS Persistent Runtime Supervisor"
Write-Host "Mode: $(if ($Apply) { 'APPLY' } else { 'DRY_RUN' })"
Write-Host "Cycles: $Cycles"
Write-Host ""

for ($i = 1; $i -le $Cycles; $i++) {

    Write-Host "================================="
    Write-Host "RUNTIME CYCLE $i"
    Write-Host "================================="
    Write-Host ""

    powershell -ExecutionPolicy Bypass -File automation/orchestration/runtime/Invoke-AiOsRuntimeSelfRoute.ps1 -Apply

    if ($Apply) {
        powershell -ExecutionPolicy Bypass -File automation/orchestration/runtime/Invoke-AiOsRuntimePacketAdvancement.ps1 -Apply
    } else {
        powershell -ExecutionPolicy Bypass -File automation/orchestration/runtime/Invoke-AiOsRuntimePacketAdvancement.ps1
    }

    if ($i -lt $Cycles) {
        Write-Host ""
        Write-Host "Sleeping $IntervalSeconds seconds..."
        Start-Sleep -Seconds $IntervalSeconds
    }
}

Write-Host ""
Write-Host "Supervisor complete."
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
