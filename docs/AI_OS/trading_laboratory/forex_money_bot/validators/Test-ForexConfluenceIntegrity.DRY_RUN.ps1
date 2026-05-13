$ErrorActionPreference = "Stop"

$root = Resolve-Path (Join-Path $PSScriptRoot "..")
$enginePath = Join-Path $root "signals\FOREX_SIGNAL_CONFLUENCE_ENGINE_001.json"
$engine = Get-Content -LiteralPath $enginePath -Raw | ConvertFrom-Json

$requiredComponents = @(
  "EMA trend alignment",
  "RSI momentum confirmation",
  "Session alignment",
  "Trend strength",
  "Volatility alignment",
  "Risk condition"
)

$total = 0
foreach ($componentName in $requiredComponents) {
  $component = $engine.confidence_model.components | Where-Object { $_.name -eq $componentName }
  if (-not $component) {
    Write-Host "FAIL: Missing confidence component: $componentName"
    exit 1
  }
  if (-not ($component.points -is [int] -or $component.points -is [long] -or $component.points -is [double] -or $component.points -is [decimal])) {
    Write-Host "FAIL: Component points must be numeric: $componentName"
    exit 1
  }
  $total += $component.points
}

if ($total -ne 100) {
  Write-Host "FAIL: Confidence model must total 100 points. Actual: $total"
  exit 1
}

$signal = $engine.example_signal_output
$requiredFields = @(
  "signal_id",
  "pair",
  "timeframe",
  "direction",
  "confidence_score",
  "decision_state",
  "latency_seconds",
  "strategy_name",
  "session_name",
  "regime_tag",
  "risk_gate_status",
  "paper_only_status",
  "live_execution_status",
  "blocked_reason"
)

foreach ($field in $requiredFields) {
  if (-not ($signal.PSObject.Properties.Name -contains $field)) {
    Write-Host "FAIL: Missing signal output field: $field"
    exit 1
  }
}

if ($signal.confidence_score -lt 0 -or $signal.confidence_score -gt 100) {
  Write-Host "FAIL: confidence_score must be 0-100."
  exit 1
}

if ($signal.paper_only_status -ne "PAPER_ONLY") {
  Write-Host "FAIL: signal paper_only_status must be PAPER_ONLY."
  exit 1
}

if ($signal.live_execution_status -ne "BLOCKED") {
  Write-Host "FAIL: signal live_execution_status must remain BLOCKED."
  exit 1
}

Write-Host "PASS: Forex confluence integrity DRY_RUN validation passed."
Write-Host "Confluence scoring totals 100 and output remains paper-only."
