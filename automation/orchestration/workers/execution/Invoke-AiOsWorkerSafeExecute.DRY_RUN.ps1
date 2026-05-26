param(
    [Parameter(Mandatory = $true)][string]$WorkerId
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

$inboxPath = "automation/orchestration/workers/inbox/AIOS_WORKER_INBOX.json"
$policyScript = "automation/orchestration/policy/Test-AiOsWorkerSafetyPolicy.DRY_RUN.ps1"

$inbox = Get-Content -Raw $inboxPath | ConvertFrom-Json

$task = @(
    $inbox.items |
    Where-Object {
        $_.worker_id -eq $WorkerId -and
        $_.status -eq "inbox"
    }
) | Select-Object -First 1

Write-Host "COPY START - Invoke-AiOsWorkerSafeExecute.DRY_RUN.ps1"
Write-Host "AI_OS Worker Safe Execute" -ForegroundColor Cyan
Write-Host "worker_id: $WorkerId"
Write-Host "mode: DRY_RUN"
Write-Host ""

if ($null -eq $task) {
    Write-Host "No inbox task found."
    Write-Host "Commit performed: NO"
    Write-Host "Push performed: NO"
    Write-Host "COPY END - Invoke-AiOsWorkerSafeExecute.DRY_RUN.ps1"
    exit 0
}

Write-Host "TASK FOUND"
Write-Host "id: $($task.id)"
Write-Host "task: $($task.task)"
Write-Host "reason: $($task.reason)"
Write-Host ""

$policyResult = powershell -ExecutionPolicy Bypass -File $policyScript `
    -Action preview_command `
    -Path automation/orchestration `
    -QuietJson | ConvertFrom-Json

Write-Host "SAFETY RESULT"
Write-Host "result: $($policyResult.result)"
Write-Host "reason: $($policyResult.reason)"
Write-Host ""

if ($policyResult.result -eq "BLOCKED") {
    Write-Host "Execution blocked by policy." -ForegroundColor Red
}
else {
    Write-Host "Would safely execute inbox task."
    Write-Host "Task completion recorded: NO"
}

Write-Host ""
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host "COPY END - Invoke-AiOsWorkerSafeExecute.DRY_RUN.ps1"
