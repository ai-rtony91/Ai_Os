param(
    [ValidateSet("help","start","daily","swarm","status","resume","workers","runtime","supervisor")]
    [string]$Mode = "help",
    [string]$Goal = "Build next AIOS runtime loop step"
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

Write-Host "AIOS SHORTCUT START" -ForegroundColor Cyan
Write-Host "Mode: $Mode"

switch ($Mode) {
    "help" {
        Write-Host ""
        Write-Host "Available commands:"
        Write-Host ".\aios.ps1 -Mode daily    # run normal daily flow"
        Write-Host ".\aios.ps1 -Mode status   # show health, next action, inbox"
        Write-Host ".\aios.ps1 -Mode resume   # resume last session"
        Write-Host ".\aios.ps1 -Mode workers  # show worker list and inbox"
        Write-Host ".\aios.ps1 -Mode swarm    # launch worker swarm"
        Write-Host ".\aios.ps1 -Mode runtime  # run goal intake + recommendation + health"
        Write-Host ".\aios.ps1 -Mode supervisor # run repeated runtime self-routing cycles"
        Write-Host ".\aios.ps1 start          # run operator-approved daily start"
    }

    "start" {
        Write-Host ""
        Write-Host "AIOS Daily Start"
        Write-Host "1. Validate path registry"
        powershell -ExecutionPolicy Bypass -File automation/runtime/path_registry/Test-AiOsPathRegistry.ps1

        Write-Host ""
        Write-Host "2. Validate runtime state"
        if (Test-Path -LiteralPath automation/runtime/state/AIOS_RUNTIME_STATE.json -PathType Leaf) {
            Get-Content -LiteralPath automation/runtime/state/AIOS_RUNTIME_STATE.json -Raw | ConvertFrom-Json | Out-Null
            Write-Host "Runtime state JSON: PASS"
        }
        else {
            Write-Host "Runtime state JSON: MISSING"
        }

        Write-Host ""
        Write-Host "3. Write runtime state"
        powershell -ExecutionPolicy Bypass -File automation/runtime/state/Write-AiOsRuntimeState.ps1

        Write-Host ""
        Write-Host "4. Worker layout"
        if (Test-Path -LiteralPath automation/window_identity/Open-AiOsWorkerWindowLayout.ps1 -PathType Leaf) {
            Write-Host "Worker layout available: automation/window_identity/Open-AiOsWorkerWindowLayout.ps1"
            Write-Host "Operator-approved command:"
            Write-Host "powershell -ExecutionPolicy Bypass -File automation/window_identity/Open-AiOsWorkerWindowLayout.ps1"
        }
        else {
            Write-Host "Worker layout unavailable."
        }

        Write-Host ""
        Write-Host "5. Active packet and repo status"
        powershell -ExecutionPolicy Bypass -File automation/runtime/reports/Write-AiOsRepoStatusReport.ps1

        Write-Host ""
        Write-Host "6. Next recommended command"
        powershell -ExecutionPolicy Bypass -File automation/runtime/recommendation/Get-AiOsNextCommand.ps1

        Write-Host ""
        Write-Host "7. Approval reminders"
        Write-Host "No autonomous APPLY execution."
        Write-Host "No broker, live trading, secrets, startup task, scheduled task, dashboard, commit, or push action is performed."
    }

    "daily" {
        powershell -ExecutionPolicy Bypass -File automation/session/Start-AiOsDailyFlow.ps1 -RunWorkerPreview
    }

    "swarm" {
        powershell -ExecutionPolicy Bypass -File automation/session/Start-AiOsDailyFlow.ps1 -LaunchSwarm -RunWorkerPreview
    }

    "status" {
        powershell -ExecutionPolicy Bypass -File automation/orchestration/health/Test-AiOsRuntimeHealth.DRY_RUN.ps1
        powershell -ExecutionPolicy Bypass -File automation/orchestration/recommendations/Get-AiOsActionRecommendation.DRY_RUN.ps1
        powershell -ExecutionPolicy Bypass -File automation/orchestration/workers/inbox/Get-AiOsWorkerInbox.DRY_RUN.ps1
    }

    "resume" {
        powershell -ExecutionPolicy Bypass -File automation/session/Resume-AiOsSession.ps1
    }

    "workers" {
        powershell -ExecutionPolicy Bypass -File automation/orchestration/workers/Get-AiOsWorkerRegistry.DRY_RUN.ps1
        powershell -ExecutionPolicy Bypass -File automation/orchestration/workers/inbox/Get-AiOsWorkerInbox.DRY_RUN.ps1
    }

    "runtime" {

    powershell -ExecutionPolicy Bypass -File checkpoints/verify_success.ps1

    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "BLOCKED: proof verification failed" -ForegroundColor Red
        exit 1
    }

    powershell -ExecutionPolicy Bypass -File automation/intake/Start-AiOsRuntimeLoop.ps1 -Goal $Goal -Apply
}

   "supervisor" {

    powershell -ExecutionPolicy Bypass -File checkpoints/verify_success.ps1

    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "BLOCKED: proof verification failed" -ForegroundColor Red
        exit 1
    }

    powershell -ExecutionPolicy Bypass -File automation/orchestration/runtime/Start-AiOsPersistentRuntimeSupervisor.ps1 -Cycles 3 -Apply
}
}

Write-Host "AIOS SHORTCUT END" -ForegroundColor Green


