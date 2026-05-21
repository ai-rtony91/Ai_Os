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

$inboxExists = Test-Path -LiteralPath $inboxPath -PathType Leaf
if ($inboxExists) {
    $inbox = Get-Content -Raw -LiteralPath $inboxPath | ConvertFrom-Json
}
else {
    $inbox = [pscustomobject]@{
        inbox_id = "AIOS_WORKER_INBOX"
        version = "1.0"
        items = @()
    }
}

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
Write-Host "Mode: DRY_RUN"
Write-Host "worker_id: $WorkerId"
Write-Host "task: $Task"
Write-Host "reason: $Reason"
Write-Host "Inbox path: $inboxPath"
Write-Host "Inbox file exists: $inboxExists"
Write-Host "Current inbox item count: $(@($inbox.items).Count)"
Write-Host ""
Write-Host "Would-be inbox item:"
$item | ConvertTo-Json -Depth 6 | Write-Host
Write-Host ""

if ($Apply) {
    Write-Host "Requested mutation: add worker inbox item"
    Write-Host "Mutation skipped: YES - this .DRY_RUN.ps1 script cannot enqueue work or change worker inbox files."
} else {
    Write-Host "Requested mutation: add worker inbox item"
    Write-Host "Mutation skipped: YES"
}

Write-Host "Inbox item added: NO"
Write-Host "Files changed: NO"
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host "Next safe action: Request a separately approved APPLY worker inbox command if this item should be persisted."
Write-Host "COPY END - Add-AiOsWorkerInboxItem.DRY_RUN.ps1"
