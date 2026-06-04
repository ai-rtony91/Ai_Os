<#
.SYNOPSIS
Runs the AI_OS OpenAI planner fixture runner in local-only DRY_RUN mode.

.DESCRIPTION
This wrapper does not read secrets, read .env files, install packages, call the
network, or call OpenAI. It invokes a local Python fixture runner and fails
closed when the runner exits nonzero.
#>

[CmdletBinding()]
param(
    [switch]$ValidateOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = (Resolve-Path -LiteralPath (Join-Path $scriptRoot "..\..\..")).Path
$runnerPath = Join-Path $scriptRoot "openai_planner_fixture_runner.py"

Write-Host "LOCAL_FIXTURE_ONLY"
Write-Host "NO_LIVE_OPENAI_API_CALL"
Write-Host "NO_API_KEY_REQUIRED"
Write-Host "NO_ENV_READ"
Write-Host "NO_PACKAGE_INSTALL"
Write-Host "NO_NETWORK_CALL"
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
    if ($ValidateOnly) {
        & $python.Source $runnerPath --validate-only
    } else {
        & $python.Source $runnerPath
    }
    $exitCode = $LASTEXITCODE
    if ($exitCode -ne 0) {
        throw "Planner fixture runner failed with exit code $exitCode"
    }
}
finally {
    Pop-Location
}
