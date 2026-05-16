param(
    [switch]$Apply
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

$workers = @(
    "task_generator",
    "health_monitor",
    "approval_processor",
    "runtime_daemon"
)

Write-Host "COPY START - Open-AiOsWorkerSwarm.DRY_RUN.ps1"
Write-Host "AI_OS Supervisor Worker Swarm" -ForegroundColor Cyan
Write-Host "Mode: $(if ($Apply) { 'APPLY' } else { 'DRY_RUN' })"
Write-Host ""

foreach ($workerId in $workers) {

    Write-Host "WORKER:"
    Write-Host "  $workerId"

    $command = "powershell -ExecutionPolicy Bypass -File automation/orchestration/workers/launcher/Open-AiOsWorkerWindow.DRY_RUN.ps1 -WorkerId $workerId"

    if ($Apply) {
        powershell -ExecutionPolicy Bypass -File automation/orchestration/workers/launcher/Open-AiOsWorkerWindow.DRY_RUN.ps1 -WorkerId $workerId -Apply
        Write-Host "  launched: YES" -ForegroundColor Green
    }
    else {
        Write-Host "  would_launch: YES"
    }

    Write-Host "  command: $command"
    Write-Host ""
}

Write-Host "Swarm workers: $($workers.Count)"
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host "COPY END - Open-AiOsWorkerSwarm.DRY_RUN.ps1"
