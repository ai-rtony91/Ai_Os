[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

Write-Host "AI_OS readiness check"
Write-Host ""

git status --short --branch

Write-Host ""
Write-Host "Running preflight..."
powershell -ExecutionPolicy Bypass -File automation\orchestration\Run-AiOsPreflight.DRY_RUN.ps1

Write-Host ""
Write-Host "Ready check complete."