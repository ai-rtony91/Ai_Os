<#
.SYNOPSIS
Runs the Phase 17 AI_OS execution pipeline preview in local-only DRY_RUN mode.
#>

[CmdletBinding()]
param(
    [switch]$ValidateOnly,
    [string]$GoalPath = "docs/AI_OS/execution_pipeline/fixtures/GOAL_INPUT_EXAMPLE_001.json",
    [string]$OutputDir = "docs/AI_OS/execution_pipeline/preview_outputs"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = (Resolve-Path -LiteralPath (Join-Path $scriptRoot "..\..\..")).Path
$runnerPath = Join-Path $scriptRoot "aios_execution_pipeline_preview.py"

Write-Host "AI_OS_PHASE_17_EXECUTION_PIPELINE_PREVIEW"
Write-Host "LOCAL_FIXTURE_ONLY"
Write-Host "NO_LIVE_OPENAI_API_CALL"
Write-Host "NO_API_KEY_REQUIRED"
Write-Host "NO_NETWORK"
Write-Host "NO_PACKAGE_INSTALL"
Write-Host "NO_RUNTIME_AUTONOMY"
Write-Host "NO_REAL_APPROVAL_WRITE"
Write-Host "NO_REAL_TELEMETRY_WRITE"
Write-Host "PAPER_ONLY_TRADING_SAFETY"
if ($ValidateOnly) {
    Write-Host "NO_WRITE_VALIDATION_MODE"
}

if (-not (Test-Path -LiteralPath $runnerPath -PathType Leaf)) {
    throw "Missing runner: $runnerPath"
}

$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    $python = Get-Command py -ErrorAction SilentlyContinue
}
if (-not $python) {
    throw "Python executable not found."
}

Push-Location $repoRoot
try {
    $args = @($runnerPath, "--goal", $GoalPath, "--output-dir", $OutputDir)
    if ($ValidateOnly) {
        $args += "--validate-only"
    }
    & $python.Source @args
    if ($LASTEXITCODE -ne 0) {
        throw "Execution pipeline preview failed with exit code $LASTEXITCODE"
    }
}
finally {
    Pop-Location
}
