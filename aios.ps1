param(
    [ValidateSet("help","daily","morning","swarm","status","resume","workers","runtime","supervisor","mission","runner")]
    [string]$Mode = "help",
    [string]$Goal = "Build next AIOS runtime loop step",
    [string]$MissionName = "",
    [int]$WorkerCount = 4,
    [ValidateSet("auto","compact","wide","dual-monitor")]
    [string]$Preset = "auto",
    [switch]$ApplyMission,
    [string]$MissionPath = "",
    [string]$TaskId = "",
    [switch]$ShowPrompt
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
        Write-Host ".\aios.ps1 -Mode morning  # run morning operations intelligence"
        Write-Host ".\aios.ps1 -Mode status   # show health, next action, inbox"
        Write-Host ".\aios.ps1 -Mode resume   # resume last session"
        Write-Host ".\aios.ps1 -Mode workers  # show worker list and inbox"
        Write-Host ".\aios.ps1 -Mode swarm    # launch worker swarm"
        Write-Host ".\aios.ps1 -Mode runtime  # run goal intake + recommendation + health"
        Write-Host ".\aios.ps1 -Mode supervisor # run repeated runtime self-routing cycles"
        Write-Host ".\aios.ps1 -Mode mission -Goal ""Improve AIOS runtime automation"" # create Mission Control plan DRY_RUN"
        Write-Host ".\aios.ps1 -Mode runner -MissionPath automation/mission_control/missions/improve-aios-runtime-automation # show next safe mission action"
        Write-Host ".\aios.ps1 -Mode runner -MissionPath automation/mission_control/missions/improve-aios-runtime-automation -TaskId MC-01 -ShowPrompt # show task prompt"
    }

    "daily" {
        powershell -ExecutionPolicy Bypass -File automation/session/Start-AiOsDailyFlow.ps1 -RunWorkerPreview
    }
    "morning" {
    powershell -ExecutionPolicy Bypass -File automation/operator/Start-AiOsMorningOperations.ps1
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

   "mission" {
    $missionArgs = @(
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        "automation/mission_control/New-AiOsMissionPlan.ps1",
        "-Goal",
        $Goal,
        "-WorkerCount",
        $WorkerCount,
        "-Preset",
        $Preset
    )

    if (-not [string]::IsNullOrWhiteSpace($MissionName)) {
        $missionArgs += @("-MissionName", $MissionName)
    }

    if ($ApplyMission) {
        $missionArgs += "-Apply"
    }

    powershell @missionArgs
}

   "runner" {
    if ([string]::IsNullOrWhiteSpace($MissionPath)) {
        Write-Host "BLOCKED: -MissionPath is required for runner mode." -ForegroundColor Red
        exit 1
    }

    $runnerArgs = @(
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        "automation/mission_control/Get-AiOsMissionNextAction.ps1",
        "-MissionPath",
        $MissionPath
    )

    if (-not [string]::IsNullOrWhiteSpace($TaskId)) {
        $runnerArgs += @("-TaskId", $TaskId)
    }

    if ($ShowPrompt) {
        $runnerArgs += "-ShowPrompt"
    }

    powershell @runnerArgs
}
}

Write-Host "AIOS SHORTCUT END" -ForegroundColor Green


