param(
    [switch]$QuietJson
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

$health = "HEALTHY"
$reasons = @()
$nextCommand = "powershell -ExecutionPolicy Bypass -File automation/orchestration/operator/Start-AiOsOperatorDay.ps1"

$branch = git branch --show-current
$status = @(git status --short)

if ($branch -ne "main") {
    $health = "WARNING"
    $reasons += "Not on main branch."
}

if ($status.Count -gt 0) {
    $health = "WARNING"
    $reasons += "Working tree has changes."
}

$requiredFiles = @(
    "automation/orchestration/operator/Start-AiOsOperatorDay.ps1",
    "automation/orchestration/runtime/Start-AiOsRuntimeCycle.DRY_RUN.ps1",
    "automation/orchestration/daemon/Start-AiOsRuntimeDaemon.DRY_RUN.ps1",
    "automation/orchestration/next_step/Resolve-AiOsNextStep.DRY_RUN.ps1",
    "automation/orchestration/approval_processor/Invoke-AiOsApprovalProcessor.DRY_RUN.ps1",
    "automation/orchestration/supervisor/Invoke-AiOsSupervisorLoop.DRY_RUN.ps1"
)

foreach ($file in $requiredFiles) {
    if (-not (Test-Path $file)) {
        $health = "BLOCKED"
        $reasons += "Missing required file: $file"
    }
}

if ($reasons.Count -eq 0) {
    $reasons += "Runtime files present and repo is clean."
}

$result = [pscustomobject]@{
    mode = "READ_ONLY"
    health = $health
    branch = $branch
    reasons = $reasons
    next_command = $nextCommand
}

if ($QuietJson) {
    $result | ConvertTo-Json -Depth 6
    exit 0
}

Write-Host "COPY START - Test-AiOsRuntimeHealth.DRY_RUN.ps1"
Write-Host "AI_OS Runtime Health Monitor" -ForegroundColor Cyan
Write-Host "health: $health"
Write-Host "branch: $branch"
Write-Host "reasons:"
$reasons | ForEach-Object { Write-Host "  $_" }
Write-Host "next_command: $nextCommand"
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host "COPY END - Test-AiOsRuntimeHealth.DRY_RUN.ps1"
