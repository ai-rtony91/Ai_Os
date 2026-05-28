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
    $gateRunnerPath = "automation/orchestration/gates/gate_runner.ps1"

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

    if (-not (Test-Path -LiteralPath $gateRunnerPath)) {
        Write-Host "BLOCKED"
        Write-Host "Gate runner missing: $gateRunnerPath"
        exit 1
    }

    $gateOutput = @(powershell -NoProfile -ExecutionPolicy Bypass -File $gateRunnerPath `
        -Mode APPLY `
        -CommandText ([string]$recommendation.recommended_command) `
        -WorkerId "RUNTIME_SELF_ROUTE" `
        -TaskId "Invoke-AiOsRuntimeSelfRoute" `
        -RepoRoot (Get-Location).Path)
    $gateExitCode = $LASTEXITCODE
    $gateText = $gateOutput -join [Environment]::NewLine
    $gateDecision = $null

    if ($gateExitCode -eq 0 -and -not [string]::IsNullOrWhiteSpace($gateText)) {
        try {
            $gateDecision = $gateText | ConvertFrom-Json
        }
        catch {
            $gateDecision = $null
        }
    }

    if ($null -eq $gateDecision) {
        Write-Host "BLOCKED"
        Write-Host "Gate runner failed or returned invalid JSON."
        exit 1
    }

    Write-Host "Gate decision: $($gateDecision.decision)"
    Write-Host "Gate tier: $($gateDecision.tier)"
    if ($gateDecision.decision -ne "AUTO_PROCEED") {
        Write-Host "BLOCKED"
        Write-Host "Gate blocked execution: $($gateDecision.blocked_reason)"
        exit 1
    }

    Write-Host "STEP - Executing recommended command"
    Invoke-Expression $recommendation.recommended_command
}

Write-Host ""
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
