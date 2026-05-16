param(
    [Parameter(Mandatory = $true)][string]$ItemId,
    [string]$ResultNote = "",
    [switch]$Apply
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

$inboxPath = "automation/orchestration/workers/inbox/AIOS_WORKER_INBOX.json"
$memoryScript = "automation/orchestration/memory/Update-AiOsRuntimeMemory.DRY_RUN.ps1"

$inbox = Get-Content -Raw $inboxPath | ConvertFrom-Json
$items = @($inbox.items)
$item = @($items | Where-Object { $_.id -eq $ItemId }) | Select-Object -First 1

Write-Host "COPY START - Complete-AiOsWorkerInboxItem.DRY_RUN.ps1"
Write-Host "AI_OS Worker Task Completion" -ForegroundColor Cyan
Write-Host "Mode: $(if ($Apply) { 'APPLY' } else { 'DRY_RUN' })"
Write-Host "item_id: $ItemId"

if ($null -eq $item) {
    throw "Inbox item not found: $ItemId"
}

Write-Host "worker_id: $($item.worker_id)"
Write-Host "task: $($item.task)"
Write-Host "current_status: $($item.status)"
Write-Host "result_note: $ResultNote"

if ($Apply) {
    foreach ($entry in $items) {
        if ($entry.id -eq $ItemId) {
            $entry.status = "complete"
            $entry.completed_utc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
            $entry.result_note = $ResultNote
        }
    }

    $inbox.items = $items
    $inbox | ConvertTo-Json -Depth 10 | Set-Content $inboxPath -Encoding UTF8

    powershell -ExecutionPolicy Bypass -File $memoryScript -Action write -Note "Worker completed inbox item $ItemId. $ResultNote" -Apply

    Write-Host "Inbox item completed: YES" -ForegroundColor Green
} else {
    Write-Host "Inbox item completed: NO"
}

Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host "COPY END - Complete-AiOsWorkerInboxItem.DRY_RUN.ps1"
