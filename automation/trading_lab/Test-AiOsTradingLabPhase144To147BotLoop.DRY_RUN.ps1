Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$validators = @(
    "Test-AiOsTradingLabPhase144SuperTrendPreview.DRY_RUN.ps1",
    "Test-AiOsTradingLabPhase145TradingViewPayloadMock.DRY_RUN.ps1",
    "Test-AiOsTradingLabPhase146TradersPostRoutePreview.DRY_RUN.ps1",
    "Test-AiOsTradingLabPhase147PaperTradeOutcomeLoop.DRY_RUN.ps1"
)

foreach ($validator in $validators) {
    $path = Join-Path $PSScriptRoot $validator
    if (-not (Test-Path -LiteralPath $path)) {
        throw "Missing validator: $validator"
    }
    Write-Output "Running $validator"
    powershell -ExecutionPolicy Bypass -File $path
    if ($LASTEXITCODE -ne 0) {
        throw "Validator failed: $validator"
    }
}

Write-Output "PASS: Phase 14.4 through Phase 14.7 minimum DRY_RUN bot loop validation passed."
Write-Output "Minimum paper/mock loop complete: TradingView-style payload -> SuperTrend permission -> Phase 14.3 decision reference -> TradersPost-style route preview -> paper outcome."
Write-Output "Live execution remains BLOCKED."
