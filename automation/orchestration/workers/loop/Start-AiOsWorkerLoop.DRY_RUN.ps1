param(
    [Parameter(Mandatory = $true)][string]$WorkerId,
    [int]$Cycles = 3,
    [int]$IntervalSeconds = 5,
    [switch]$Apply
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

Write-Host "COPY START - Start-AiOsWorkerLoop.DRY_RUN.ps1"
Write-Host "AI_OS Worker Auto Loop" -ForegroundColor Cyan
Write-Host "Worker: $WorkerId"
Write-Host "Cycles: $Cycles"
Write-Host "Mode: $(if ($Apply) { 'APPLY' } else { 'DRY_RUN' })"

for ($i = 1; $i -le $Cycles; $i++) {
    Write-Host ""
    Write-Host "WORKER LOOP CYCLE $i" -ForegroundColor Yellow

    powershell -ExecutionPolicy Bypass -File automation/orchestration/workers/inbox/Get-AiOsWorkerInbox.DRY_RUN.ps1 -WorkerId $WorkerId

    Write-Host ""
    Write-Host "Worker checked inbox."
    Write-Host "Action taken: NO"

    if ($i -lt $Cycles) {
        Write-Host "Sleeping $IntervalSeconds seconds..."
        Start-Sleep -Seconds $IntervalSeconds
    }
}

Write-Host ""
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host "COPY END - Start-AiOsWorkerLoop.DRY_RUN.ps1"
