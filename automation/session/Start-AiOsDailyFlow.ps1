param(
    [switch]$LaunchSwarm,
    [switch]$RunWorkerPreview
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

Write-Host "COPY START - Start-AiOsDailyFlow.ps1"
Write-Host "AI_OS Daily Flow" -ForegroundColor Cyan

Write-Host ""
Write-Host "STEP 1 - Session"
powershell -ExecutionPolicy Bypass -File automation/session/Start-AiOsSession.ps1

Write-Host ""
Write-Host "STEP 2 - Resume"
powershell -ExecutionPolicy Bypass -File automation/session/Resume-AiOsSession.ps1

Write-Host ""
Write-Host "STEP 3 - Recommendation"
powershell -ExecutionPolicy Bypass -File automation/orchestration/recommendations/Get-AiOsActionRecommendation.DRY_RUN.ps1

Write-Host ""
Write-Host "STEP 4 - Self Heal"
powershell -ExecutionPolicy Bypass -File automation/orchestration/self_heal/Invoke-AiOsSelfHeal.DRY_RUN.ps1

Write-Host ""
Write-Host "STEP 5 - Worker Inbox"
powershell -ExecutionPolicy Bypass -File automation/orchestration/workers/inbox/Get-AiOsWorkerInbox.DRY_RUN.ps1

if ($RunWorkerPreview) {
    Write-Host ""
    Write-Host "STEP 6 - Worker Preview"
    powershell -ExecutionPolicy Bypass -File automation/orchestration/workers/cycle/Start-AiOsAutonomousWorkerCycle.DRY_RUN.ps1 -WorkerId validator_worker -Cycles 1 -IntervalSeconds 1
}

if ($LaunchSwarm) {
    Write-Host ""
    Write-Host "STEP 7 - Launch Swarm"
    powershell -ExecutionPolicy Bypass -File automation/orchestration/swarm/Open-AiOsWorkerSwarm.DRY_RUN.ps1 -Apply
}

Write-Host ""
Write-Host "DAILY FLOW READY" -ForegroundColor Green
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host "COPY END - Start-AiOsDailyFlow.ps1"
