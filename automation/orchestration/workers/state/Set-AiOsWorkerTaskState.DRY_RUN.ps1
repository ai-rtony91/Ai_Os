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
Write-Host "Mode: $(if ($Apply) { 'APPLY' } else { 'DRY_RUN' })"
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

if ($Apply) {
    foreach ($entry in $items) {
        if ($entry.id -eq $ItemId) {
            $entry.status = $State
            if ($entry.PSObject.Properties.Name -notcontains "state_note") {
    $entry | Add-Member -NotePropertyName state_note -NotePropertyValue ""
}
$entry.state_note = $Note
            if ($entry.PSObject.Properties.Name -notcontains "updated_utc") {
    $entry | Add-Member -NotePropertyName updated_utc -NotePropertyValue ""
}
$entry.updated_utc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
        }
    }

    $inbox.items = $items
    $inbox | ConvertTo-Json -Depth 10 | Set-Content $inboxPath -Encoding UTF8

    Write-Host "State updated: YES" -ForegroundColor Green
} else {
    Write-Host "State updated: NO"
}

Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host "COPY END - Set-AiOsWorkerTaskState.DRY_RUN.ps1"

