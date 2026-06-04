[CmdletBinding()]
param(
    [switch]$ValidateOnly,
    [string]$OutputDir = "docs/AI_OS/improvement_loop/preview_outputs"
)

$ErrorActionPreference = "Stop"

Write-Host "LOCAL_FIXTURE_ONLY"
Write-Host "NO_OPENAI_CALL"
Write-Host "NO_API_KEY"
Write-Host "NO_NETWORK"
Write-Host "NO_RUNTIME_AUTONOMY"
Write-Host "NO_AUTO_MERGE"
Write-Host "NO_AUTO_PUSH"

$scriptPath = "automation/orchestration/improvement_loop/aios_improvement_loop_preview.py"
$argsList = @($scriptPath, "--output-dir", $OutputDir)
if ($ValidateOnly) {
    Write-Host "NO_WRITE_VALIDATION_MODE"
    $argsList += "--validate-only"
}

python @argsList
if ($LASTEXITCODE -ne 0) {
    throw "AI_OS improvement loop preview failed closed with exit code $LASTEXITCODE"
}
