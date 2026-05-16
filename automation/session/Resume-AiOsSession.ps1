Set-StrictMode -Off
$ErrorActionPreference = "Stop"

Write-Host "COPY START - Resume-AiOsSession.ps1"
Write-Host "AI_OS Auto Resume Session" -ForegroundColor Cyan

$memoryPath = "automation/orchestration/memory/AIOS_RUNTIME_MEMORY.json"

if (-not (Test-Path $memoryPath)) {
    Write-Host "No memory file found."
    Write-Host "Run: powershell -ExecutionPolicy Bypass -File automation/session/Start-AiOsSession.ps1"
    Write-Host "COPY END - Resume-AiOsSession.ps1"
    exit 0
}

$memory = Get-Content -Raw $memoryPath | ConvertFrom-Json

Write-Host ""
Write-Host "LAST MEMORY"
Write-Host "last_action: $($memory.last_action)"
Write-Host "last_note: $($memory.last_note)"
Write-Host "history_count: $(@($memory.history).Count)"

Write-Host ""
Write-Host "CURRENT NEXT STEP"
powershell -ExecutionPolicy Bypass -File automation/orchestration/next_step/Resolve-AiOsNextStep.DRY_RUN.ps1

Write-Host ""
Write-Host "CURRENT BLOCKER"
powershell -ExecutionPolicy Bypass -File automation/orchestration/blockers/Resolve-AiOsRuntimeBlocker.DRY_RUN.ps1

Write-Host ""
Write-Host "RESUME RECOMMENDATION" -ForegroundColor Yellow
Write-Host "Run:"
Write-Host "powershell -ExecutionPolicy Bypass -File automation/orchestration/advancement/Invoke-AiOsPacketAdvancement.DRY_RUN.ps1"

Write-Host ""
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host "COPY END - Resume-AiOsSession.ps1"
