param(
    [Parameter(Mandatory = $true)][string]$Goal,
    [switch]$Apply
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

Write-Host "AIOS Runtime Loop"
Write-Host "Mode: $(if ($Apply) { 'APPLY' } else { 'DRY_RUN' })"
Write-Host "Goal: $Goal"
Write-Host ""

Write-Host "STEP 1 - Intake"
powershell -ExecutionPolicy Bypass -File automation/intake/Invoke-AiOsGoalIntake.ps1 -Goal $Goal -Apply

Write-Host ""
Write-Host "STEP 2 - Recommendation"
powershell -ExecutionPolicy Bypass -File automation/orchestration/recommendations/Get-AiOsActionRecommendation.DRY_RUN.ps1

Write-Host ""
Write-Host "STEP 3 - Runtime health"
powershell -ExecutionPolicy Bypass -File automation/orchestration/health/Test-AiOsRuntimeHealth.DRY_RUN.ps1

Write-Host ""
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
