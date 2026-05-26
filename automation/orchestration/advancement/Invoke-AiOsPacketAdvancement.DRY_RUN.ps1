param(
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

Write-Host "COPY START - Invoke-AiOsPacketAdvancement.DRY_RUN.ps1"
Write-Host "AI_OS Autonomous Packet Advancement" -ForegroundColor Cyan
Write-Host "Mode: DRY_RUN"

Write-Host ""
Write-Host "STEP 1 - APPROVAL PROCESSOR"
powershell -ExecutionPolicy Bypass -File automation/orchestration/approval_processor/Invoke-AiOsApprovalProcessor.DRY_RUN.ps1

Write-Host ""
Write-Host "STEP 2 - SUPERVISOR LOOP"
powershell -ExecutionPolicy Bypass -File automation/orchestration/supervisor/Invoke-AiOsSupervisorLoop.DRY_RUN.ps1

Write-Host ""
Write-Host "STEP 3 - TASK GENERATOR"
powershell -ExecutionPolicy Bypass -File automation/orchestration/task_generator/New-AiOsTaskFromNextStep.DRY_RUN.ps1

Write-Host ""
Write-Host "STEP 4 - BLOCKER RESOLVER"
powershell -ExecutionPolicy Bypass -File automation/orchestration/blockers/Resolve-AiOsRuntimeBlocker.DRY_RUN.ps1

Write-Host ""
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host "COPY END - Invoke-AiOsPacketAdvancement.DRY_RUN.ps1"
