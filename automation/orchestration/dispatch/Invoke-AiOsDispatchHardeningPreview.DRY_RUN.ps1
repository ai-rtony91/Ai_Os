param(
    [switch]$ValidateOnly
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Runner = Join-Path $ScriptDir "aios_dispatch_hardening_preview.py"

Write-Output "AI_OS_DISPATCH_HARDENING_PREVIEW"
Write-Output "LOCAL_FIXTURE_ONLY"
Write-Output "NO_LIVE_OPENAI_API_CALL"
Write-Output "NO_API_KEY_REQUIRED"
Write-Output "NO_NETWORK"
Write-Output "NO_RUNTIME_AUTONOMY"
Write-Output "NO_NIGHT_SUPERVISOR_RUNTIME_START"
Write-Output "NO_PROMPTFOO_EXECUTION"
Write-Output "NO_COMPUTER_USE_ACTIONS"
Write-Output "NO_SKILL_EXECUTION"
Write-Output "NO_BROKER_OANDA_LIVE_TRADING"
Write-Output "NO_PI_GPIO_MOTOR"

if ($ValidateOnly) {
    & python $Runner --validate-only
} else {
    & python $Runner
}

if ($LASTEXITCODE -ne 0) {
    throw "AI_OS dispatch hardening preview failed closed with exit code $LASTEXITCODE"
}

