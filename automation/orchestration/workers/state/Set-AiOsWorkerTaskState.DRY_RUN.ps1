param(
    [Parameter(Mandatory = $true)][string]$ItemId,
    [Parameter(Mandatory = $true)]
    [ValidateSet("inbox","claimed","running","complete","failed")]
    [string]$State,
    [string]$Note = "",
    [switch]$Apply
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

$inboxPath = "automation/orchestration/workers/inbox/AIOS_WORKER_INBOX.json"

$inbox = Get-Content -Raw $inboxPath | ConvertFrom-Json
$items = @($inbox.items)
$item = @($items | Where-Object { $_.id -eq $ItemId }) | Select-Object -First 1

Write-Host "COPY START - Set-AiOsWorkerTaskState.DRY_RUN.ps1"
Write-Host "AI_OS Worker Task State Machine" -ForegroundColor Cyan
Write-Host "Mode: DRY_RUN"
Write-Host "item_id: $ItemId"
Write-Host "target_state: $State"

if ($null -eq $item) {
    throw "Inbox item not found: $ItemId"
}

Write-Host "current_state: $($item.status)"
Write-Host "worker_id: $($item.worker_id)"
Write-Host "task: $($item.task)"
Write-Host "note: $Note"

$allowed = $false

if ($item.status -eq "inbox" -and $State -eq "claimed") { $allowed = $true }
if ($item.status -eq "claimed" -and $State -eq "running") { $allowed = $true }
if ($item.status -eq "running" -and $State -eq "complete") { $allowed = $true }
if ($item.status -eq "running" -and $State -eq "failed") { $allowed = $true }

if (-not $allowed) {
    throw "Blocked state move: $($item.status) -> $State"
}

$updatedUtc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
$proposedUpdate = [pscustomobject]@{
    id = $ItemId
    current_state = $item.status
    target_state = $State
    note = $Note
    proposed_updated_utc = $updatedUtc
}

Write-Host ""
Write-Host "Would-be state update:"
$proposedUpdate | ConvertTo-Json -Depth 6 | Write-Host
Write-Host ""

if ($Apply) {
    Write-Host "Requested mutation: update worker task state"
    Write-Host "Mutation skipped: YES - this .DRY_RUN.ps1 script cannot change worker inbox state."
} else {
    Write-Host "Requested mutation: update worker task state"
    Write-Host "Mutation skipped: YES"
}

Write-Host "State updated: NO"
Write-Host "Files changed: NO"
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host "Next safe action: Request a separately approved APPLY worker state command if this state change should be persisted."
Write-Host "COPY END - Set-AiOsWorkerTaskState.DRY_RUN.ps1"

