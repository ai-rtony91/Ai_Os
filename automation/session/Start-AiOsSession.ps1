Set-StrictMode -Off
$ErrorActionPreference = "Stop"

Write-Host "COPY START - Start-AiOsSession.ps1"
Write-Host "AI_OS Session Bootstrap" -ForegroundColor Cyan
Write-Host ""

Write-Host "STEP 1 - Health Check" -ForegroundColor Yellow
powershell -ExecutionPolicy Bypass -File automation/orchestration/health/Test-AiOsRuntimeHealth.DRY_RUN.ps1

Write-Host ""
Write-Host "STEP 2 - Runtime Memory" -ForegroundColor Yellow
powershell -ExecutionPolicy Bypass -File automation/orchestration/memory/Update-AiOsRuntimeMemory.DRY_RUN.ps1

Write-Host ""
Write-Host "STEP 3 - Worker Registry" -ForegroundColor Yellow
powershell -ExecutionPolicy Bypass -File automation/orchestration/workers/Get-AiOsWorkerRegistry.DRY_RUN.ps1

Write-Host ""
Write-Host "STEP 4 - Command Pack Health Check" -ForegroundColor Yellow
powershell -ExecutionPolicy Bypass -File automation/command_packs/Run-AiOsCommandPack.ps1 -Pack health-check

Write-Host ""
Write-Host "STEP 5 - Runtime Blocker" -ForegroundColor Yellow
powershell -ExecutionPolicy Bypass -File automation/orchestration/blockers/Resolve-AiOsRuntimeBlocker.DRY_RUN.ps1

Write-Host ""
Write-Host "SESSION READY" -ForegroundColor Green
Write-Host "Recommended next command:"
Write-Host "powershell -ExecutionPolicy Bypass -File automation/orchestration/advancement/Invoke-AiOsPacketAdvancement.DRY_RUN.ps1"

Write-Host ""
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host "COPY END - Start-AiOsSession.ps1"
