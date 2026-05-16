param(
    [Parameter(Mandatory = $true)][string]$WorkerId,
    [int]$IntervalSeconds = 10,
    [int]$MaxCycles = 10,
    [switch]$Apply
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

$cycleScript = "automation/orchestration/workers/cycle/Start-AiOsAutonomousWorkerCycle.DRY_RUN.ps1"

Write-Host "COPY START - Start-AiOsWorkerDaemon.DRY_RUN.ps1"
Write-Host "AI_OS Persistent Worker Daemon" -ForegroundColor Cyan
Write-Host "Worker: $WorkerId"
Write-Host "IntervalSeconds: $IntervalSeconds"
Write-Host "MaxCycles: $MaxCycles"
Write-Host "Mode: $(if ($Apply) { 'APPLY' } else { 'DRY_RUN' })"
Write-Host ""

for ($i = 1; $i -le $MaxCycles; $i++) {
    Write-Host "DAEMON PASS $i" -ForegroundColor Yellow

    if ($Apply) {
        powershell -ExecutionPolicy Bypass -File $cycleScript -WorkerId $WorkerId -Cycles 1 -IntervalSeconds 1 -Apply
    } else {
        powershell -ExecutionPolicy Bypass -File $cycleScript -WorkerId $WorkerId -Cycles 1 -IntervalSeconds 1
    }

    if ($i -lt $MaxCycles) {
        Write-Host "Waiting $IntervalSeconds seconds..."
        Start-Sleep -Seconds $IntervalSeconds
    }
}

Write-Host ""
Write-Host "Daemon finished safely."
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host "COPY END - Start-AiOsWorkerDaemon.DRY_RUN.ps1"
