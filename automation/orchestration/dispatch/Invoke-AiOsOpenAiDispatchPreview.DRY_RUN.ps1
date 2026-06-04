param(
    [switch]$ValidateOnly
)

$ErrorActionPreference = "Stop"

Write-Output "AI_OS_OPENAI_DISPATCH_PREVIEW"
Write-Output "LOCAL_FIXTURE_ONLY"
Write-Output "NO_LIVE_OPENAI_API_CALL"
Write-Output "NO_API_KEY_REQUIRED"
Write-Output "NO_NETWORK"
Write-Output "NO_RUNTIME_AUTONOMY"
Write-Output "NO_NIGHT_SUPERVISOR_RUNTIME_START"
Write-Output "NO_BROKER_OANDA_LIVE_TRADING"
Write-Output "NO_PI_GPIO_MOTOR"

$scriptPath = Join-Path $PSScriptRoot "aios_openai_dispatch_preview.py"
$argsList = @($scriptPath)
if ($ValidateOnly) {
    $argsList += "--validate-only"
}

python @argsList
if ($LASTEXITCODE -ne 0) {
    throw "AI_OS OpenAI dispatch preview failed closed."
}
