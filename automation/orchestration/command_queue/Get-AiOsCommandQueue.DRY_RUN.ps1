param(
    [switch]$QuietJson
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

$queuePath = "automation/orchestration/command_queue/AIOS_COMMAND_QUEUE.json"

if (-not (Test-Path $queuePath)) {
    throw "Queue missing: $queuePath"
}

$queue = Get-Content -Raw $queuePath | ConvertFrom-Json

if ($QuietJson) {
    $queue | ConvertTo-Json -Depth 8
    exit 0
}

Write-Host "COPY START - Get-AiOsCommandQueue.DRY_RUN.ps1"
Write-Host "AI_OS Command Queue" -ForegroundColor Cyan
Write-Host "items: $(@($queue.items).Count)"

foreach ($item in @($queue.items)) {
    Write-Host ""
    Write-Host "id: $($item.id)"
    Write-Host "status: $($item.status)"
    Write-Host "reason: $($item.reason)"
    Write-Host "command: $($item.command)"
}

Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host "COPY END - Get-AiOsCommandQueue.DRY_RUN.ps1"
