param(
    [switch]$LaunchSwarm,
    [switch]$RunWorkerPreview
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

Write-Host "AIOS SHORTCUT START" -ForegroundColor Cyan

$script = "automation/session/Start-AiOsDailyFlow.ps1"

if ($LaunchSwarm -and $RunWorkerPreview) {
    powershell -ExecutionPolicy Bypass -File $script -LaunchSwarm -RunWorkerPreview
}
elseif ($LaunchSwarm) {
    powershell -ExecutionPolicy Bypass -File $script -LaunchSwarm
}
elseif ($RunWorkerPreview) {
    powershell -ExecutionPolicy Bypass -File $script -RunWorkerPreview
}
else {
    powershell -ExecutionPolicy Bypass -File $script -RunWorkerPreview
}

Write-Host "AIOS SHORTCUT END" -ForegroundColor Green
