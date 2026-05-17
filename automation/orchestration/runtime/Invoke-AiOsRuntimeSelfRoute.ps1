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
    $commandValidatorPath = "automation/orchestration/validators/Test-AiOsRecommendedCommand.ps1"

    if (-not (Test-Path -LiteralPath $commandValidatorPath)) {
        Write-Host "BLOCKED"
        exit 1
    }

    $validationOutput = @(powershell -ExecutionPolicy Bypass -File $commandValidatorPath $recommendation.recommended_command)
    $validationExitCode = $LASTEXITCODE
    $validationText = $validationOutput -join [Environment]::NewLine
    $validationResult = $null

    if (-not [string]::IsNullOrWhiteSpace($validationText)) {
        try {
            $validationResult = $validationText | ConvertFrom-Json
        }
        catch {
            $validationResult = $null
        }
    }

    foreach ($line in $validationOutput) {
        Write-Host $line
    }

    $validationStatus = @(
        if ($null -ne $validationResult) {
            $validationResult.status
            $validationResult.result
            $validationResult.overall_result
        }
    ) | Where-Object { -not [string]::IsNullOrWhiteSpace([string]$_) }

    $validationBlocked = @($validationStatus | Where-Object { $_ -in @("BLOCKED", "FAIL") }).Count -gt 0

    if ($validationExitCode -ne 0 -or $validationBlocked) {
        Write-Host "BLOCKED"
        exit 1
    }

    Write-Host "STEP - Executing recommended command"
    Invoke-Expression $recommendation.recommended_command
}

Write-Host ""
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
