param(
    [switch]$Apply
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

Write-Host "AIOS Runtime Self Route"
Write-Host "Mode: $(if ($Apply) { 'APPLY' } else { 'DRY_RUN' })"
Write-Host ""

$recommendation = powershell -ExecutionPolicy Bypass -File automation/orchestration/recommendations/Get-AiOsActionRecommendation.DRY_RUN.ps1 -QuietJson | ConvertFrom-Json

Write-Host "Recommended command:"
Write-Host $recommendation.recommended_command
Write-Host ""

if ($Apply) {
    Write-Host "STEP - Executing recommended command"
    Invoke-Expression $recommendation.recommended_command
}

Write-Host ""
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
