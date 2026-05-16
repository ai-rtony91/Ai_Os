param(
    [Parameter(Mandatory = $true)][string]$Task,
    [Parameter(Mandatory = $true)][string]$Reason,
    [switch]$Apply
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

$registryPath = "automation/orchestration/workers/AIOS_WORKER_REGISTRY.json"
$inboxScript = "automation/orchestration/workers/inbox/Add-AiOsWorkerInboxItem.DRY_RUN.ps1"

$registry = Get-Content -Raw $registryPath | ConvertFrom-Json

$selectedWorker = "task_generator"

if ($Task -match "health|runtime|repair") {
    $selectedWorker = "health_monitor"
}
elseif ($Task -match "approval|pr|merge") {
    $selectedWorker = "approval_processor"
}
elseif ($Task -match "validat|check|review") {
    $selectedWorker = "validator_worker"
}
elseif ($Task -match "queue|packet|generate|task") {
    $selectedWorker = "task_generator"
}

$worker = @($registry.workers | Where-Object {
    $_.worker_id -eq $selectedWorker
}) | Select-Object -First 1

Write-Host "COPY START - Invoke-AiOsTaskRouter.DRY_RUN.ps1"
Write-Host "AI_OS Worker Task Router" -ForegroundColor Cyan
Write-Host "Task: $Task"
Write-Host "Reason: $Reason"
Write-Host ""
Write-Host "Assigned worker:"
Write-Host "  worker_id: $selectedWorker"
Write-Host "  type: $($worker.type)"
Write-Host "  purpose: $($worker.purpose)"
Write-Host ""

if ($Apply) {
    powershell -ExecutionPolicy Bypass -File $inboxScript `
        -WorkerId $selectedWorker `
        -Task $Task `
        -Reason $Reason `
        -Apply

    Write-Host "Inbox assignment: YES" -ForegroundColor Green
}
else {
    Write-Host "Inbox assignment: NO"
}

Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host "COPY END - Invoke-AiOsTaskRouter.DRY_RUN.ps1"
