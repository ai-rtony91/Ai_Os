param(
    [Parameter(Mandatory = $true)][string]$ItemId,
    [string]$ResultNote = "",
    [switch]$Apply
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

$inboxPath = "automation/orchestration/workers/inbox/AIOS_WORKER_INBOX.json"

$inbox = Get-Content -Raw $inboxPath | ConvertFrom-Json
$items = @($inbox.items)
$item = @($items | Where-Object { $_.id -eq $ItemId }) | Select-Object -First 1

Write-Host "COPY START - Complete-AiOsWorkerInboxItem.DRY_RUN.ps1"
Write-Host "AI_OS Worker Task Completion" -ForegroundColor Cyan
Write-Host "Mode: DRY_RUN"
Write-Host "item_id: $ItemId"

if ($null -eq $item) {
    throw "Inbox item not found: $ItemId"
}

Write-Host "worker_id: $($item.worker_id)"
Write-Host "task: $($item.task)"
Write-Host "current_status: $($item.status)"
Write-Host "result_note: $ResultNote"

if ($item.status -eq "complete") {
    Write-Host "completion_validation: WARN - item is already complete" -ForegroundColor Yellow
} else {
    Write-Host "completion_validation: PASS"
}

$proposedCompletion = [pscustomobject]@{
    id = $item.id
    worker_id = $item.worker_id
    task = $item.task
    current_status = $item.status
    proposed_status = "complete"
    result_note = $ResultNote
    proposed_completed_utc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
}

Write-Host "Would-be completion update:"
$proposedCompletion | ConvertTo-Json -Depth 10

Write-Host "Requested mutation: complete worker inbox item"
Write-Host "Mutation skipped: YES"
Write-Host "Inbox item completed: NO"
Write-Host "Runtime memory updated: NO"
Write-Host "Files changed: NO"
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host "COPY END - Complete-AiOsWorkerInboxItem.DRY_RUN.ps1"
