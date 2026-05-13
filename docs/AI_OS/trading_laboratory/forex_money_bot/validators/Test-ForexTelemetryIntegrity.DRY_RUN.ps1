$ErrorActionPreference = "Stop"

$root = Resolve-Path (Join-Path $PSScriptRoot "..")
$telemetryFiles = Get-ChildItem -Path (Join-Path $root "telemetry") -Filter "*.json"
$requiredTelemetryFields = @(
  "signal_received_timestamp",
  "decision_timestamp",
  "execution_timestamp",
  "close_timestamp",
  "latency_seconds",
  "trade_duration_minutes",
  "confidence_score",
  "spread_placeholder",
  "slippage_placeholder",
  "session_name",
  "market_regime",
  "paper_only_status"
)
$requiredMetricFields = @(
  "simulated_rr",
  "simulated_profit_pips",
  "simulated_loss_pips",
  "win_streak",
  "loss_streak",
  "daily_expectancy",
  "pair_performance_score"
)

foreach ($file in $telemetryFiles) {
  $json = Get-Content -LiteralPath $file.FullName -Raw | ConvertFrom-Json
  if ($json.live_execution_status -ne "BLOCKED") {
    Write-Host "FAIL: live_execution_status must remain BLOCKED: $($file.FullName)"
    exit 1
  }
  if ($json.paper_only_status -ne "PAPER_ONLY") {
    Write-Host "FAIL: paper_only_status must be PAPER_ONLY: $($file.FullName)"
    exit 1
  }
  $payload = $json.telemetry
  if (-not $payload) { $payload = $json.latency_audit }
  if (-not $payload) { $payload = $json.signal_health }
  if (-not $payload) {
    Write-Host "FAIL: Telemetry payload missing: $($file.FullName)"
    exit 1
  }
  foreach ($field in $requiredTelemetryFields) {
    if (-not ($payload.PSObject.Properties.Name -contains $field)) {
      Write-Host "FAIL: Missing telemetry field $field in $($file.FullName)"
      exit 1
    }
  }
}

$mainTelemetry = Get-Content -LiteralPath (Join-Path $root "telemetry\FOREX_BOT_TELEMETRY_001.json") -Raw | ConvertFrom-Json
foreach ($field in $requiredMetricFields) {
  if (-not ($mainTelemetry.telemetry.PSObject.Properties.Name -contains $field)) {
    Write-Host "FAIL: Missing simulated metric field: $field"
    exit 1
  }
}

Write-Host "PASS: Forex telemetry integrity DRY_RUN validation passed."
Write-Host "Telemetry fields and simulated metrics confirmed paper-only."
