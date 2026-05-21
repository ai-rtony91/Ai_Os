param(
    [Parameter(Mandatory = $true)][string]$Command,
    [string]$Reason = "",
    [switch]$Apply
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

$queuePath = "automation/orchestration/command_queue/AIOS_COMMAND_QUEUE.json"

$queueExists = Test-Path -LiteralPath $queuePath -PathType Leaf
if ($queueExists) {
    $queue = Get-Content -Raw -LiteralPath $queuePath | ConvertFrom-Json
}
else {
    $queue = [pscustomobject]@{
        queue_id = "AIOS_COMMAND_QUEUE"
        version = "1.0"
        items = @()
    }
}
$utc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")

$item = [pscustomobject]@{
    id = $utc.Replace(":","").Replace("-","")
    command = $Command
    reason = $Reason
    status = "queued"
    created_utc = $utc
}

Write-Host "COPY START - Add-AiOsCommandQueueItem.DRY_RUN.ps1"
Write-Host "AI_OS Command Queue Add" -ForegroundColor Cyan
Write-Host "Mode: DRY_RUN"
Write-Host "command: $Command"
Write-Host "reason: $Reason"
Write-Host "Queue path: $queuePath"
Write-Host "Queue file exists: $queueExists"
Write-Host "Current queue item count: $(@($queue.items).Count)"
Write-Host ""
Write-Host "Would-be queue entry:"
$item | ConvertTo-Json -Depth 6 | Write-Host
Write-Host ""

if ($Apply) {
    Write-Host "Requested mutation: enqueue command item"
    Write-Host "Mutation skipped: YES - this .DRY_RUN.ps1 script cannot enqueue work or change queue files."
} else {
    Write-Host "Requested mutation: enqueue command item"
    Write-Host "Mutation skipped: YES"
}

Write-Host "Queued: NO"
Write-Host "Files changed: NO"
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host "Next safe action: Request a separately approved APPLY queue command if this item should be persisted."
Write-Host "COPY END - Add-AiOsCommandQueueItem.DRY_RUN.ps1"
