param(
    [string]$WorkerId = "",
    [ValidateSet("all","open","complete","inbox","claimed","running","failed")]
    [string]$View = "open"
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

$inboxPath = "automation/orchestration/workers/inbox/AIOS_WORKER_INBOX.json"
$inbox = Get-Content -Raw $inboxPath | ConvertFrom-Json

$items = @($inbox.items)

if (-not [string]::IsNullOrWhiteSpace($WorkerId)) {
    $items = @($items | Where-Object { $_.worker_id -eq $WorkerId })
}

if ($View -eq "open") {
    $items = @($items | Where-Object { $_.status -ne "complete" -and $_.status -ne "failed" })
}
elseif ($View -ne "all") {
    $items = @($items | Where-Object { $_.status -eq $View })
}

Write-Host "COPY START - Get-AiOsWorkerInbox.DRY_RUN.ps1"
Write-Host "AI_OS Worker Inbox" -ForegroundColor Cyan
Write-Host "view: $View"
Write-Host "worker_id: $WorkerId"
Write-Host "items: $($items.Count)"

foreach ($item in $items) {
    Write-Host ""
    Write-Host "id: $($item.id)"
    Write-Host "worker_id: $($item.worker_id)"
    Write-Host "worker_type: $($item.worker_type)"
    Write-Host "status: $($item.status)"
    Write-Host "task: $($item.task)"
    Write-Host "reason: $($item.reason)"
    if ($item.PSObject.Properties.Name -contains "state_note") {
        Write-Host "state_note: $($item.state_note)"
    }
}

Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host "COPY END - Get-AiOsWorkerInbox.DRY_RUN.ps1"
