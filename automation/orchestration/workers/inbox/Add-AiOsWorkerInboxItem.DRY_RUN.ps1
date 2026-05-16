param(
    [Parameter(Mandatory = $true)][string]$WorkerId,
    [Parameter(Mandatory = $true)][string]$Task,
    [string]$Reason = "",
    [switch]$Apply
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

$inboxPath = "automation/orchestration/workers/inbox/AIOS_WORKER_INBOX.json"
$registryPath = "automation/orchestration/workers/AIOS_WORKER_REGISTRY.json"

$registry = Get-Content -Raw $registryPath | ConvertFrom-Json
$worker = @($registry.workers | Where-Object { $_.worker_id -eq $WorkerId }) | Select-Object -First 1

if ($null -eq $worker) {
    throw "Worker not found: $WorkerId"
}

$inbox = Get-Content -Raw $inboxPath | ConvertFrom-Json
$utc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")

$item = [pscustomobject]@{
    id = $utc.Replace(":","").Replace("-","")
    worker_id = $WorkerId
    worker_type = $worker.type
    task = $Task
    reason = $Reason
    status = "inbox"
    created_utc = $utc
}

Write-Host "COPY START - Add-AiOsWorkerInboxItem.DRY_RUN.ps1"
Write-Host "AI_OS Worker Inbox Add" -ForegroundColor Cyan
Write-Host "Mode: $(if ($Apply) { 'APPLY' } else { 'DRY_RUN' })"
Write-Host "worker_id: $WorkerId"
Write-Host "task: $Task"

if ($Apply) {
    $inbox.items = @($inbox.items) + $item
    $inbox | ConvertTo-Json -Depth 8 | Set-Content $inboxPath -Encoding UTF8
    Write-Host "Inbox item added: YES"
} else {
    Write-Host "Inbox item added: NO"
}

Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host "COPY END - Add-AiOsWorkerInboxItem.DRY_RUN.ps1"
