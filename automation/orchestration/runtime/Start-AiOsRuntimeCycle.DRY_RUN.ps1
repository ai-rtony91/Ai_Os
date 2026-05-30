param(
    [ValidateRange(1, 5)][int]$Cycles = 1
)
# RECURSION GUARD: Maximum 5 cycles enforced by ValidateRange.
# Each cycle spawns 14+ subprocesses.
# If supervisor_status = BLOCKED, the supervisor loop must not call
# Resolve-AiOsNextStep for that cycle. See Invoke-AiOsSupervisorLoop.DRY_RUN.ps1.

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

Write-Host "COPY START — Start-AiOsRuntimeCycle.DRY_RUN.ps1"
Write-Host "AI_OS Autonomous Runtime Cycle" -ForegroundColor Cyan
Write-Host "Mode: DRY_RUN"
Write-Host "Cycles: $Cycles"
Write-Host ""

for ($i = 1; $i -le $Cycles; $i++) {
    Write-Host "=============================="
    Write-Host "RUNTIME CYCLE $i"
    Write-Host "=============================="

    # do/while($false) is the PowerShell idiom for a breakable step sequence:
    # break exits this inner block only — the outer for-loop continues to the next cycle.
    # $ErrorActionPreference = "Stop" does NOT catch subprocess exit codes; explicit checks are required.
    do {
        Write-Host ""
        Write-Host "STEP 1 - OPERATOR OBSERVE" -ForegroundColor Yellow
        powershell -ExecutionPolicy Bypass -File automation/orchestration/bootstrap/Start-AiOsDay.ps1
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "CYCLE $i STEP 1 failed (exit code $LASTEXITCODE). Skipping remaining steps in this cycle."
            break
        }

        Write-Host ""
        Write-Host "STEP 2 - APPROVAL PROCESSOR" -ForegroundColor Yellow
        powershell -ExecutionPolicy Bypass -File automation/orchestration/approval_processor/Invoke-AiOsApprovalProcessor.DRY_RUN.ps1
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "CYCLE $i STEP 2 failed (exit code $LASTEXITCODE). Skipping remaining steps in this cycle."
            break
        }

        Write-Host ""
        Write-Host "STEP 3 - SUPERVISOR LOOP" -ForegroundColor Yellow
        powershell -ExecutionPolicy Bypass -File automation/orchestration/supervisor/Invoke-AiOsSupervisorLoop.DRY_RUN.ps1
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "CYCLE $i STEP 3 failed (exit code $LASTEXITCODE). Skipping remaining steps in this cycle."
            break
        }

        Write-Host ""
        Write-Host "STEP 4 - NEXT STEP AFTER ACTION" -ForegroundColor Yellow
        powershell -ExecutionPolicy Bypass -File automation/orchestration/next_step/Resolve-AiOsNextStep.DRY_RUN.ps1
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "CYCLE $i STEP 4 failed (exit code $LASTEXITCODE)."
            break
        }
    } while ($false)
}

Write-Host ""
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host "COPY END — Start-AiOsRuntimeCycle.DRY_RUN.ps1"
