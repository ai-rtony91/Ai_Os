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
        Write-Host ".\aios.ps1 start          # show read-only operator start guidance"
    }

    "start" {
        Write-Host ""
        Write-Host "AIOS Operator Start" -ForegroundColor Cyan
        Write-Host "Mode: DRY_RUN_READ_ONLY"

        Write-Host ""
        Write-Host "CURRENT BRANCH" -ForegroundColor Yellow
        $branch = git branch --show-current
        Write-Host $branch

        Write-Host ""
        Write-Host "DIRTY FILES" -ForegroundColor Yellow
        $dirtyFiles = @(git status --short)
        if ($dirtyFiles.Count -eq 0) {
            Write-Host "- none"
        }
        else {
            $dirtyFiles | ForEach-Object { Write-Host "- $_" }
        }

        Write-Host ""
        Write-Host "ACTIVE PACKET" -ForegroundColor Yellow
        $activePacketRoot = "automation/orchestration/work_packets/active"
        $activePackets = @()
        if (Test-Path -LiteralPath $activePacketRoot -PathType Container) {
            $activePackets = @(Get-ChildItem -LiteralPath $activePacketRoot -File -Filter "*.json" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending)
        }
        if ($activePackets.Count -eq 0) {
            Write-Host "- none"
        }
        else {
            $packetFile = $activePackets[0]
            try {
                $packet = Get-Content -LiteralPath $packetFile.FullName -Raw | ConvertFrom-Json
                $packetId = if ($packet.packet_id) { [string]$packet.packet_id } else { $packetFile.BaseName }
                $packetStatus = if ($packet.status) { [string]$packet.status } else { "UNKNOWN" }
                Write-Host "$packetId [$packetStatus]"
                Write-Host $packetFile.FullName
            }
            catch {
                Write-Host "$($packetFile.Name) [JSON_PARSE_REVIEW_REQUIRED]"
            }
        }

        Write-Host ""
        Write-Host "NEXT RECOMMENDED COMMAND" -ForegroundColor Yellow
        if (Test-Path -LiteralPath automation/runtime/recommendation/Get-AiOsNextCommand.ps1 -PathType Leaf) {
            powershell -ExecutionPolicy Bypass -File automation/runtime/recommendation/Get-AiOsNextCommand.ps1
        }
        else {
            powershell -ExecutionPolicy Bypass -File automation/orchestration/recommendations/Get-AiOsActionRecommendation.DRY_RUN.ps1
        }

        Write-Host ""
        Write-Host "VALIDATOR RECOMMENDATION" -ForegroundColor Yellow
        powershell -ExecutionPolicy Bypass -File automation/orchestration/validators/Get-AiOsValidatorRecommendation.DRY_RUN.ps1

        Write-Host ""
        Write-Host "FILES NOT TO COMMIT" -ForegroundColor Yellow
        powershell -ExecutionPolicy Bypass -File automation/orchestration/commit_packages/New-AiOsCommitPackageRecommendation.DRY_RUN.ps1

        Write-Host ""
        Write-Host "APPROVAL INBOX SUMMARY" -ForegroundColor Yellow
        powershell -ExecutionPolicy Bypass -File automation/orchestration/approval_inbox/Get-AiOsApprovalInboxSummary.DRY_RUN.ps1

        Write-Host ""
        Write-Host "WORKER LOCK STATUS" -ForegroundColor Yellow
        powershell -ExecutionPolicy Bypass -File automation/orchestration/locks/Get-AiOsWorkerLockStatus.DRY_RUN.ps1

        Write-Host ""
        Write-Host "CODEX HANDOFF AVAILABLE" -ForegroundColor Yellow
        Write-Host "Run:"
        Write-Host "powershell -ExecutionPolicy Bypass -File automation/orchestration/handoff/New-AiOsCodexHandoff.DRY_RUN.ps1"

        Write-Host ""
        Write-Host "OPERATOR QUEUE RUNNER AVAILABLE" -ForegroundColor Yellow
        Write-Host "Run:"
        Write-Host "powershell -ExecutionPolicy Bypass -File automation/orchestration/queue_runner/Invoke-AiOsOperatorQueueRunner.DRY_RUN.ps1"

        Write-Host ""
        Write-Host "OPERATOR SESSION BOOTSTRAP AVAILABLE" -ForegroundColor Yellow
        Write-Host "Run:"
        Write-Host "powershell -ExecutionPolicy Bypass -File automation/orchestration/session/Start-AiOsOperatorSession.DRY_RUN.ps1"

        Write-Host ""
        Write-Host "Approval reminders:"
        Write-Host "- No git add, commit, or push was run."
        Write-Host "- No dashboard, broker, trading execution, scheduled task, startup task, or secret path was touched."
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


