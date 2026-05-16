param(
    [Parameter(Mandatory = $true)][string]$Command,
    [string]$Reason = "",
    [switch]$Apply
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

$queuePath = "automation/orchestration/command_queue/AIOS_COMMAND_QUEUE.json"

if (-not (Test-Path $queuePath)) {
    @{ queue_id="AIOS_COMMAND_QUEUE"; version="1.0"; items=@() } | ConvertTo-Json -Depth 6 | Set-Content $queuePath -Encoding UTF8
}

$queue = Get-Content -Raw $queuePath | ConvertFrom-Json
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
Write-Host "Mode: $(if ($Apply) { 'APPLY' } else { 'DRY_RUN' })"
Write-Host "command: $Command"
Write-Host "reason: $Reason"

if ($Apply) {
    $queue.items = @($queue.items) + $item
    $queue | ConvertTo-Json -Depth 8 | Set-Content $queuePath -Encoding UTF8
    Write-Host "Queued: YES"
} else {
    Write-Host "Queued: NO"
}

Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host "COPY END - Add-AiOsCommandQueueItem.DRY_RUN.ps1"
