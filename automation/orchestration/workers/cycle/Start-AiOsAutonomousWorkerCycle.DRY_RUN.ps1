param(
    [Parameter(Mandatory = $true)][string]$WorkerId,
    [int]$Cycles = 3,
    [int]$IntervalSeconds = 5,
    [switch]$Apply
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

$logRoot = "automation/orchestration/workers/logs"
$logPath = Join-Path $logRoot "$WorkerId.log"
$executeScript = "automation/orchestration/workers/execution/Invoke-AiOsWorkerSafeExecute.DRY_RUN.ps1"
$inboxScript = "automation/orchestration/workers/inbox/Get-AiOsWorkerInbox.DRY_RUN.ps1"

New-Item -ItemType Directory -Force -Path $logRoot | Out-Null

function Write-AiOsLog {
    param([string]$Message)
    $utc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    "$utc [$WorkerId] $Message" | Add-Content $logPath
}

Write-Host "COPY START - Start-AiOsAutonomousWorkerCycle.DRY_RUN.ps1"
Write-Host "AI_OS Autonomous Worker Cycle" -ForegroundColor Cyan
Write-Host "Worker: $WorkerId"
Write-Host "Cycles: $Cycles"
Write-Host "Mode: $(if ($Apply) { 'APPLY' } else { 'DRY_RUN' })"
Write-Host "Log: $logPath"

Write-AiOsLog "Worker cycle started. Apply=$Apply Cycles=$Cycles"

for ($i = 1; $i -le $Cycles; $i++) {
    Write-Host ""
    Write-Host "WORKER CYCLE $i" -ForegroundColor Yellow
    Write-AiOsLog "Cycle $i started."

    powershell -ExecutionPolicy Bypass -File $inboxScript -WorkerId $WorkerId

    if ($Apply) {
        powershell -ExecutionPolicy Bypass -File $executeScript -WorkerId $WorkerId -Apply
        Write-AiOsLog "Safe execute attempted with Apply."
    } else {
        powershell -ExecutionPolicy Bypass -File $executeScript -WorkerId $WorkerId
        Write-AiOsLog "Safe execute previewed."
    }

    if ($i -lt $Cycles) {
        Write-Host "Sleeping $IntervalSeconds seconds..."
        Start-Sleep -Seconds $IntervalSeconds
    }
}

Write-AiOsLog "Worker cycle finished."

Write-Host ""
Write-Host "Worker cycle complete."
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host "COPY END - Start-AiOsAutonomousWorkerCycle.DRY_RUN.ps1"
