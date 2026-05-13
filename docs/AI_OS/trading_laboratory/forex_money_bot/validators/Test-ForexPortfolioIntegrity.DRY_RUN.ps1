$ErrorActionPreference = "Stop"

$root = Resolve-Path (Join-Path $PSScriptRoot "..")
$requiredExposureStates = @("SAFE", "WATCH", "HIGH_EXPOSURE", "LOCKDOWN")
$requiredMetrics = @("portfolio_confidence_score", "pair_priority_score", "volatility_weight", "drawdown_pressure", "exposure_score", "correlation_risk", "queue_rank", "paper_only_status")

$exposurePath = Join-Path $root "exposure\FOREX_PAIR_CORRELATION_MATRIX_001.json"
$exposure = Get-Content -LiteralPath $exposurePath -Raw | ConvertFrom-Json
foreach ($state in $requiredExposureStates) {
  if ($exposure.exposure_states -notcontains $state) {
    Write-Host "FAIL: Missing exposure state: $state"
    exit 1
  }
}

$metricFiles = @(
  (Join-Path $root "portfolio\FOREX_PORTFOLIO_STATE_001.json"),
  (Join-Path $root "ranking\FOREX_OPPORTUNITY_RANKING_ENGINE_001.json"),
  (Join-Path $root "exposure\FOREX_DRAWDOWN_PRESSURE_MODEL_001.json")
)

foreach ($file in $metricFiles) {
  $json = Get-Content -LiteralPath $file -Raw | ConvertFrom-Json
  $payload = $json.portfolio_state
  if (-not $payload) { $payload = $json.example_ranked_opportunity }
  if (-not $payload) { $payload = $json.drawdown_model }
  foreach ($metric in $requiredMetrics) {
    if (-not ($payload.PSObject.Properties.Name -contains $metric)) {
      Write-Host "FAIL: Missing metric $metric in $file"
      exit 1
    }
  }
}

$jsonFiles = Get-ChildItem -Path $root -Recurse -Filter "*.json"
foreach ($file in $jsonFiles) {
  $json = Get-Content -LiteralPath $file.FullName -Raw | ConvertFrom-Json
  if ($json.live_execution_status -ne "BLOCKED") {
    Write-Host "FAIL: live_execution_status must remain BLOCKED: $($file.FullName)"
    exit 1
  }
  if (($json.PSObject.Properties.Name -contains "broker_api_status") -and $json.broker_api_status -ne "BLOCKED") {
    Write-Host "FAIL: broker_api_status must remain BLOCKED: $($file.FullName)"
    exit 1
  }
  if (($json.PSObject.Properties.Name -contains "webhook_status") -and $json.webhook_status -ne "BLOCKED") {
    Write-Host "FAIL: webhook_status must remain BLOCKED: $($file.FullName)"
    exit 1
  }
}

Write-Host "PASS: Forex portfolio integrity DRY_RUN validation passed."
Write-Host "Exposure states, metrics, and blocked execution confirmed."
