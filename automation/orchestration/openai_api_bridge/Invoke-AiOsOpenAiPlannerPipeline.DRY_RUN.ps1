<#
.SYNOPSIS
Runs the AI_OS OpenAI planner pipeline simulator in local-only DRY_RUN mode.

.DESCRIPTION
This wrapper does not read secrets, read .env files, install packages, call the
network, call OpenAI, or enable runtime autonomy.
#>

[CmdletBinding()]
param(
    [switch]$ValidateOnly,
    [string]$InputPath = "docs/AI_OS/openai_api_bridge/fixtures/PIPELINE_GOAL_INPUT_001.json",
    [string]$OutputDir = "docs/AI_OS/openai_api_bridge/pipeline_outputs"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = (Resolve-Path -LiteralPath (Join-Path $scriptRoot "..\..\..")).Path
$runnerPath = Join-Path $scriptRoot "aios_planner_pipeline_runner.py"

Write-Host "LOCAL_FIXTURE_ONLY"
Write-Host "NO_LIVE_OPENAI_API_CALL"
Write-Host "NO_API_KEY_REQUIRED"
Write-Host "NO_NETWORK"
Write-Host "NO_PACKAGE_INSTALL"
Write-Host "NO_RUNTIME_AUTONOMY"
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
    $args = @($runnerPath, "--input", $InputPath, "--output-dir", $OutputDir, "--dry-run")
    if ($ValidateOnly) {
        $args += "--validate-only"
    }
    & $python.Source @args
    $exitCode = $LASTEXITCODE
    if ($exitCode -ne 0) {
        throw "Planner pipeline runner failed with exit code $exitCode"
    }
}
finally {
    Pop-Location
}
