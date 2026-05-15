param(
    [string]$WorkerId = "WORKER-1"
)

$CardPath = ".\automation\orchestration\task_cards\$WorkerId-TASK.md"

if (!(Test-Path $CardPath)) {
    Write-Host "Task card not found for $WorkerId" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host " AI_OS WORKER TASK CARD" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

Get-Content $CardPath
