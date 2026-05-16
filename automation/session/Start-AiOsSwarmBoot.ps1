param(
    [switch]$LaunchSwarm,
    [switch]$RunDaemonPreview
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

Write-Host "COPY START - Start-AiOsSwarmBoot.ps1"
Write-Host "AI_OS One Command Swarm Boot" -ForegroundColor Cyan
Write-Host ""

Write-Host "STEP 1 - Session Start" -ForegroundColor Yellow
powershell -ExecutionPolicy Bypass -File automation/session/Start-AiOsSession.ps1

Write-Host ""
Write-Host "STEP 2 - Action Recommendation" -ForegroundColor Yellow
powershell -ExecutionPolicy Bypass -File automation/orchestration/recommendations/Get-AiOsActionRecommendation.DRY_RUN.ps1

Write-Host ""
Write-Host "STEP 3 - Worker Swarm Preview" -ForegroundColor Yellow
powershell -ExecutionPolicy Bypass -File automation/orchestration/swarm/Open-AiOsWorkerSwarm.DRY_RUN.ps1

if ($LaunchSwarm) {
    Write-Host ""
    Write-Host "STEP 4 - Launch Worker Swarm" -ForegroundColor Yellow
    powershell -ExecutionPolicy Bypass -File automation/orchestration/swarm/Open-AiOsWorkerSwarm.DRY_RUN.ps1 -Apply
}

if ($RunDaemonPreview) {
    Write-Host ""
    Write-Host "STEP 5 - Worker Daemon Preview" -ForegroundColor Yellow
    powershell -ExecutionPolicy Bypass -File automation/orchestration/workers/daemon/Start-AiOsWorkerDaemon.DRY_RUN.ps1 -WorkerId validator_worker -IntervalSeconds 3 -MaxCycles 2
}

Write-Host ""
Write-Host "SWARM BOOT READY" -ForegroundColor Green
Write-Host "Recommended next:"
Write-Host "powershell -ExecutionPolicy Bypass -File automation/orchestration/workers/daemon/Start-AiOsWorkerDaemon.DRY_RUN.ps1 -WorkerId validator_worker -IntervalSeconds 10 -MaxCycles 10"

Write-Host ""
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host "COPY END - Start-AiOsSwarmBoot.ps1"
